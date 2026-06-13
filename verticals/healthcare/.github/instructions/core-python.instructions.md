---
applyTo: 'apps/core/**/*.py'
description: 'Django backend conventions for the Stingray Health Portal core app (views, models, URLs, admin).'
---

# Stingray Health Portal — core app (Django) Instructions

<!-- BEGIN GENERATED: gen-repo-instructions (do not edit inside) -->
## Views — authentication & access control
- Patient/portal views that read per-user data MUST be decorated with `@login_required` (evidence: apps/core/views.py:25, apps/core/views.py:80, apps/core/views.py:114, apps/core/views.py:146).
- Public marketing/tool views (home, about, pricing, free tools, investment calculator) MUST stay undecorated and serve content to anonymous users (evidence: apps/core/views.py:7, apps/core/views.py:11, apps/core/views.py:15, apps/core/views.py:41).

## Views — model imports
- View functions MUST import `apps.core.models` classes lazily inside the function body (e.g. `from .models import DoctorVisit, LabTest`), not at module top level (evidence: apps/core/views.py:83, apps/core/views.py:117, apps/core/views.py:149, apps/core/views.py:169).

## Views — per-user query scoping
- Patient-facing views MUST scope querysets to the current user with `.filter(patient=request.user)` (bound as `user = request.user`) before returning records (evidence: apps/core/views.py:87, apps/core/views.py:120, apps/core/views.py:152).
- Subsequent GET filters (e.g. `status`, `category`, `type`) MUST be applied by chaining `.filter(...)` onto the already user-scoped queryset, defaulting to `"all"` to mean unfiltered (evidence: apps/core/views.py:122, apps/core/views.py:126, apps/core/views.py:154).

## Views — rendering & context
- Views MUST build an explicit context `dict` with stable string keys and return via `render(request, "<template>", context)` (evidence: apps/core/views.py:101, apps/core/views.py:111, apps/core/views.py:136, apps/core/views.py:202).
- To populate filter dropdowns from distinct column values, views SHOULD use `.values_list("<field>", flat=True).distinct()` on the user-scoped queryset (evidence: apps/core/views.py:130).

## Views — query performance
- Cross-patient list views SHOULD eager-load related rows with `.select_related(...)` for foreign keys and `.prefetch_related(...)` for reverse relations (evidence: apps/core/views.py:171).
- Explicit result ordering SHOULD be set with `.order_by(...)` on the queryset (e.g. `"-created_at"`, `"follow_up_date"`) (evidence: apps/core/views.py:97, apps/core/views.py:175).

## Models — structure & conventions
- Patient-owned models MUST relate to `django.contrib.auth.models.User` via a `ForeignKey` with an explicit `related_name` (evidence: apps/core/models.py:32, apps/core/models.py:66, apps/core/models.py:110).
- Status/type fields MUST be backed by a class-level `*_CHOICES` list of `(value, label)` tuples referenced from the field's `choices=` with a `default=` (evidence: apps/core/models.py:26, apps/core/models.py:40, apps/core/models.py:58, apps/core/models.py:72).
- Record models SHOULD declare a `class Meta` with `ordering` to set a default sort (evidence: apps/core/models.py:48, apps/core/models.py:90, apps/core/models.py:124).
- Every model MUST define a human-readable `__str__` returning an f-string summary (evidence: apps/core/models.py:19, apps/core/models.py:51, apps/core/models.py:93, apps/core/models.py:127).

## URLs
- URL patterns MUST use `path(...)` with a `name=` kwarg; patient portal routes MUST live under the `portal/` prefix (evidence: apps/core/urls.py:16, apps/core/urls.py:17, apps/core/urls.py:18).

## Admin
- Models MUST be registered with the `@admin.register(Model)` decorator on a `ModelAdmin` subclass (evidence: apps/core/admin.py:19, apps/core/admin.py:33, apps/core/admin.py:53, apps/core/admin.py:66).
- Each `ModelAdmin` SHOULD declare `list_display` and `search_fields` (using `__` lookups for related user fields), and SHOULD add `list_filter` where useful (evidence: apps/core/admin.py:21, apps/core/admin.py:22, apps/core/admin.py:43, apps/core/admin.py:77).
<!-- END GENERATED -->
