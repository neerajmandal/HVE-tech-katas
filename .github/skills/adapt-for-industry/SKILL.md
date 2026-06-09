---
name: adapt-for-industry
description: Adapt the Stingray portal (Django 5.2 backend, server-rendered Tailwind templates) from healthcare to a target industry by generating a domain manifest (apps/core/domain.py), registering a context processor that injects it into every template, exposing GET /portal/domain.json, wiring the templates to it, and driving customize-use-case to produce entity-mapped synthetic seed data — so a single invocation delivers an end-to-end vertical (chrome + data) while preserving model fields, dashboard context keys, URL names, and visit_type codes.
---

# Adapt for Industry — Stingray Portal (Django)

## Context

This app is a healthcare patient portal. The backend (`apps/core`) is Django 5.2
over SQLite; the display layer is Django templates under `templates/`. Industry
adaptation changes **brand, role labels, entity terminology, page copy, nav
labels, theme, compliance context, and sample data VALUES** while preserving
model field names, dashboard context keys, URL names/paths, and the `visit_type`
enum codes.

The mechanism is a single **domain manifest** read by every template:

- `apps/core/domain.py` defines a `DOMAIN` dict (the source of truth).
- `apps/core/context_processors.py` returns `{"domain": DOMAIN}`; registering it
  in `settings.py` injects `domain` into every template render.
- `apps/core/views.py` adds a `domain_json` view; `apps/core/urls.py` exposes it
  at `GET /portal/domain.json` (the parity/smoke endpoint, no auth) — the Django
  equivalent of katas2's `GET /api/domain`.

This skill **generates** the manifest, wires the templates to it, and then drives
`customize-use-case` to produce an entity-mapped synthetic **seed command** for
the vertical, so the demo data VALUES match the new industry rather than leaving
healthcare rows behind. The actual migrate/reseed/build/run are owned by
`deploy-adaptation` — this skill never mutates state itself.

## Step 1: Read the existing surfaces

Read before designing the pack:

- `README.md` and `.github/skills/README.md` (the entity-mapping anchor + contract table).
- `apps/core/models.py` — the six models and their fields (the stable schema).
- `apps/core/views.py` — `patient_dashboard` (the dashboard context keys),
  `lab_tests`, `doctor_visits`, `invoice_list` (the stable view/context contract).
- `apps/core/urls.py` — the URL names (`patient_dashboard`, `lab_tests`,
  `doctor_visits`, `invoice_list`) that nav targets must resolve to.
- `StingrayHealthPortal/settings.py` — the `TEMPLATES['OPTIONS']['context_processors']`
  list to extend.
- Display surfaces to re-skin: `templates/base.html`, `templates/portal_base.html`,
  and `templates/core/` (`dashboard.html`, `lab_tests.html`, `doctor_visits.html`,
  `invoices_list.html`, `home.html`, `welcome.html`, `about.html`, `pricing.html`,
  `free-tools.html`).
- `apps/core/models.py` `DoctorVisit.VISIT_TYPE_CHOICES` — the closed enum (first
  element is the code; second is the display label to re-skin).

Study where healthcare terminology appears as **display copy** versus where it is
a **stable binding** (field name, context key, URL name, enum code).

## Step 2: Identify the target industry

Ask the user for:

1. Target industry and sub-domain (e.g. *manufacturing — discrete assembly*).
2. Brand name + suffix + tagline (e.g. "Stingray Operations Portal").
3. The role label for a logged-in user (Patient → Operator / Client / Student).
4. Entity terminology: how the **observation** (`LabTest`), **interaction**
   (`DoctorVisit`), and **billing document** (`Invoice`) should be named, plus
   their sub-labels (category, provider, status/abnormal wording).
5. Display labels for `visit_type`'s five codes (`checkup`, `follow_up`,
   `urgent`, `specialist`, `preventive`) in the new vertical.
6. Regulatory/compliance frameworks that should follow the industry (see the
   Compliance Quick Sheet) and a short, non-legal compliance note for the footer.
7. Theme preference: keep the existing Tailwind accent (`teal-*`, lowest risk) or
   change it (requires editing static class names — see UI Adaptation Plan).

If the user is unsure, propose defaults from `references/EXAMPLES.md` and confirm.

## Step 3: Generate the domain manifest

Generate **sibling** files; do not overwrite baseline template logic beyond
swapping hardcoded display strings for `{{ domain.* }}` fields.

1. `apps/core/domain.py` — a `DOMAIN` dict (single source of truth for vertical
   display copy): industry slug, brand (name/suffix/tagline), role label,
   assistant label, nav (group + per-link `label`/`url_name`), per-page portal
   titles/subtitles, entity terms, dashboard stat labels + section headings,
   badge labels, invoices title/subtitle, home/welcome copy, and compliance
   (frameworks + note). Every nav `url_name` MUST be one of `patient_dashboard`,
   `lab_tests`, `doctor_visits`, `invoice_list` (the real names in `urls.py`).
2. `apps/core/context_processors.py` — `def domain(request): return {"domain": DOMAIN}`.
3. Register it in `StingrayHealthPortal/settings.py` by appending
   `"apps.core.context_processors.domain"` to
   `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
4. `apps/core/views.py` — add `def domain_json(request): return JsonResponse(DOMAIN)`.
5. `apps/core/urls.py` — add `path("portal/domain.json", views.domain_json, name="domain_json")`.

See `references/GENERATION_GUIDE.md` for the manifest shape and field list, and
`references/EXAMPLES.md` for ready-to-adapt manufacturing and finance presets.

## UI adaptation plan

Apply changes in this order:

- **Re-skin display copy first** by replacing hardcoded healthcare strings with
  `{{ domain.* }}` fields: brand in `base.html` + `portal_base.html`, role label
  + nav group/labels + assistant button in `portal_base.html`, the
  `{% block page_title %}`/`{% block page_subtitle %}` overrides per page,
  Dashboard stat labels + section headings + badge labels, list-page titles and
  empty-state copy, and the public pages' copy.
- **Re-skin `visit_type` labels** by editing the VALUES (second tuple element) in
  `DoctorVisit.VISIT_TYPE_CHOICES` and any template chip labels — keep the five
  codes unchanged. (Changing model choices is display-only and needs no
  migration since the stored values are the codes.)
- **Keep bindings stable**: do not rename model fields, dashboard context keys,
  URL names, or `visit_type` codes. If the vertical truly needs a new field,
  document the reason and update *every* consumer together (model → migration →
  view → template → seed).
- **Theme**: Tailwind compiles only static class names, so a color swap means
  find/replacing accent classes (e.g. `teal-600`→`amber-600`) across templates
  and rebuilding CSS, not a manifest value. Prefer keeping the accent unless the
  user insists.

## Compliance quick sheet

Include compliance **context** in the manifest note and any AI-assistant copy;
do not generate legal advice, and use synthetic data only.

- Healthcare: HIPAA, HL7/FHIR — patient/clinical data sensitivity.
- Financial services: SOX, PCI-DSS, KYC/AML, audit trails, money precision.
- Manufacturing: ISO 9001, OSHA, ISO 55000 (asset management), IoT/quality controls.
- Legal: eDiscovery, retention, privilege, matter/client confidentiality.
- Education: FERPA, student records, consent boundaries.
- Energy/utilities: grid/asset/outage/safety and regulatory reporting.
- Public sector: accessibility, records retention, data residency, procurement.

## Step 4: Generate the vertical's seed data (via customize-use-case)

Adapting for an industry covers **UI, data, and context** — not display copy
alone. The manifest only re-skins display strings, so this step is a **required
part of the adaptation**: drive `customize-use-case` to generate an entity-mapped
synthetic **seed command** for the same industry so the demo data VALUES match
the new vertical instead of leaving healthcare rows behind.

- Invoke `../customize-use-case/SKILL.md` and follow its **Step 4: Generate the
  seed command** to create `apps/core/management/commands/seed_<slug>.py` (use
  the same slug as the manifest `industry`). Map the vertical's records onto the
  existing fields only — observations → `LabTest`, interactions → `DoctorVisit`,
  billing → `Invoice` — reusing the five `visit_type` codes and the demo password
  (`password123`). State the seeded demo usernames.
- Make the seeded VALUES consistent with the manifest context: record names,
  categories, providers, statuses, and invoice line items should read as the new
  industry (e.g. finance metrics, advisors, statements), and `is_abnormal` should
  reflect the vertical's `abnormal` wording.
- Vertical **calculators** are optional and also belong to `customize-use-case`;
  generate them in the same pass only if the user wants them.
- Only skip the seed when the user **explicitly** asks for a chrome-only change;
  otherwise data generation is part of completing the adaptation.

## Step 5: Handoff

Record:

- The files created/modified (manifest, context processor, settings line,
  `domain_json` view + URL, wired templates, and the generated `seed_<slug>.py`).
- The seeded demo usernames so the smoke-test can log in.
- That `deploy-adaptation` must run the seed command, build Tailwind, and
  smoke-test — this skill does not mutate state.

## Step C: Validate

Run from the repo root. The `ui_contract` and `domain_manifest` checks prove the
manifest is wired and free of display/binding drift:

```bash
python .github/skills/validate-adaptation/validate.py
```

Self-test only:

```bash
python .github/skills/validate-adaptation/validate.py --self-test
```

See `../validate-adaptation/VALIDATE.md` for check details and remediation.

## Step D: Deploy

Generation does not migrate, reseed, build, or run the app. After validation,
hand off to `../deploy-adaptation/SKILL.md` to (re)seed the demo DB (via the
`seed_<slug>` command generated in Step 4), build Tailwind, and run the
smoke/Playwright checks.
