---
applyTo: 'apps/core/**/*.py'
description: 'Django view, model, URL, admin, and domain-manifest conventions for the manufacturing vertical core app.'
---

# Manufacturing Vertical — Core App (Django) Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->

## Views

- Authenticated portal views MUST be decorated with `@login_required` from `django.contrib.auth.decorators`; public/marketing views (`home`, `about`, `pricing`, `free_tools`, `investment_calculator`) stay undecorated (evidence: apps/core/views.py:32-35, apps/core/views.py:120-121, apps/core/views.py:14-15).
- Model classes MUST be imported lazily inside the view body, not at module top, to keep `views.py` import-light (evidence: apps/core/views.py:123, apps/core/views.py:157, apps/core/views.py:190, apps/core/views.py:210).
- Per-user data views MUST scope querysets to `request.user` via `.filter(patient=user)`; never return another user's records (evidence: apps/core/views.py:125-133, apps/core/views.py:160, apps/core/views.py:193).
- Views MUST build an explicit `context` dict with stable keys and return `render(request, "<template>", context)`; do not pass `locals()` (evidence: apps/core/views.py:141-151, apps/core/views.py:177-184, apps/core/views.py:199-204).
- Context keys feeding the dashboard/list templates (e.g. `recent_labs`, `total_labs`, `pending_labs`, `abnormal_labs`, `recent_visits`, `total_visits`, `upcoming_followups`) MUST be preserved by adaptations — templates bind to these names (evidence: apps/core/views.py:141-149).
- Distinct filter-option lists MUST use `.order_by().values_list("<field>", flat=True).distinct()` to clear default ordering before deduping (evidence: apps/core/views.py:170-175).
- Cross-user list views spanning related rows MUST use `.select_related(...)`/`.prefetch_related(...)` to avoid N+1 queries (evidence: apps/core/views.py:212-217).

## Models

- Every model MUST define `__str__` returning a human-readable label (evidence: apps/core/models.py:19-20, apps/core/models.py:51-52, apps/core/models.py:93-96, apps/core/models.py:127-128).
- ForeignKey/OneToOne fields MUST set an explicit `related_name` for reverse access (evidence: apps/core/models.py:8-10, apps/core/models.py:32-34, apps/core/models.py:66-68, apps/core/models.py:118-120, apps/core/models.py:134-136).
- Enumerated fields MUST use a `*_CHOICES` list on the model with a `default` (evidence: apps/core/models.py:26-30, apps/core/models.py:58-64, apps/core/models.py:102-107).
- Models with a natural sort order MUST declare it via `class Meta: ordering = [...]` (evidence: apps/core/models.py:48-49, apps/core/models.py:90-91, apps/core/models.py:124-125).
- Adaptations MUST preserve existing model field names (e.g. `patient`, `visit_type`, `test_category`, `is_abnormal`); re-skin user-facing copy through the domain manifest instead of renaming fields (evidence: apps/core/models.py:32-44, apps/core/models.py:66-77, apps/core/domain.py:1-6).

## URLs

- Every route MUST be a named `path()` so templates resolve via `{% url '<name>' %}` (evidence: apps/core/urls.py:5-21).
- Authenticated portal routes MUST live under the `portal/` prefix and adaptations MUST preserve existing URL names and paths (`patient_dashboard`, `lab_tests`, `doctor_visits`, `domain_json`) (evidence: apps/core/urls.py:16-20).

## Admin

- Models MUST be registered with the `@admin.register(<Model>)` decorator on a `ModelAdmin` subclass (evidence: apps/core/admin.py:19-20, apps/core/admin.py:33-34, apps/core/admin.py:53-54, apps/core/admin.py:66-67).
- Each registered `ModelAdmin` MUST set `list_display` and `search_fields` (and `list_filter` where it aids triage) (evidence: apps/core/admin.py:21-29, apps/core/admin.py:35-50, apps/core/admin.py:55-63).

## Domain Manifest

- `apps/core/domain.py`'s `DOMAIN` dict is the single source of truth for vertical display copy; user-facing wording changes MUST be made there, not hardcoded in views or templates (evidence: apps/core/domain.py:1-9).
- The five `visit_type` codes (`checkup`, `follow_up`, `urgent`, `specialist`, `preventive`) MUST stay stable; relabel them via `DOMAIN["visit_type_labels"]` and never by editing `DoctorVisit.VISIT_TYPE_CHOICES` (evidence: apps/core/domain.py:78-84, apps/core/models.py:58-64).
- The manifest MUST be surfaced only through the `domain` context processor and the `domain_json` view; do not add ad-hoc `from .domain import DOMAIN` re-imports elsewhere (evidence: apps/core/context_processors.py:1-5, apps/core/views.py:7-11, apps/core/urls.py:20).

<!-- END GENERATED -->
