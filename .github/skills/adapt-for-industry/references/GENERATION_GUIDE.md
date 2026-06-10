# Generation Guide — adapt-for-industry

This guide describes how to generate the **domain manifest** that re-skins the
Stingray portal (Django) for a new industry. The manifest is the single source of
truth for vertical display copy; the app's structure (models, views, URL names,
context keys, enum codes) stays stable.

## Sibling-pack principle

Generate new files; never overwrite baseline template *logic*. The only edits to
existing files are mechanical: swapping a hardcoded healthcare string for a
`{{ domain.* }}` field, and adding one line to `settings.py`. Reverting an
adaptation is then `git restore` of the wired templates/settings plus deleting
the generated manifest files.

Generated/added:

```text
apps/core/domain.py                 # the DOMAIN dict (manifest, incl. `theme` accent block)
apps/core/context_processors.py     # def domain(request) -> {"domain": DOMAIN}
apps/core/templatetags/__init__.py  # makes templatetags a package
apps/core/templatetags/domain_extras.py  # dict_get filter (renders visit_type_labels)
templates/partials/_theme_style.html     # inline <style> overriding the accent @theme vars from domain.theme
```

Edited (string swaps only, plus one settings line and the JSON endpoint):

```text
StingrayHealthPortal/settings.py    # append "apps.core.context_processors.domain"
apps/core/views.py                  # add domain_json view
apps/core/urls.py                   # add path("portal/domain.json", ...)
templates/base.html                 # brand; include _theme_style; teal→accent
templates/portal_base.html          # brand, role, nav, assistant, page meta; include _theme_style; teal→accent; avatar_bg
templates/core/dashboard.html       # stat labels, section headings, badges, visit_type, followups heading; teal→accent
templates/core/lab_tests.html       # title/subtitle, table headers (record/category/ordered_by); teal→accent
templates/core/doctor_visits.html   # title/subtitle, visit_type filter chips + badge, detail labels (reason/diagnosis/plan), vitals guard; teal→accent
templates/core/invoices_list.html   # title/subtitle
templates/core/home.html            # PUBLIC landing: hero + preview cards + stats -> domain.home.*; teal→accent / cyan→accent2
templates/core/welcome.html         # PUBLIC welcome: heading/blurb/quick-links -> domain.home.*; teal→accent / cyan→accent2
templates/account/login.html        # teal→accent
templates/account/signup.html       # teal→accent
templates/account/logout.html       # teal→accent
```

Permanent enablement (committed once, inert on the baseline — like the safelist):

```text
static/input.css                    # @theme accent/accent2 color scale (healthcare defaults)
```

## Entity-mapping anchor

Map the vertical onto the existing models first (see `.github/skills/README.md`):

- `User` (auth) → the person who signs in.
- `PatientProfile` → per-user profile/affiliation (reuse `insurance_provider` /
  `insurance_policy_number` as generic affiliation/identifier fields).
- `LabTest` → a measured **observation**: `test_name`, `test_category`,
  `ordered_by`, `result_value`, `reference_range`, `unit`, `is_abnormal`,
  `status`.
- `DoctorVisit` → a scheduled **interaction/event**: `doctor_name`, `specialty`,
  `visit_type` (closed enum), `reason`, `diagnosis`, `treatment_plan`,
  `follow_up_date`.
- `Invoice` + `InvoiceLineItem` → a **billing document** with line items.

If a concept cannot map onto an existing field, document the intentional schema
change and update model, migration, view, template, and seed together — do not
rename fields casually.

## Manifest shape (`apps/core/domain.py`)

Use a plain dict so the same object can be returned from the context processor
and the `domain_json` view (JSON-serializable). Keep nav `url_name` targets
pointing at real URL names.

```python
# apps/core/domain.py
DOMAIN = {
    "industry": "manufacturing",
    "brand": {"name": "Stingray", "suffix": "Operations Portal",
              "tagline": "Plant performance and asset reliability at a glance"},
    "role_label": "Operator",
    "assistant_label": "Maintenance AI",
    "nav": {
        "group": "Operations",
        "records": {"url_name": "lab_tests", "label": "Inspections"},
        "visits":  {"url_name": "doctor_visits", "label": "Work Orders"},
    },
    "page_meta": {
        "patient_dashboard": {"title": "Operations Dashboard", "subtitle": "Welcome back"},
        "lab_tests":  {"title": "Inspections", "subtitle": "Equipment inspection readings"},
        "doctor_visits": {"title": "Work Orders", "subtitle": "Maintenance activity"},
    },
    "entities": {
        "record":  {"singular": "Inspection", "plural": "Inspections", "category": "Discipline",
                    "abnormal": "Out of Spec", "normal": "In Spec", "pending": "Pending",
                    "ordered_by": "Inspector"},
        "visit":   {"singular": "Work Order", "plural": "Work Orders",
                    "provider": "Technician", "specialty": "Discipline",
                    "reason_label": "Work Requested", "diagnosis_label": "Findings",
                    "plan_label": "Corrective Action"},
        "invoice": {"singular": "Purchase Order", "plural": "Purchase Orders", "party": "Supplier"},
    },
    "dashboard": {
        "stats": {"total": "Total Inspections", "pending": "Pending Inspections",
                  "abnormal": "Out of Spec", "visits": "Work Orders"},
        "recent_records": "Recent Inspections", "recent_visits": "Recent Work Orders",
        "followups": "Upcoming Scheduled Maintenance", "followup_prefix": "Next service for",
    },
    "invoices": {"title": "Procurement Dashboard",
                 "subtitle": "Manage purchase orders and supplier billing"},
    "visit_type_labels": {
        "checkup": "Routine Inspection", "follow_up": "Re-inspection",
        "urgent": "Breakdown Repair", "specialist": "Specialist Service",
        "preventive": "Preventive Maintenance",
    },
    "home": {"eyebrow": "Industrial operations", "headline_lead": "Asset reliability,",
             "headline_accent": "at a glance", "blurb": "...", "stat_label": "Assets monitored"},
    "welcome": {"heading": "Welcome aboard", "blurb": "..."},
    "compliance": {"frameworks": ["ISO 9001", "OSHA", "ISO 55000"],
                   "note": "Synthetic demonstration data only; not a system of record."},
    "theme": {  # per-industry accent (see "Per-industry accent theming")
        "accent":  {"50": "#fffbeb", "100": "#fef3c7", "300": "#fcd34d", "400": "#fbbf24",
                    "500": "#f59e0b", "600": "#d97706", "700": "#b45309", "900": "#78350f"},
        "accent2": {"400": "#fb923c", "500": "#f97316", "600": "#ea580c", "700": "#c2410c"},
        "avatar_bg": "d97706",
    },
}
```

## Context processor + registration

```python
# apps/core/context_processors.py
from .domain import DOMAIN


def domain(request):
    return {"domain": DOMAIN}
```

```python
# StingrayHealthPortal/settings.py  -> TEMPLATES[0]["OPTIONS"]["context_processors"]
"context_processors": [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "apps.core.context_processors.domain",   # <-- add
],
```

## Parity endpoint (`/portal/domain.json`)

```python
# apps/core/views.py
from django.http import JsonResponse
from .domain import DOMAIN


def domain_json(request):
    return JsonResponse(DOMAIN)
```

```python
# apps/core/urls.py
path("portal/domain.json", views.domain_json, name="domain_json"),
```

## Template wiring examples

`templates/portal_base.html` (brand + role + nav, string swaps only):

```django
<h1 class="text-lg font-bold text-white leading-tight">{{ domain.brand.name }}</h1>
<p class="text-xs text-teal-400 font-medium">{{ domain.brand.suffix }}</p>
...
<p class="text-xs text-slate-400">{{ domain.role_label }}</p>
...
<p class="...uppercase...">{{ domain.nav.group }}</p>
<a href="{% url domain.nav.records.url_name %}" ...>{{ domain.nav.records.label }}</a>
<a href="{% url domain.nav.visits.url_name %}" ...>{{ domain.nav.visits.label }}</a>
...
{{ domain.assistant_label }}   {# was "Nurse AI" #}
```

> `{% url domain.nav.records.url_name %}` works because Django's `url` tag
> accepts a context variable holding the URL name.

`templates/core/dashboard.html` (stat label, string swap only):

```django
<p class="...">{{ domain.dashboard.stats.total }}</p>   {# was "Total Lab Tests" #}
```

## Re-skinning `visit_type` labels (manifest, not the model)

`visit_type` is a closed enum (`checkup`, `follow_up`, `urgent`, `specialist`,
`preventive`). Re-skin only the **display labels**, through the manifest's
`visit_type_labels` — keep both the model **codes and choice labels untouched**
(changing the model is not needed and splits the source of truth).

Templates that show a visit type (`dashboard.html`, `doctor_visits.html`) bind to
the model with `{{ visit.get_visit_type_display }}`, which renders the *model's*
healthcare labels ("Annual Checkup") and ignores the manifest. Django templates
cannot index a dict by a variable key directly, so generate a tiny filter and
route the code through the manifest instead:

```python
# apps/core/templatetags/domain_extras.py
from django import template

register = template.Library()


@register.filter
def dict_get(mapping, key):
    """Look up ``mapping[key]`` from a template, falling back to the key."""
    if isinstance(mapping, dict):
        return mapping.get(key, key)
    return key
```

Then in each visit-type template, load the tag library and replace the model
display call:

```django
{% load domain_extras %}
...
{{ domain.visit_type_labels|dict_get:visit.visit_type }}   {# was visit.get_visit_type_display #}
```

> The `ui_contract` check fails if `dashboard.html` or `doctor_visits.html` still
> contains `get_visit_type_display` once a manifest is present — that is exactly
> the label↔binding drift that left "Annual Checkup" on a manufacturing portal.

### Don't forget the visit-type FILTER chips and the clinical vitals panel

`doctor_visits.html` has a second place that hardcodes healthcare visit types: the
**filter chips** (`Checkup`, `Urgent Care`, …). Re-skin each chip label through the
same manifest filter (`{{ domain.visit_type_labels|dict_get:"urgent" }}`) and the
"Visit Type:" caption via `{{ domain.entities.visit.singular }} Type:`. Otherwise
a manufacturing portal still offers an "Urgent Care" filter.

The visit detail card also renders a **clinical vitals panel** (Blood Pressure,
Heart Rate, Temperature °F, Weight). Non-clinical verticals leave `vitals_*` empty,
so guard the panel and let it disappear instead of showing `None bpm / 56°F`:

```django
{% if visit.vitals_bp or visit.vitals_heart_rate or visit.vitals_temperature or visit.vitals_weight %}
  ... vitals grid ...
{% endif %}
```

### Re-skin the three visit-detail field LABELS (clinical-leak gotcha)

The visit detail card renders three free-text `DoctorVisit` fields under fixed
headings that are *clinical by default*: **Reason for Visit** (`visit.reason`),
**Diagnosis** (`visit.diagnosis`) and **Treatment Plan** (`visit.treatment_plan`).
These are NOT covered by the visit-type or vitals work above — left alone, a legal
or finance portal still shows "Diagnosis" / "Treatment Plan" over its data. Bind
each heading to the manifest, keeping the healthcare label as the `default` so the
baseline (no manifest) is unchanged:

```django
{{ domain.entities.visit.reason_label|default:"Reason for Visit" }}
{{ domain.entities.visit.diagnosis_label|default:"Diagnosis" }}
{{ domain.entities.visit.plan_label|default:"Treatment Plan" }}
```

So **every** manifest's `entities.visit` MUST define `reason_label`,
`diagnosis_label` and `plan_label` (e.g. legal → Matter Summary / Assessment /
Recommended Action; manufacturing → Work Requested / Findings / Corrective Action).
The `ui_contract` check fails if `doctor_visits.html` does not bind all three to
`domain.entities.visit.*` or if the active manifest omits any of the three keys.

`lab_tests.html` likewise has table headers (`Test Name`, `Category`, `Ordered By`)
— bind them to `domain.entities.record.singular/category/ordered_by`. The
`ui_contract` check now scans `lab_tests.html`, `doctor_visits.html`, and
`invoices_list.html` for leftover healthcare literals, so a partial re-skin of any
list page fails the validator.

> **Seed categories that repeat across records (distinct() gotcha).** Verticals
> usually reuse a `test_category` / Practice Area across several records (e.g. two
> "Litigation" assessments), unlike the healthcare baseline where categories were
> mostly unique per patient. The lab_tests view builds its Category filter chips
> with `.order_by().values_list("test_category", flat=True).distinct()` — the
> `.order_by()` is **required** to clear `LabTest.Meta.ordering=['-order_date']`,
> otherwise Django pulls `order_date` into the `SELECT DISTINCT` and the same
> category renders as two chips. Do not remove that `.order_by()`.

### Re-skin the PUBLIC landing + welcome pages (front-door leak)

`home.html` (unauthenticated landing) and `welcome.html` (post-signup) are NOT
part of the portal chrome scan, and they carry the heaviest healthcare copy of any
page: the hero headline (**"Your Health Records"**), the three decorative preview
cards (**"Complete Blood Count" / Hematology / WBC / Hemoglobin**, **"Dr. Williams -
Cardiology" / Annual Checkup**, **"Lipid Panel"**), the stats (**"Patients
Served"**, "Lab Results Delivered") and the welcome quick-links. Left alone, a
visitor's *first* screen still says "Your Health Records" even though the logged-in
portal is fully re-skinned.

Bind every one of these to a manifest **`home`** block, each value defaulted to its
healthcare original so the baseline (no manifest) is unchanged:

```django
{{ domain.home.hero_title_lead|default:"Your Health Records," }}
{{ domain.home.preview_record_title|default:"Complete Blood Count" }}
{{ domain.home.stat1_label|default:"Patients Served" }}
```

So every manifest MUST define a `home` block. Suggested keys (flat, so each gets a
clean `|default:`): `hero_badge`, `hero_title_lead`, `hero_title_emphasis`,
`hero_subtitle`, `cta_authed`, `cta_guest`, `cta_learn`, `stat{1,2,3}_value`,
`stat{1,2,3}_label`, `preview_record_{title,category,status,metric1_label,
metric1_value,metric2_label,metric2_value,footer}`, `preview_visit_{title,subtitle}`,
`preview_pending_{title,subtitle}`, `welcome_subtitle`, `welcome_cta_title`,
`welcome_cta_body`, `quicklink_{records,visits,about}_desc`. (`welcome.html`'s
quick-link headings reuse `domain.nav.records.label` / `domain.nav.visits.label`.)
The `ui_contract` check fails if either public template lacks a `domain.home.` bind
or the manifest omits the `home` block.

## Per-industry accent theming (manifest-driven)

Each vertical also gets its **own accent color** (healthcare teal, finance indigo,
manufacturing amber, …), driven from the same manifest — not a per-adaptation
find/replace. The `theme_contract` validator check enforces this end to end.

### How it works (Tailwind v4)

The accent is a **Tailwind v4 `@theme` color scale** registered once in
`static/input.css`. Tailwind generates `accent-*` / `accent2-*` utilities whose
values are `var(--color-accent-*)` references, so overriding those CSS variables
at runtime re-skins **every** accent surface with zero class-name edits:

```css
/* static/input.css — permanent, healthcare defaults */
@theme {
  --color-accent-50:  #f0fdfa;  --color-accent-100: #ccfbf1;
  --color-accent-300: #5eead4;  --color-accent-400: #2dd4bf;
  --color-accent-500: #14b8a6;  --color-accent-600: #0d9488;
  --color-accent-700: #0f766e;  --color-accent-900: #134e4a;
  --color-accent2-400: #22d3ee; --color-accent2-500: #06b6d4;
  --color-accent2-600: #0891b2; --color-accent2-700: #0e7490;
}
```

> **Tailwind v4 gotcha (learned the hard way):** `theme.extend.colors` in
> `tailwind.config.js` is **ignored** by Tailwind v4 — declaring `accent` there
> produces **no** utilities. The scale MUST be declared with `@theme` in
> `input.css`. (The legacy JS config is still read for `content`/`safelist`, which
> is why teal kept compiling, masking the problem.) Verify after `npm run build`
> that `static/output.css` contains `.text-accent-600 { color: var(--color-accent-600) }`.

### Generation steps

1. **Manifest `theme` block** in `apps/core/domain.py` — per-industry hex scales
   plus `avatar_bg` (the hex, no `#`, passed to ui-avatars):

   ```python
   "theme": {
       "accent":  {"50": "#eef2ff", "100": "#e0e7ff", "300": "#a5b4fc",
                   "400": "#818cf8", "500": "#6366f1", "600": "#4f46e5",
                   "700": "#4338ca", "900": "#312e81"},          # finance indigo
       "accent2": {"400": "#a78bfa", "500": "#8b5cf6",
                   "600": "#7c3aed", "700": "#6d28d9"},           # violet secondary
       "avatar_bg": "4f46e5",
   },
   ```

2. **Override partial** `templates/partials/_theme_style.html` — emits an inline
   `<style>` that overrides the `@theme` vars from the manifest (no-op on the
   baseline via `{% if domain.theme %}`):

   ```django
   {% if domain.theme %}<style>
     :root {
       --color-accent-50: {{ domain.theme.accent.50 }};
       /* …100,300,400,500,600,700,900… */
       --color-accent-900: {{ domain.theme.accent.900 }};
       --color-accent2-400: {{ domain.theme.accent2.400 }};
       /* …500,600,700… */
     }
   </style>{% endif %}
   ```

3. **Include it in both root layouts** — add
   `{% include 'partials/_theme_style.html' %}` to the `<head>` of
   `templates/base.html` **and** `templates/portal_base.html`, right after the
   `output.css` link so it wins the cascade.

4. **Replace brand color classes** in the themed templates: `teal-*` → `accent-*`
   and `cyan-*` → `accent2-*` (covers `bg-`, `text-`, `border-`, `ring-`,
   `from-`/`via-`/`to-` gradients, and `/opacity` modifiers). Themed files:
   `base.html`, `portal_base.html`, `core/dashboard.html`, `core/doctor_visits.html`,
   `core/lab_tests.html`, `core/home.html`, `core/welcome.html`,
   `account/login.html`, `account/signup.html`, `account/logout.html`. Also swap
   the hardcoded ui-avatars `background=0d9488` for `{{ domain.theme.avatar_bg }}`
   in `portal_base.html`.

5. **Leave semantic/status colors alone** — `red`/`amber`/`green`/`purple` (visit
   badges, abnormal/pending states) and `slate`/`gray` (sidebar, chrome) are NOT
   the brand accent; keep them so status stays legible across verticals.

6. **Rebuild and restart**: `npm run build` (Tailwind + collectstatic), then
   restart the dev server (`deploy-adaptation` owns this). The shades used across
   templates are accent `{50,100,300,400,500,600,700,900}` and accent2
   `{400,500,600,700}` — keep the manifest scale complete or a surface falls back
   to the healthcare default.

> `static/input.css` (the `@theme` scale, healthcare defaults) is **permanent
> enablement** — like the existing safelist — so adaptations only supply colors.
> It is inert on the baseline because no baseline template references `accent-*`.
> The per-adaptation parts (manifest `theme`, the partial, the two includes, and
> the `teal→accent` template swaps) roll back with the rest of the adaptation.

## UI contract — why bindings stay stable

The `ui_contract` validator check enforces that every template which reads the
manifest no longer hardcodes a baseline healthcare label, and that manifest nav
targets resolve to real URL names. This mirrors the "display label vs data
binding" discipline: re-skin the words, keep the bindings. A page can render
fine while a stat silently reads the wrong field if a label is changed without
re-checking its binding — the manifest + validator prevent that.

## Compliance

State frameworks in `compliance.frameworks` and a short, **non-legal** note in
`compliance.note` (e.g. "Synthetic demonstration data; not a system of record").
Use synthetic data only. Healthcare → HIPAA/FHIR; finance → SOX/PCI-DSS/KYC-AML;
manufacturing → ISO 9001/OSHA/ISO 55000; legal → eDiscovery/privilege; education
→ FERPA. Multilingual/i18n/localization are out of scope.
