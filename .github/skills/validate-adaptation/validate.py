#!/usr/bin/env python3
"""Architecture-aware validator for the Stingray industry-adapter skill pack.

Target app: Django 5.2 + server-rendered Tailwind templates. The backend models
live in ``apps/core/models.py`` (Django ORM); the display surfaces are Django
templates under ``templates/``; the domain manifest is a Python dict in
``apps/core/domain.py`` injected into every template by a context processor. All
checks are READ-ONLY.

The validator is safe to run on the unadapted (healthcare) baseline: every check
that depends on a generated adaptation (a domain manifest, a generated seed
command, or vertical calculators) reports ``skip`` when that adaptation is absent,
and only enforces the stable contract once it is present.

Usage (from the repo root)::

    python .github/skills/validate-adaptation/validate.py
    python .github/skills/validate-adaptation/validate.py --check ui_contract
    python .github/skills/validate-adaptation/validate.py --self-test

Exit code is non-zero if any non-skipped check fails.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_NAME = "validate-adaptation"

# ---------------------------------------------------------------------------
# Frozen contract — the stable keys an adaptation MUST NOT rename. Display copy
# and data VALUES are free to change; these structural keys are the binding
# surface every layer depends on.
# ---------------------------------------------------------------------------

# Django model -> required fields (an adaptation may add fields, never drop or
# rename these). These mirror the six tables in apps/core/models.py.
MODEL_FIELDS: dict[str, set[str]] = {
    "PatientProfile": {
        "user",
        "date_of_birth",
        "phone_number",
        "address",
        "insurance_provider",
        "insurance_policy_number",
        "created_at",
        "updated_at",
    },
    "LabTest": {
        "patient",
        "test_name",
        "test_category",
        "ordered_by",
        "order_date",
        "result_date",
        "status",
        "result_value",
        "reference_range",
        "unit",
        "is_abnormal",
        "notes",
        "created_at",
    },
    "DoctorVisit": {
        "patient",
        "doctor_name",
        "specialty",
        "visit_date",
        "visit_type",
        "reason",
        "diagnosis",
        "treatment_plan",
        "follow_up_date",
        "vitals_bp",
        "vitals_heart_rate",
        "vitals_temperature",
        "vitals_weight",
        "notes",
        "created_at",
    },
    "Invoice": {
        "invoice_number",
        "patient",
        "issue_date",
        "due_date",
        "status",
        "subtotal",
        "tax",
        "total",
        "notes",
        "created_by",
        "created_at",
        "updated_at",
    },
    "InvoiceLineItem": {
        "invoice",
        "description",
        "quantity",
        "unit_price",
        "total_price",
        "service_date",
        "provider_name",
    },
}

# The patient_dashboard view (apps/core/views.py) builds these context keys and
# the templates bind to them. This is the Django equivalent of katas2's
# DashboardStats response contract.
DASHBOARD_CONTEXT_KEYS = {
    "total_labs",
    "pending_labs",
    "abnormal_labs",
    "total_visits",
    "recent_labs",
    "recent_visits",
    "upcoming_followups",
}

# doctor_visits.visit_type is a closed enum that drives filter chips and badge
# colors. Display labels may be re-skinned per vertical, but the stored CODES
# must stay within this set.
VISIT_TYPE_CODES = {"checkup", "follow_up", "urgent", "specialist", "preventive"}

# Portal URL names defined in apps/core/urls.py. A manifest nav target must
# resolve to one of these (templates reference them via {% url '<name>' %}).
PORTAL_URL_NAMES = {"patient_dashboard", "lab_tests", "doctor_visits", "invoice_list"}

# Baseline healthcare display strings. Once a template reads the domain manifest
# (via the injected ``domain`` context), these literals must not remain
# hardcoded in it (that is display / binding drift — a half-finished re-skin).
WIRED_BASELINE_STRINGS: dict[str, list[str]] = {
    "templates/portal_base.html": ["Health Portal", "Health Records", "Nurse AI"],
    "templates/base.html": ["Health Portal"],
    "templates/core/dashboard.html": [
        "Total Lab Tests",
        "Recent Lab Tests",
        "Recent Doctor Visits",
    ],
    "templates/core/lab_tests.html": ["Lab Tests", "Test Name", "Ordered By"],
    "templates/core/doctor_visits.html": [
        "Doctor Visits",
        "Visit Type:",
        "Urgent Care",
    ],
    "templates/core/invoices_list.html": ["Patient Billing Dashboard"],
}

# Templates that render a DoctorVisit.visit_type to the user. Once a manifest is
# present, these must route the code through the manifest's ``visit_type_labels``
# (via the ``domain_extras`` dict_get filter) rather than ``get_visit_type_display``
# -- otherwise the model's healthcare choice LABELS (e.g. "Annual Checkup") leak
# into the re-skinned vertical even though the codes are correct. This is display
# vs binding drift that the literal banned-strings scan above cannot catch.
VISIT_TYPE_DISPLAY_TEMPLATES = [
    "templates/core/dashboard.html",
    "templates/core/doctor_visits.html",
]
DOMAIN_EXTRAS = "apps/core/templatetags/domain_extras.py"

# The visit-detail page renders three free-text DoctorVisit fields under fixed
# heading labels. The healthcare baseline labels (Reason for Visit / Diagnosis /
# Treatment Plan) are clinical and leak into a re-skinned vertical unless they are
# bound to the manifest. doctor_visits.html must read each from
# ``domain.entities.visit.<key>`` (with a healthcare default), and an active
# manifest must define all three so the displayed copy matches the industry.
VISIT_DETAIL_LABEL_KEYS = ["reason_label", "diagnosis_label", "plan_label"]
VISIT_DETAIL_TEMPLATE = "templates/core/doctor_visits.html"

# Public (unauthenticated) pages. The landing page (home.html) and post-signup
# welcome page (welcome.html) carry heavy healthcare copy -- the hero ("Your
# Health Records"), the decorative preview cards ("Complete Blood Count",
# "Dr. Williams - Cardiology", "Lipid Panel"), the stats ("Patients Served") and
# the welcome quick-links. These are the "front door" and are NOT covered by the
# portal-chrome scan, so they must read from a manifest ``home`` block (each value
# defaulted to its healthcare original). Once a manifest exists it must define a
# ``home`` block and both public templates must bind to ``domain.home.``.
PUBLIC_TEMPLATES = [
    "templates/core/home.html",
    "templates/core/welcome.html",
]

DOMAIN_MODULE = "apps/core/domain.py"
CONTEXT_PROCESSOR = "apps/core/context_processors.py"
SETTINGS = "StingrayHealthPortal/settings.py"
MODELS = "apps/core/models.py"
VIEWS = "apps/core/views.py"
URLS = "apps/core/urls.py"

# Per-industry accent theming. The accent palette is a Tailwind v4 @theme color
# scale (--color-accent-* / --color-accent2-*) registered in static/input.css;
# an adaptation overrides those CSS variables at runtime from the manifest's
# ``theme`` block via an inline <style> partial included in both root layouts.
# NOTE (Tailwind v4 gotcha): the JS config's ``theme.extend.colors`` is IGNORED
# by v4 — the scale MUST be declared with @theme in input.css for the utilities
# to exist and reference the overridable var. See adapt-for-industry
# references/GENERATION_GUIDE.md ("Per-industry accent theming").
INPUT_CSS = "static/input.css"
THEME_PARTIAL = "templates/partials/_theme_style.html"
# Templates whose accent surfaces are themed: they must use the accent/accent2
# scale, never a hardcoded teal-*/cyan-* brand class, once a manifest is present.
THEMED_TEMPLATES = [
    "templates/base.html",
    "templates/portal_base.html",
    "templates/core/dashboard.html",
    "templates/core/doctor_visits.html",
    "templates/core/lab_tests.html",
    "templates/core/home.html",
    "templates/core/welcome.html",
    "templates/account/login.html",
    "templates/account/signup.html",
    "templates/account/logout.html",
]
# Root layouts that must inject the per-industry accent override.
THEME_HOST_LAYOUTS = ["templates/base.html", "templates/portal_base.html"]


@dataclass
class Result:
    name: str
    passed: bool
    details: str
    remediation: str = ""
    skipped: bool = False

    def as_json(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "status": "skipped"
                if self.skipped
                else "pass"
                if self.passed
                else "fail",
                "passed": self.passed,
                "skipped": self.skipped,
                "details": self.details,
                "remediation": self.remediation,
            }
        )


def _path(rel: str) -> Path:
    return REPO_ROOT / rel


def _exists(rel: str) -> bool:
    return _path(rel).exists()


def _read(rel: str) -> str:
    return _path(rel).read_text(encoding="utf-8")


def _ok(name: str, details: str) -> Result:
    return Result(name, True, details)


def _fail(name: str, details: str, remediation: str) -> Result:
    return Result(name, False, details, remediation)


def _skip(name: str, details: str) -> Result:
    return Result(name, True, details, skipped=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _model_fields(source: str) -> dict[str, set[str]]:
    """Map Django model class name -> assigned field names.

    Django fields are class-level assignments of the form ``name = models.X(...)``
    so we collect ``ast.Assign`` targets whose value is a ``models.*`` call.
    """
    tree = ast.parse(source)
    classes: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        fields: set[str] = set()
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                func = stmt.value.func
                is_model_field = (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "models"
                )
                if is_model_field:
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            fields.add(target.id)
        if fields:
            classes[node.name] = fields
    return classes


def _dict_keys_in_context(source: str, marker: str) -> set[str]:
    """Collect string keys assigned in a ``context = {...}`` dict near a marker
    function. Used to read the patient_dashboard context keys."""
    keys: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == marker:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Dict):
                    for key in sub.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            keys.add(key.value)
    return keys


def _quoted_strings(source: str) -> list[str]:
    return re.findall(r"""["'`]([^"'`]*)["'`]""", source)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_environment() -> Result:
    if sys.version_info < (3, 10):  # noqa: UP036 - validator is portable, may run on older interpreters
        return _fail(
            "environment",
            f"python={sys.version.split()[0]}",
            "Use Python 3.10+ to run the validator.",
        )
    required = [
        MODELS,
        VIEWS,
        URLS,
        SETTINGS,
        "apps/core/management/commands/seed_dummy_data.py",
        "templates/portal_base.html",
        "templates/base.html",
        "manage.py",
        "package.json",
    ]
    missing = [p for p in required if not _exists(p)]
    if missing:
        return _fail(
            "environment",
            f"missing {missing}",
            "Run from the repo root and restore the listed baseline files.",
        )
    return _ok(
        "environment",
        f"python={sys.version.split()[0]}, Django+templates baseline present",
    )


def check_backend_compile() -> Result:
    failures: list[str] = []
    roots = [_path("apps"), _path("StingrayHealthPortal")]
    files = sorted(p for root in roots for p in root.rglob("*.py"))
    for path in files:
        if "__pycache__" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)}:{exc.lineno} {exc.msg}")
    if failures:
        return _fail(
            "backend_compile",
            "; ".join(failures),
            "Fix the Python syntax errors before deploying the adaptation.",
        )
    return _ok("backend_compile", "all apps/ and project Python modules parse")


def check_schema_integrity() -> Result:
    classes = _model_fields(_read(MODELS))
    problems: list[str] = []
    for model, required in MODEL_FIELDS.items():
        actual = classes.get(model)
        if actual is None:
            problems.append(f"{model} class missing")
            continue
        dropped = required - actual
        if dropped:
            problems.append(f"{model} dropped/renamed {sorted(dropped)}")
    if problems:
        return _fail(
            "schema_integrity",
            "; ".join(problems),
            "Adaptations must reuse the existing models/fields. Re-skin display copy and swap data VALUES, but keep model field names stable (or migrate every consumer and document the reason).",
        )
    return _ok(
        "schema_integrity", f"{len(MODEL_FIELDS)} models retain their contract fields"
    )


def check_api_contract() -> Result:
    """The Django equivalent of katas2's api_contract: the patient_dashboard view
    must still build every dashboard context key the templates bind to."""
    keys = _dict_keys_in_context(_read(VIEWS), "patient_dashboard")
    missing = DASHBOARD_CONTEXT_KEYS - keys
    if missing:
        return _fail(
            "api_contract",
            f"patient_dashboard context missing {sorted(missing)}",
            "Keep the dashboard context keys stable; they bind apps/core/views.py to templates/core/dashboard.html.",
        )
    return _ok("api_contract", "patient_dashboard builds all dashboard context keys")


def check_visit_type_enum() -> Result:
    src = _read(MODELS)
    match = re.search(r"VISIT_TYPE_CHOICES\s*=\s*\[(?P<body>.*?)\]", src, re.DOTALL)
    if not match:
        return _skip("visit_type_enum", "VISIT_TYPE_CHOICES not found in models.py")
    codes = set(re.findall(r"\(\s*[\"']([a-z_]+)[\"']\s*,", match.group("body")))
    extra = codes - VISIT_TYPE_CODES
    if extra:
        return _fail(
            "visit_type_enum",
            f"unexpected visit_type codes {sorted(extra)}",
            f"visit_type is a closed enum {sorted(VISIT_TYPE_CODES)}. Re-skin the human labels (the second tuple element) per vertical, but keep these codes; seed data must use them too.",
        )
    if codes != VISIT_TYPE_CODES:
        return _fail(
            "visit_type_enum",
            f"visit_type codes changed to {sorted(codes)}",
            f"Keep all five codes {sorted(VISIT_TYPE_CODES)}; only the display labels may be re-skinned.",
        )
    return _ok(
        "visit_type_enum",
        f"visit_type retains the {len(VISIT_TYPE_CODES)} stable codes",
    )


def check_domain_manifest() -> Result:
    has_domain = _exists(DOMAIN_MODULE)
    has_processor = _exists(CONTEXT_PROCESSOR)
    if not has_domain and not has_processor:
        return _skip(
            "domain_manifest",
            "no domain manifest present; app is on the unadapted healthcare baseline (run adapt-for-industry to generate one)",
        )
    problems: list[str] = []
    if not has_domain:
        problems.append(f"{CONTEXT_PROCESSOR} exists but {DOMAIN_MODULE} is missing")
    else:
        dsrc = _read(DOMAIN_MODULE)
        if "DOMAIN" not in dsrc:
            problems.append(f"{DOMAIN_MODULE} does not define a DOMAIN manifest")
        # nav targets reference portal URL names; flag any unknown {% url %} name.
        nav_names = set(
            re.findall(r"['\"]url_name['\"]\s*:\s*['\"]([a-z_]+)['\"]", dsrc)
        )
        unresolved = sorted(nav_names - PORTAL_URL_NAMES)
        if unresolved:
            problems.append(f"manifest nav url_name(s) not in urls.py: {unresolved}")
    if not has_processor:
        problems.append(f"{DOMAIN_MODULE} exists but {CONTEXT_PROCESSOR} is missing")
    else:
        psrc = _read(CONTEXT_PROCESSOR)
        if "domain" not in psrc:
            problems.append("context processor does not return a `domain` key")
        settings_src = _read(SETTINGS)
        if (
            "context_processors.domain" not in settings_src
            and "core.context_processors" not in settings_src
        ):
            problems.append("context processor not registered in settings.py TEMPLATES")
    if problems:
        return _fail(
            "domain_manifest",
            "; ".join(problems),
            "Wire the generated manifest end to end: define DOMAIN, return it from a context processor, register that processor in settings.py, and point nav at real {% url %} names.",
        )
    return _ok(
        "domain_manifest",
        "domain manifest is present and wired (DOMAIN + context processor + settings registration)",
    )


def check_ui_contract() -> Result:
    if not _exists(DOMAIN_MODULE):
        return _skip(
            "ui_contract",
            "no domain manifest yet; baseline display copy is the original healthcare app (nothing to drift-check)",
        )
    drift: list[str] = []
    for rel, banned in WIRED_BASELINE_STRINGS.items():
        if not _exists(rel):
            continue
        src = _read(rel)
        reads_manifest = "domain." in src
        if not reads_manifest:
            drift.append(f"{rel} does not read the domain manifest (still hardcoded)")
            continue
        leftover = [s for s in banned if s in src]
        if leftover:
            drift.append(
                f"{rel} still hardcodes {leftover} despite reading the manifest"
            )
    # visit_type label drift: re-skinned templates must render visit_type through
    # the manifest's visit_type_labels (domain_extras dict_get), not the model's
    # get_visit_type_display (which still yields the healthcare choice labels).
    for rel in VISIT_TYPE_DISPLAY_TEMPLATES:
        if not _exists(rel):
            continue
        if "get_visit_type_display" in _read(rel):
            drift.append(
                f"{rel} renders visit_type via get_visit_type_display (model "
                f"healthcare labels) instead of domain.visit_type_labels"
            )
    # Visit-detail field labels: doctor_visits.html must bind each detail heading
    # to the manifest (domain.entities.visit.<key>), and the active manifest must
    # define all three -- otherwise the clinical baseline headings (Diagnosis /
    # Treatment Plan / Reason for Visit) leak into the re-skinned vertical.
    if _exists(VISIT_DETAIL_TEMPLATE):
        vsrc = _read(VISIT_DETAIL_TEMPLATE)
        missing_binds = [
            k
            for k in VISIT_DETAIL_LABEL_KEYS
            if f"domain.entities.visit.{k}" not in vsrc
        ]
        if missing_binds:
            drift.append(
                f"{VISIT_DETAIL_TEMPLATE} hardcodes visit-detail label(s); not bound "
                f"to manifest key(s) {missing_binds} (domain.entities.visit.*)"
            )
    if _exists(DOMAIN_MODULE):
        dsrc = _read(DOMAIN_MODULE)
        missing_keys = [k for k in VISIT_DETAIL_LABEL_KEYS if k not in dsrc]
        if missing_keys:
            drift.append(
                f"{DOMAIN_MODULE} entities.visit is missing detail-label key(s) "
                f"{missing_keys}; clinical baseline labels would leak into the vertical"
            )
    # Public pages: home.html / welcome.html must bind to a manifest ``home`` block
    # (each value defaulted to its healthcare original), and the active manifest
    # must define that block -- otherwise the landing/welcome copy ("Your Health
    # Records", "Complete Blood Count", "Patients Served", ...) leaks on the front
    # door even though the authenticated portal is fully re-skinned.
    for rel in PUBLIC_TEMPLATES:
        if _exists(rel) and "domain.home." not in _read(rel):
            drift.append(
                f"{rel} does not bind to the manifest's home block "
                f"(domain.home.*); public healthcare copy would leak"
            )
    if _exists(DOMAIN_MODULE) and '"home"' not in _read(DOMAIN_MODULE):
        drift.append(
            f"{DOMAIN_MODULE} is missing a 'home' block; the public landing/welcome "
            f"pages would fall back to healthcare copy"
        )
    if drift:
        return _fail(
            "ui_contract",
            "; ".join(drift),
            "Every re-skinned template must read its labels from the injected `domain` context (apps/core/domain.py). Replace leftover hardcoded healthcare strings with {{ domain.* }} fields, and render visit_type through {{ domain.visit_type_labels|dict_get:visit.visit_type }} (the generated apps/core/templatetags/domain_extras.py filter) so display copy and data bindings cannot drift apart.",
        )
    return _ok(
        "ui_contract",
        "wired templates read the manifest and contain no leftover baseline display strings",
    )


def check_theme_contract() -> Result:
    if not _exists(DOMAIN_MODULE):
        return _skip(
            "theme_contract",
            "no domain manifest yet; baseline keeps the healthcare teal accent (nothing to theme-check)",
        )
    problems: list[str] = []

    # 1. The manifest must carry a theme block (accent + accent2 scales + avatar_bg).
    dsrc = _read(DOMAIN_MODULE)
    if '"theme"' not in dsrc and "'theme'" not in dsrc:
        problems.append(f"{DOMAIN_MODULE} has no `theme` block (accent palette)")
    else:
        for key in ("accent", "accent2", "avatar_bg"):
            if f'"{key}"' not in dsrc and f"'{key}'" not in dsrc:
                problems.append(f"{DOMAIN_MODULE} theme is missing `{key}`")

    # 2. input.css must register the accent scale via Tailwind v4 @theme (the JS
    #    config theme.extend.colors is ignored by v4, so this is mandatory).
    if not _exists(INPUT_CSS):
        problems.append(f"{INPUT_CSS} not found")
    else:
        css = _read(INPUT_CSS)
        if (
            "@theme" not in css
            or "--color-accent-600" not in css
            or "--color-accent2-600" not in css
        ):
            problems.append(
                f"{INPUT_CSS} does not register the accent scale via @theme "
                "(--color-accent-* / --color-accent2-*)"
            )

    # 3. The override partial must exist and override the same theme vars.
    if not _exists(THEME_PARTIAL):
        problems.append(f"{THEME_PARTIAL} (per-industry accent override) is missing")
    else:
        partial = _read(THEME_PARTIAL)
        if "--color-accent-600" not in partial or "domain.theme" not in partial:
            problems.append(
                f"{THEME_PARTIAL} must override --color-accent-* from domain.theme"
            )

    # 4. Both root layouts must include the override partial.
    for rel in THEME_HOST_LAYOUTS:
        if _exists(rel) and "partials/_theme_style.html" not in _read(rel):
            problems.append(f"{rel} does not include partials/_theme_style.html")

    # 5. No themed template may keep a hardcoded teal-*/cyan-* brand class; the
    #    accent must flow through the accent/accent2 scale so the manifest re-skins
    #    it. (Semantic status colors red/amber/green/purple/slate are untouched.)
    for rel in THEMED_TEMPLATES:
        if not _exists(rel):
            continue
        src = _read(rel)
        leftovers = sorted({m for m in re.findall(r"\b(?:teal|cyan)-\d{2,3}", src)})
        if leftovers:
            problems.append(f"{rel} still hardcodes brand color class(es) {leftovers}")

    if problems:
        return _fail(
            "theme_contract",
            "; ".join(problems),
            "Wire per-industry accent theming: add a `theme` block (accent/accent2 hex "
            "scales + avatar_bg) to apps/core/domain.py; register the accent scale with "
            "@theme in static/input.css; generate templates/partials/_theme_style.html to "
            "override --color-accent-* from domain.theme and include it in base.html + "
            "portal_base.html; and replace every teal-*/cyan-* brand class with the "
            "accent-*/accent2-* scale. See adapt-for-industry GENERATION_GUIDE.md "
            "(Per-industry accent theming). NOTE: Tailwind v4 ignores theme.extend.colors "
            "in tailwind.config.js — the @theme declaration in input.css is required.",
        )
    return _ok(
        "theme_contract",
        "per-industry accent theming wired (domain.theme + @theme scale + override partial; no hardcoded teal/cyan brand classes)",
    )


def check_seed_contract() -> Result:
    cmd_dir = _path("apps/core/management/commands")
    if not cmd_dir.exists():
        return _skip("seed_contract", "no management/commands directory found")
    scripts = [p for p in cmd_dir.glob("seed_*.py") if p.name != "seed_dummy_data.py"]
    if not scripts:
        return _skip(
            "seed_contract",
            "no generated seed_*.py command yet (run customize-use-case to create vertical data)",
        )
    classes = _model_fields(_read(MODELS))
    known = {field for fields in classes.values() for field in fields}
    # Django model constructors also accept the implicit pk and *_id FK aliases.
    known |= {"id", "pk", "user_id", "patient_id", "invoice_id", "created_by_id"}
    problems: list[str] = []
    for script in scripts:
        try:
            text = script.read_text(encoding="utf-8")
            tree = ast.parse(text)
        except SyntaxError as exc:
            problems.append(f"{script.name}:{exc.lineno} {exc.msg}")
            continue
        used_kwargs: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = (
                    func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
                )
                # match Model(...) and Model.objects.create(...) constructors
                if name in MODEL_FIELDS or name in {
                    "create",
                    "get_or_create",
                    "update_or_create",
                }:
                    used_kwargs.update(kw.arg for kw in node.keywords if kw.arg)
        unknown = sorted(used_kwargs - known - {"defaults"})
        if unknown:
            problems.append(f"{script.name} sets unknown field(s) {unknown}")
        # Full persona + data switch: a vertical seed must replace the healthcare
        # persona with its own industry logins and re-skin EVERY surface, not just
        # labs and visits. Reusing the baseline patient* users (no create_user) or
        # skipping invoices/profiles leaves healthcare identity and billing showing.
        if "create_user" not in text:
            problems.append(
                f"{script.name} never calls User.objects.create_user(...) — create the "
                "industry demo logins (e.g. operator1) so the persona switches; do not "
                "reuse the healthcare patient* users"
            )
        missing_tables = [
            t
            for t in (
                "PatientProfile",
                "LabTest",
                "DoctorVisit",
                "Invoice",
                "InvoiceLineItem",
            )
            if t not in text
        ]
        if missing_tables:
            problems.append(
                f"{script.name} does not reseed {missing_tables} — switch every surface to "
                "the target industry (operator site/profile, inspections, work orders AND "
                "purchase orders), not only labs and visits"
            )
    if problems:
        return _fail(
            "seed_contract",
            "; ".join(problems),
            "Seed commands must (1) populate existing model fields only — map vertical concepts onto current fields (e.g. an inspection reading onto LabTest.result_value), no invented names; and (2) perform a FULL persona switch — create industry logins via User.objects.create_user(...) and reseed every surface (PatientProfile, LabTest, DoctorVisit, Invoice, InvoiceLineItem) so no healthcare identity or billing leaks through.",
        )
    return _ok(
        "seed_contract",
        f"{len(scripts)} generated seed command(s) switch persona + populate known model fields only",
    )


def check_calculators() -> Result:
    """Every calculator URL must resolve to a view, and any finance service
    functions referenced by views must be defined. On the baseline this passes
    trivially (the single investment calculator)."""
    urls_src = _read(URLS)
    views_src = _read(VIEWS)
    view_funcs = set(
        re.findall(r"^def\s+([a-z_][a-z0-9_]*)\s*\(", views_src, re.MULTILINE)
    )
    # views referenced from urls.py as views.<name>
    referenced = set(re.findall(r"views\.([a-z_][a-z0-9_]*)", urls_src))
    missing_views = sorted(referenced - view_funcs)
    if missing_views:
        return _fail(
            "calculators",
            f"urls.py references undefined view(s) {missing_views}",
            "Define each view in apps/core/views.py before wiring its URL.",
        )
    # if a finance service module exists, calculate_* helpers used by views must exist there or in views
    finance_rel = "apps/core/services/finance.py"
    finance_funcs: set[str] = set()
    if _exists(finance_rel):
        finance_funcs = set(
            re.findall(
                r"^def\s+(calculate_[a-z0-9_]+)\s*\(", _read(finance_rel), re.MULTILINE
            )
        )
    local_calc = set(
        re.findall(r"^def\s+(calculate_[a-z0-9_]+)\s*\(", views_src, re.MULTILINE)
    )
    used_calc = set(re.findall(r"\b(calculate_[a-z0-9_]+)\s*\(", views_src))
    undefined = sorted(used_calc - finance_funcs - local_calc)
    if undefined:
        return _fail(
            "calculators",
            f"views call undefined calculator(s) {undefined}",
            "Define each calculate_* function in apps/core/services/finance.py (or views.py) before calling it.",
        )
    return _ok(
        "calculators",
        f"{len(referenced)} portal/tool view(s) resolve; calculators defined",
    )


def check_tests() -> Result:
    return _skip(
        "tests",
        "no enforced suite here; static gates are `npm run typecheck`, `python manage.py check`, and `python manage.py makemigrations --check --dry-run`",
    )


def helper_self_tests() -> list[Result]:
    results: list[Result] = []
    sample_models = _model_fields(
        "class LabTest(models.Model):\n"
        "    test_name = models.CharField(max_length=200)\n"
        "    is_abnormal = models.BooleanField(default=False)\n"
    )
    results.append(
        _ok("self_model_parse", "model field parser extracts Django fields")
        if sample_models.get("LabTest") == {"test_name", "is_abnormal"}
        else _fail("self_model_parse", f"got {sample_models}", "Fix _model_fields.")
    )
    ctx = _dict_keys_in_context(
        "def patient_dashboard(request):\n"
        "    context = {\n        'total_labs': 1,\n        'recent_labs': [],\n    }\n"
        "    return context\n",
        "patient_dashboard",
    )
    results.append(
        _ok("self_context_parse", "context-key parser extracts dashboard keys")
        if ctx == {"total_labs", "recent_labs"}
        else _fail("self_context_parse", f"got {ctx}", "Fix _dict_keys_in_context.")
    )
    results.append(
        _ok(
            "self_enum_membership",
            "synthetic visit_type codes are within the closed enum",
        )
        if {"checkup", "urgent"} <= VISIT_TYPE_CODES
        else _fail("self_enum_membership", "enum failed", "Fix VISIT_TYPE_CODES.")
    )
    return results


CHECKS: dict[str, Callable[[], Result]] = {
    "environment": check_environment,
    "backend_compile": check_backend_compile,
    "schema_integrity": check_schema_integrity,
    "api_contract": check_api_contract,
    "visit_type_enum": check_visit_type_enum,
    "domain_manifest": check_domain_manifest,
    "ui_contract": check_ui_contract,
    "theme_contract": check_theme_contract,
    "seed_contract": check_seed_contract,
    "calculators": check_calculators,
    "tests": check_tests,
}


def emit(results: Iterable[Result]) -> int:
    failed = 0
    for result in results:
        status = "SKIP" if result.skipped else "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.details}")
        print(result.as_json(), file=sys.stderr)
        if not result.passed and not result.skipped:
            failed += 1
            if result.remediation:
                print(f"       remediation: {result.remediation}")
    print(f"Summary: {failed} failed")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Validate {SKILL_NAME} artifacts for the Stingray Django app."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run validator helper self-tests without reading app files.",
    )
    parser.add_argument(
        "--check",
        action="append",
        choices=sorted(CHECKS),
        help="Run one check; repeat for multiple.",
    )
    args = parser.parse_args()
    if args.self_test:
        return emit(helper_self_tests())
    selected = args.check or list(CHECKS)
    return emit(CHECKS[name]() for name in selected)


if __name__ == "__main__":
    raise SystemExit(main())
