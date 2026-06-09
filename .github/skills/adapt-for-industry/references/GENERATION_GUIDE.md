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
apps/core/domain.py                 # the DOMAIN dict (manifest)
apps/core/context_processors.py     # def domain(request) -> {"domain": DOMAIN}
```

Edited (string swaps only, plus one settings line and the JSON endpoint):

```text
StingrayHealthPortal/settings.py    # append "apps.core.context_processors.domain"
apps/core/views.py                  # add domain_json view
apps/core/urls.py                   # add path("portal/domain.json", ...)
templates/base.html                 # brand
templates/portal_base.html          # brand, role, nav group/labels, assistant, page meta
templates/core/dashboard.html       # stat labels, section headings, badges
templates/core/lab_tests.html       # title/labels/empty copy
templates/core/doctor_visits.html   # title/labels/empty copy
templates/core/invoices_list.html   # title/subtitle
templates/core/home.html            # hero/feature copy
templates/core/welcome.html         # heading/blurb
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
                    "provider": "Technician", "specialty": "Discipline"},
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
