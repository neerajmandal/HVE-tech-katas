---
applyTo: 'templates/**/*.html'
description: 'Django template layout conventions for the Stingray Health Portal (base vs portal_base, blocks).'
---

# Stingray Health Portal — Templates Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->
## Template inheritance
- Every page template MUST start with an `{% extends ... %}` tag and place its body inside `{% block content %}...{% endblock %}` (evidence: templates/core/home.html:1, templates/core/home.html:3, templates/core/dashboard.html:1, templates/core/dashboard.html:6).
- Authenticated patient portal pages (dashboard, lab tests, doctor visits) MUST extend `portal_base.html` (the sidebar layout) (evidence: templates/core/dashboard.html:1, templates/core/lab_tests.html:1, templates/core/doctor_visits.html:1).
- Public marketing/tool pages (home, about, free tools, investment calculator, welcome, invoices) MUST extend `base.html` (the top-nav layout) (evidence: templates/core/home.html:1, templates/core/about.html:1, templates/core/free-tools.html:1, templates/core/invoices_list.html:1).

## Portal page blocks
- Templates extending `portal_base.html` SHOULD override `{% block page_title %}` and `{% block page_subtitle %}` to set the header bar text (evidence: templates/core/dashboard.html:3, templates/core/dashboard.html:4, templates/core/lab_tests.html:3, templates/core/doctor_visits.html:4).

## Base layout shared elements
- `base.html` and `portal_base.html` MUST load the compiled stylesheet via `{% load static %}` / `{% load compress %}` and `{% static 'output.css' %}`, and MUST expose a `{% block extra_head %}` for per-page head additions (evidence: templates/base.html:12, templates/base.html:16, templates/base.html:19, templates/portal_base.html:17).
- Inter-page links MUST use the `{% url '<name>' %}` tag with the named URL patterns, never hard-coded paths (evidence: templates/base.html:27, templates/base.html:46, templates/portal_base.html:55, templates/portal_base.html:66).
<!-- END GENERATED -->
