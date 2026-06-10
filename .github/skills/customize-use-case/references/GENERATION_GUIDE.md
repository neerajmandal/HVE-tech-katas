# Generation Guide — customize-use-case

Worked templates for generating a vertical calculator and an entity-mapped seed
command (Django). Match the existing code style exactly; keep the function's
returned dict keys identical to the context keys the template reads.

## Calculator template (example: OEE)

### 1. `apps/core/services/finance.py`

Create the module if it does not exist. Model the function on the baseline
`calculate_compound_interest` stub: plain function, guarded divisions, returns a
dict the template reads.

```python
def calculate_oee(planned_minutes, downtime_minutes, ideal_cycle_time_sec,
                  total_units, good_units):
    """Overall Equipment Effectiveness. Returns a dict the template renders."""
    run_time = planned_minutes - downtime_minutes
    availability = run_time / planned_minutes if planned_minutes > 0 else 0.0
    performance = ((ideal_cycle_time_sec / 60 * total_units) / run_time
                   if run_time > 0 else 0.0)
    performance = min(performance, 1.0)
    quality = good_units / total_units if total_units > 0 else 0.0
    oee = availability * performance * quality
    rating = ("World Class" if oee >= 0.85
              else "Acceptable" if oee >= 0.60 else "Needs Improvement")
    a, p, q = round(availability * 100, 1), round(performance * 100, 1), round(quality * 100, 1)
    return {
        "availability_pct": a, "performance_pct": p, "quality_pct": q,
        "oee_pct": round(oee * 100, 1), "run_time_minutes": round(run_time, 1),
        "rating": rating,
        "breakdown": [
            {"label": "Availability", "value": a},
            {"label": "Performance", "value": p},
            {"label": "Quality", "value": q},
        ],
    }
```

### 2. `apps/core/views.py`

```python
import json
from .services.finance import calculate_oee


def oee_calculator(request):
    planned_minutes = 480.0
    downtime_minutes = 45.0
    ideal_cycle_time_sec = 30.0
    total_units = 800
    good_units = 760
    if request.method == "GET" and any(
        k in request.GET for k in ["planned", "downtime", "cycle", "total", "good"]
    ):
        try:
            planned_minutes = float(request.GET.get("planned", planned_minutes))
            downtime_minutes = float(request.GET.get("downtime", downtime_minutes))
            ideal_cycle_time_sec = float(request.GET.get("cycle", ideal_cycle_time_sec))
            total_units = int(request.GET.get("total", total_units))
            good_units = int(request.GET.get("good", good_units))
        except (ValueError, TypeError):
            pass
    results = calculate_oee(planned_minutes, downtime_minutes,
                            ideal_cycle_time_sec, total_units, good_units)
    context = {
        "planned_minutes": planned_minutes, "downtime_minutes": downtime_minutes,
        "ideal_cycle_time_sec": ideal_cycle_time_sec, "total_units": total_units,
        "good_units": good_units, **results,
        "breakdown_json": json.dumps(results["breakdown"]),
    }
    return render(request, "core/oee-calculator.html", context)
```

### 3. `apps/core/urls.py`

```python
path("free-tools/oee-calculator/", views.oee_calculator, name="oee_calculator"),
```

### 4. `templates/core/oee-calculator.html`

Follow `templates/core/investment-calculator.html`: a GET `<form>` whose input
`name=` attributes match the view's GET keys (`planned`, `downtime`, `cycle`,
`total`, `good`), then result panels reading the context keys
(`{{ oee_pct }}`, `{{ rating }}`, …). Feed any chart from `{{ breakdown_json }}`.

### 5. `templates/core/free-tools.html`

Add a card linking to the new page:

```django
<a href="{% url 'oee_calculator' %}" class="...">OEE Calculator</a>
```

> The validator's `calculators` check confirms `views.oee_calculator` exists and
> `calculate_oee` is defined in `services/finance.py` (or `views.py`).

## Seed command template

`apps/core/management/commands/seed_<slug>.py`
(run: `uv run python manage.py seed_<slug>`):

```python
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.core.models import (
    DoctorVisit, Invoice, InvoiceLineItem, LabTest, PatientProfile,
)

VISIT_TYPES = ["checkup", "follow_up", "urgent", "specialist", "preventive"]  # closed enum


class Command(BaseCommand):
    help = "Seeds the database with synthetic <industry> demo data"

    def handle(self, *args, **kwargs):
        # FK-safe idempotent reset of demo data
        InvoiceLineItem.objects.all().delete()
        Invoice.objects.all().delete()
        DoctorVisit.objects.all().delete()
        LabTest.objects.all().delete()
        PatientProfile.objects.all().delete()
        User.objects.filter(username__startswith="operator").delete()

        users = []
        for i in range(1, 9):
            u = User.objects.create_user(
                username=f"operator{i}", email=f"operator{i}@stingray-ops.example",
                password="password123", first_name="Op", last_name=f"{i}",  # pragma: allowlist secret
            )
            PatientProfile.objects.create(
                user=u, date_of_birth=date(1985, 1, 1), phone_number="555-0100",
                address="Plant A — Detroit",
                insurance_provider="Plant A — Detroit",     # generic: site
                insurance_policy_number=f"ASSET-{1000 + i}",  # generic: asset/badge id
            )
            users.append(u)

        for u in users:
            # lab_tests as inspection readings:
            LabTest.objects.create(
                patient=u, test_name="Vibration Analysis",
                test_category="Predictive Maintenance", ordered_by="Inspector R. Diaz",
                order_date=date.today(), result_date=date.today(), status="completed",
                result_value="1.8", reference_range="0.0-2.5", unit="mm/s",
                is_abnormal=False, notes="Within spec.",
            )
            # doctor_visits as work orders (vitals_* left null):
            DoctorVisit.objects.create(
                patient=u, doctor_name="Tech: J. Rivera", specialty="Mechanical",
                visit_date=date.today(), visit_type="preventive",
                reason="Replace bearing on conveyor C-12",
                treatment_plan="Swap SKF 6205; re-torque guard.",
                follow_up_date=date.today() + timedelta(days=90),
            )
            # invoices as purchase orders + line items (spare parts):
            inv = Invoice.objects.create(
                invoice_number=f"PO-{u.id:05d}", patient=u,
                due_date=date.today() + timedelta(days=30), status="pending",
                subtotal=420, tax=34, total=454, created_by=u,
            )
            InvoiceLineItem.objects.create(
                invoice=inv, description="SKF 6205 bearing", quantity=2,
                unit_price=120, total_price=240, service_date=date.today(),
                provider_name="Acme Industrial Supply",
            )

        self.stdout.write(self.style.SUCCESS(
            f"seeded: users={len(users)}, labs={LabTest.objects.count()}, "
            f"visits={DoctorVisit.objects.count()}, invoices={Invoice.objects.count()}"
        ))
```

Rules the `seed_contract` validator enforces:

- Only set **existing** model fields (no invented field names). FK aliases
  (`patient_id`, `user_id`, `invoice_id`, `created_by_id`) and `defaults=` are
  allowed.
- `visit_type` must be one of the five codes above.
- Create users with `User.objects.create_user(..., password="password123")` so <!-- pragma: allowlist secret -->
  demo logins work. The repo runs a `detect-secrets` pre-commit hook (`prek`) that
  flags the `password="..."` keyword form, so append `  # pragma: allowlist secret`
  to that line in the generated `seed_<slug>.py` (and to any doc example) or the
  commit/CI will fail.

## Keep bindings stable

- Calculator function dict keys == template context keys.
- Map vertical data onto existing model fields; don't rename fields.
- Re-skin display copy through the domain manifest (that's `adapt-for-industry`),
  not by hardcoding new strings in the calculator templates.
