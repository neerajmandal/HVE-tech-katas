---
applyTo: 'templates/**/*.html'
description: 'Django template conventions for the manufacturing vertical — domain-manifest copy binding, layout inheritance, and runtime accent theming.'
---

# Manufacturing Vertical — Templates Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->

## Domain Manifest Binding

- User-facing copy (brand, nav labels, page titles/subtitles, entity terms, stats) MUST be rendered from `domain.*` context, never hardcoded strings (evidence: templates/base.html:10, templates/base.html:30, templates/portal_base.html:31-32, templates/core/doctor_visits.html:4-5).
- Any template that reads manifest dictionaries by key MUST `{% load domain_extras %}` before using the `dict_get` filter (evidence: templates/core/doctor_visits.html:2, apps/core/templatetags/domain_extras.py:6-11).
- `visit_type` labels MUST be resolved via `domain.visit_type_labels|dict_get:"<code>"` (or `:visit.visit_type`); never use `get_visit_type_display` (evidence: templates/core/doctor_visits.html:21-41, templates/core/doctor_visits.html:77).
- Visit-detail section headings MUST bind to `domain.entities.visit.reason_label` / `diagnosis_label` / `plan_label` (with `|default:` fallbacks) rather than fixed clinical wording (evidence: templates/core/doctor_visits.html:85, templates/core/doctor_visits.html:115, templates/core/doctor_visits.html:121, apps/core/domain.py:52-54).
- `visit_type` filter codes used in `{% if %}` branches and `?type=` links MUST stay the five stable codes (`checkup`, `follow_up`, `urgent`, `specialist`, `preventive`) (evidence: templates/core/doctor_visits.html:18-41, apps/core/domain.py:78-84).

## Layout & Inheritance

- Public/marketing pages MUST `{% extends "base.html" %}`; authenticated portal pages MUST `{% extends "portal_base.html" %}` (evidence: templates/core/home.html:1, templates/core/dashboard.html:1, templates/core/doctor_visits.html:1, templates/core/lab_tests.html:1).
- Both layout shells MUST include `{% include 'partials/_theme_style.html' %}` in `<head>` so the manifest accent override is applied at runtime (evidence: templates/base.html:18, templates/portal_base.html:16).

## Theming

- Accent surfaces MUST use the `accent-*` / `accent2-*` token utilities (e.g. `text-accent-600`, `bg-accent-600`, `ring-accent-500`); never hardcode teal or hex colors, so the manifest theme override re-skins them at runtime (evidence: templates/base.html:30, templates/base.html:60, templates/portal_base.html:32, templates/core/doctor_visits.html:15).
- The accent CSS variables are defined by the `@theme` scale in `static/input.css` and overridden per-vertical by `_theme_style.html` from `domain.theme.accent` / `domain.theme.accent2`; keep utility class names aligned with those variable names (evidence: static/input.css:15-28, templates/partials/_theme_style.html:1-16, apps/core/domain.py:122-140).
- Avatar/background colors driven by the manifest MUST read `domain.theme.avatar_bg` rather than embedding a hex value (evidence: templates/portal_base.html:41, templates/portal_base.html:129, apps/core/domain.py:139).

<!-- END GENERATED -->
