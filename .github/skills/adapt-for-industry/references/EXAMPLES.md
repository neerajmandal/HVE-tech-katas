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
  "visit":   {"singular": "Work Order", "plural": "Work Orders", "provider": "Technician", "specialty": "Discipline",
              "reason_label": "Work Requested", "diagnosis_label": "Findings", "plan_label": "Corrective Action"},
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

**Accent palette** (`theme`; amber primary + orange secondary)

```python
"theme": {
  "accent":  {"50": "#fffbeb", "100": "#fef3c7", "300": "#fcd34d", "400": "#fbbf24",
              "500": "#f59e0b", "600": "#d97706", "700": "#b45309", "900": "#78350f"},
  "accent2": {"400": "#fb923c", "500": "#f97316", "600": "#ea580c", "700": "#c2410c"},
  "avatar_bg": "d97706"}
```

**Public landing + welcome copy** (`home` block — re-skins `home.html` / `welcome.html`)

```python
"home": {
  "hero_badge": "Operations, Simplified",
  "hero_title_lead": "Your Equipment Health,",
  "hero_title_emphasis": "All in One Place",
  "hero_subtitle": "Track inspections, review work orders, and stay ahead of downtime. Stingray Operations Portal keeps you connected to your maintenance team.",
  "cta_authed": "Go to My Portal", "cta_guest": "Sign In to Your Portal", "cta_learn": "Learn More",
  "stat1_value": "10K+", "stat1_label": "Assets Tracked",
  "stat2_value": "50K+", "stat2_label": "Inspections Logged",
  "stat3_value": "99.9%", "stat3_label": "Uptime",
  "preview_record_title": "Vibration Analysis", "preview_record_category": "Mechanical", "preview_record_status": "In Spec",
  "preview_record_metric1_label": "RMS Velocity", "preview_record_metric1_value": "2.1 mm/s",
  "preview_record_metric2_label": "Bearing Temp", "preview_record_metric2_value": "Normal",
  "preview_record_footer": "Inspected by A. Reyes \u00b7 Jan 15, 2026",
  "preview_visit_title": "Line 3 - Conveyor", "preview_visit_subtitle": "Preventive Maintenance",
  "preview_pending_title": "Hydraulic Pressure Check", "preview_pending_subtitle": "Pending",
  "welcome_subtitle": "Your Stingray Operations Portal account has been created successfully.",
  "welcome_cta_title": "Access Your Work Orders",
  "welcome_cta_body": "View inspections, review work orders, and stay connected to your maintenance team.",
  "quicklink_records_desc": "View your inspections and history",
  "quicklink_visits_desc": "Review your work order history",
  "quicklink_about_desc": "Learn about Stingray Operations"}
```

> Every manifest must define a `home` block — it is the unauthenticated front door.
> Each template value is defaulted to its healthcare original, so omitting the block
> leaks "Your Health Records" / "Complete Blood Count" / "Patients Served" to
> first-time visitors. `ui_contract` enforces it.

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
  "visit":   {"singular": "Advisory Session", "plural": "Advisory Sessions", "provider": "Advisor", "specialty": "Practice",
              "reason_label": "Session Focus", "diagnosis_label": "Assessment", "plan_label": "Recommended Action"},
  "invoice": {"singular": "Statement", "plural": "Statements", "party": "Custodian"}},
"compliance": {"frameworks": ["SOX", "PCI-DSS", "KYC/AML", "SEC"],
  "note": "Synthetic demonstration data only. Not financial advice and not a system of record."}
```

**`visit_type` label re-skin**

```python
"checkup": "Portfolio Review", "follow_up": "Follow-up", "urgent": "Risk Alert Review",
"specialist": "Specialist Consult", "preventive": "Planning Session"
```

**Accent palette** (`theme`; indigo primary + violet secondary — institutional, "trust")

```python
"theme": {
  "accent":  {"50": "#eef2ff", "100": "#e0e7ff", "300": "#a5b4fc", "400": "#818cf8",
              "500": "#6366f1", "600": "#4f46e5", "700": "#4338ca", "900": "#312e81"},
  "accent2": {"400": "#a78bfa", "500": "#8b5cf6", "600": "#7c3aed", "700": "#6d28d9"},
  "avatar_bg": "4f46e5"}
```

**Calculators**: the existing Investment calculator already suits finance — extend
if the user wants (e.g. Retirement, Net Worth, Tax-Loss Harvest estimate).

---

## Accent palette quick reference

The accent is a per-industry brand color (see GENERATION_GUIDE "Per-industry
accent theming"). Suggested defaults — primary / secondary Tailwind families:

| Industry | accent (primary) | accent2 (secondary) | avatar_bg |
| --- | --- | --- | --- |
| Healthcare (baseline) | teal | cyan | `0d9488` |
| Finance / wealth | indigo | violet | `4f46e5` |
| Manufacturing | amber | orange | `d97706` |
| Legal | blue | sky | `2563eb` |
| Education | emerald | teal | `059669` |

Use the full Tailwind shade hexes for `{50,100,300,400,500,600,700,900}` (accent)
and `{400,500,600,700}` (accent2). Keep semantic status colors (red/amber/green/
purple) untouched.

---

## How to use a preset

1. Confirm the industry, slug, brand, and compliance with the user (offer the
   preset as a default).
2. Generate `apps/core/domain.py` and `apps/core/context_processors.py`, register
   the processor in `settings.py`, add the `domain_json` view/URL, and wire the
   templates (see `GENERATION_GUIDE.md`).
3. Hand calculators + seed data to `customize-use-case`, then validate and deploy.
