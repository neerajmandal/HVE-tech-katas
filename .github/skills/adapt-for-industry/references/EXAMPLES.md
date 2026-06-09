# Industry Presets — adapt-for-industry

These are **example presets** to seed a conversation, not files to copy verbatim.
The skill is industry-agnostic; confirm the slugs and copy with the user, then
generate the manifest. Each preset reuses the existing six tables (no field
renames) and keeps the five `visit_type` codes.

---

## Preset A — Manufacturing (plant operations)

**Entity mapping**

| Model | Manufacturing meaning |
| --- | --- |
| `User` | Plant operators (operator1..N) |
| `PatientProfile` | Operator/site profile; `insurance_provider`→"Plant / Site", `insurance_policy_number`→"Asset/Badge ID" |
| `LabTest` | Equipment **inspection readings** (Vibration Analysis, Thermal Imaging, Lubricant Analysis…); `test_category`→Discipline; `is_abnormal`→Out of Spec |
| `DoctorVisit` | Maintenance **work orders**; `doctor_name`→Technician; `specialty`→Discipline (Mechanical/Electrical/Controls) |
| `Invoice` | **Purchase orders** for spare parts; line items = parts (bearings, seals, PLC modules) |

**Manifest highlights**

```python
"brand": {"name": "Stingray", "suffix": "Operations Portal",
          "tagline": "Plant performance and asset reliability at a glance"},
"role_label": "Operator",
"assistant_label": "Maintenance AI",
"nav": {"group": "Operations",
        "records": {"url_name": "lab_tests", "label": "Inspections"},
        "visits":  {"url_name": "doctor_visits", "label": "Work Orders"}},
"entities": {
  "record":  {"singular": "Inspection", "plural": "Inspections", "category": "Discipline",
              "abnormal": "Out of Spec", "normal": "In Spec", "pending": "Pending", "ordered_by": "Inspector"},
  "visit":   {"singular": "Work Order", "plural": "Work Orders", "provider": "Technician", "specialty": "Discipline"},
  "invoice": {"singular": "Purchase Order", "plural": "Purchase Orders", "party": "Supplier"}},
"dashboard": {"stats": {"total": "Total Inspections", "pending": "Pending Inspections",
              "abnormal": "Out of Spec", "visits": "Work Orders"},
              "recent_records": "Recent Inspections", "recent_visits": "Recent Work Orders",
              "followups": "Upcoming Scheduled Maintenance", "followup_prefix": "Next service for"},
"invoices": {"title": "Procurement Dashboard", "subtitle": "Manage purchase orders and supplier billing"},
"compliance": {"frameworks": ["ISO 9001", "OSHA", "ISO 27001", "ISO 55000"],
  "note": "Synthetic demonstration data only. Quality and safety records modeled on ISO 9001 / OSHA / ISO 55000 asset-management practices; not a system of record."}
```

**`visit_type` label re-skin** (manifest `visit_type_labels`; codes unchanged)

```python
"checkup": "Routine Inspection", "follow_up": "Re-inspection", "urgent": "Breakdown Repair",
"specialist": "Specialist Service", "preventive": "Preventive Maintenance"
```

**Calculators** (for `customize-use-case`): OEE, Downtime Cost, Maintenance ROI.

---

## Preset B — Financial services (wealth/advisory)

**Entity mapping**

| Model | Finance meaning |
| --- | --- |
| `User` | Clients |
| `PatientProfile` | Client profile; `insurance_provider`→"Custodian", `insurance_policy_number`→"Account #" |
| `LabTest` | Portfolio/risk **metric readings** (Sharpe Ratio, Expense Ratio, Concentration, Liquidity); `is_abnormal`→Out of Policy |
| `DoctorVisit` | **Advisory sessions**; `doctor_name`→Advisor; `specialty`→Practice (Retirement/Tax/Estate) |
| `Invoice` | **Account statements**; line items = fees (advisory fee, fund expense, transaction) |

**Manifest highlights**

```python
"brand": {"name": "Stingray", "suffix": "Wealth Portal",
          "tagline": "Portfolio health and advisory at a glance"},
"role_label": "Client",
"assistant_label": "Advisor AI",
"nav": {"group": "Portfolio",
        "records": {"url_name": "lab_tests", "label": "Metrics"},
        "visits":  {"url_name": "doctor_visits", "label": "Advisory Sessions"}},
"entities": {
  "record":  {"singular": "Metric", "plural": "Metrics", "category": "Category",
              "abnormal": "Out of Policy", "normal": "In Policy", "pending": "Pending", "ordered_by": "Analyst"},
  "visit":   {"singular": "Advisory Session", "plural": "Advisory Sessions", "provider": "Advisor", "specialty": "Practice"},
  "invoice": {"singular": "Statement", "plural": "Statements", "party": "Custodian"}},
"compliance": {"frameworks": ["SOX", "PCI-DSS", "KYC/AML", "SEC"],
  "note": "Synthetic demonstration data only. Not financial advice and not a system of record."}
```

**`visit_type` label re-skin**

```python
"checkup": "Portfolio Review", "follow_up": "Follow-up", "urgent": "Risk Alert Review",
"specialist": "Specialist Consult", "preventive": "Planning Session"
```

**Calculators**: the existing Investment calculator already suits finance — extend
if the user wants (e.g. Retirement, Net Worth, Tax-Loss Harvest estimate).

---

## How to use a preset

1. Confirm the industry, slug, brand, and compliance with the user (offer the
   preset as a default).
2. Generate `apps/core/domain.py` and `apps/core/context_processors.py`, register
   the processor in `settings.py`, add the `domain_json` view/URL, and wire the
   templates (see `GENERATION_GUIDE.md`).
3. Hand calculators + seed data to `customize-use-case`, then validate and deploy.
