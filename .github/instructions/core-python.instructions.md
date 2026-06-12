---
applyTo: '**/apps/core/**/*.py'
description: 'Django backend conventions for the apps.core app (views, models, domain manifest, admin)'
---

# Stingray Health Portal — apps.core Python Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->
## Views
- Views handling patient data or the portal MUST be decorated with `@login_required`; public marketing/tool views (home, about, pricing, free_tools, investment_calculator) MUST remain undecorated (evidence: apps/core/views.py:32, :120, :154, :187, :207).
- Views MUST import models lazily inside the function body (`from .models import LabTest`), not at module top level (evidence: apps/core/views.py:123, :157, :190, :210).
- Views MUST scope per-patient querysets with `.filter(patient=request.user)`; never return another user's records (evidence: apps/core/views.py:127, :160, :193).
- Views MUST assemble a `context` dict and end with `return render(request, "core/<template>.html", context)` (evidence: apps/core/views.py:141-151, :177-184).
- Dashboard/page `context` keys are a stable template contract — MUST NOT rename existing keys (e.g. `recent_labs`, `total_unpaid_amount`) when editing views (evidence: apps/core/views.py:141, :243; apps/core/domain.py docstring).
- Distinct chip/filter lists MUST insert an empty `.order_by()` before `.values_list(...).distinct()` to clear `Meta.ordering`, otherwise DISTINCT duplicates rows (evidence: apps/core/views.py:170-175; apps/core/models.py:48-49).
- List views aggregating related rows SHOULD use `.select_related()` / `.prefetch_related()` (evidence: apps/core/views.py:212-217).

## Domain manifest
- `apps/core/domain.py` is the single source of truth for display copy; industry adaptations MUST edit the `DOMAIN` dict and MUST preserve model field names, context keys, URL names/paths, and `visit_type` enum codes (evidence: apps/core/domain.py:1-7).
- `visit_type` codes (`checkup`, `follow_up`, `urgent`, `specialist`, `preventive`) MUST stay stable; relabel via `DOMAIN["visit_type_labels"]`, never by editing `DoctorVisit.VISIT_TYPE_CHOICES` (evidence: apps/core/domain.py:78-84; apps/core/models.py:58-64).
- Expose the manifest to templates only through the existing `domain` context processor and `domain_json` view — do not re-import `DOMAIN` ad hoc in new views (evidence: apps/core/context_processors.py:4-5, apps/core/views.py:10-11).

## Models
- Every model MUST define a `__str__` returning a human-readable label (evidence: apps/core/models.py:19, :51, :93, :127, :144).
- Foreign keys to `User` MUST set an explicit `related_name` (evidence: apps/core/models.py:8-10, :32-34, :110).
- Enumerations MUST be declared as class-level `*_CHOICES` lists of `(code, label)` tuples and referenced via `choices=` (evidence: apps/core/models.py:26-30, :58-64, :102-107).
- Models with a natural sort MUST set `class Meta: ordering = [...]` (evidence: apps/core/models.py:48-49, :90-91, :124-125).

## URLs & admin
- Every `urlpatterns` entry MUST pass a `name=`; authenticated portal routes live under the `portal/` prefix (evidence: apps/core/urls.py:6-20).
- Admin classes MUST be registered with the `@admin.register(Model)` decorator and define `list_display`/`search_fields` (evidence: apps/core/admin.py:19-21, :33-35, :66-68).
<!-- END GENERATED -->
