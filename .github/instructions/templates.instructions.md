---
applyTo: 'templates/**/*.html'
description: 'Django template conventions: domain-manifest binding and accent theming'
---

# Stingray Health Portal — Template Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->
## Domain-manifest binding
- User-facing copy (titles, subtitles, entity nouns, nav labels) MUST be rendered from the `domain.*` manifest, not hardcoded, so an industry adaptation re-skins via `apps/core/domain.py` alone (evidence: templates/core/doctor_visits.html:4-5, :11; templates/core/dashboard.html).
- Templates that read manifest dicts MUST declare `{% load domain_extras %}` at the top (evidence: templates/core/doctor_visits.html:2, templates/core/lab_tests.html:6).
- `visit_type` labels MUST be rendered with `domain.visit_type_labels|dict_get:"<code>"`; MUST NOT use `get_visit_type_display` or hardcode the label (evidence: templates/core/doctor_visits.html:21-41; apps/core/templatetags/domain_extras.py:6-11).
- Visit-detail headings MUST bind to `domain.entities.visit.reason_label` / `diagnosis_label` / `plan_label` rather than literal "Reason for Visit"/"Diagnosis"/"Treatment Plan" (evidence: apps/core/domain.py:47-55).

## Layout & theming
- Page templates MUST extend `base.html` (public) or `portal_base.html` (authenticated) rather than redefining `<html>` boilerplate (evidence: templates/core/doctor_visits.html:1, templates/base.html).
- Accent surfaces MUST use the `accent-*` / `accent2-*` utility classes (theme tokens), never hardcoded teal/hex, so the manifest theme override re-skins them at runtime (evidence: static/input.css:15-28, templates/core/doctor_visits.html:15; templates/partials/_theme_style.html).
<!-- END GENERATED -->
