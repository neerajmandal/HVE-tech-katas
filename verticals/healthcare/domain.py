"""Domain manifest — REFERENCE copy of the healthcare baseline.

This is the identity/baseline vertical the repository ships with. It is kept
here as a side-by-side reference so the two katas can be compared field-for-
field with ``verticals/manufacturing/domain.py``. On the healthcare baseline
the live app renders the same copy these values describe.

Like every vertical, this manifest re-skins brand, role, entity terminology,
page copy, nav labels, theme, and compliance context while preserving model
field names, dashboard context keys, URL names/paths, and the ``visit_type``
enum codes.
"""

DOMAIN = {
    "industry": "healthcare",
    "brand": {
        "name": "Stingray",
        "suffix": "Health Portal",
        "tagline": "Your health information at a glance",
    },
    "role_label": "Patient",
    "assistant_label": "Health AI",
    "nav": {
        "group": "My Health",
        "records": {"url_name": "lab_tests", "label": "Lab Tests"},
        "visits": {"url_name": "doctor_visits", "label": "Doctor Visits"},
    },
    "page_meta": {
        "patient_dashboard": {
            "title": "Patient Dashboard",
            "subtitle": "Your health overview at a glance",
        },
        "lab_tests": {
            "title": "Lab Tests",
            "subtitle": "Your lab results and test history",
        },
        "doctor_visits": {
            "title": "Doctor Visits",
            "subtitle": "Your appointments and visit details",
        },
    },
    "entities": {
        "record": {
            "singular": "Lab Test",
            "plural": "Lab Tests",
            "category": "Category",
            "abnormal": "Abnormal",
            "normal": "Normal",
            "pending": "Pending",
            "ordered_by": "Ordered by",
        },
        "visit": {
            "singular": "Doctor Visit",
            "plural": "Doctor Visits",
            "provider": "Doctor",
            "specialty": "Specialty",
            "reason_label": "Reason for Visit",
            "diagnosis_label": "Diagnosis",
            "plan_label": "Treatment Plan",
        },
        "invoice": {
            "singular": "Invoice",
            "plural": "Invoices",
            "party": "Provider",
        },
    },
    "dashboard": {
        "stats": {
            "total": "Total Lab Tests",
            "pending": "Pending Results",
            "abnormal": "Abnormal Results",
            "visits": "Doctor Visits",
        },
        "recent_records": "Recent Lab Tests",
        "recent_visits": "Recent Doctor Visits",
        "followups": "Upcoming Follow-ups",
        "followup_prefix": "Next visit for",
    },
    "invoices": {
        "title": "Billing Dashboard",
        "subtitle": "Manage your medical bills and payments",
    },
    "visit_type_labels": {
        "checkup": "Check-up",
        "follow_up": "Follow-up",
        "urgent": "Urgent Care",
        "specialist": "Specialist",
        "preventive": "Preventive Care",
    },
    "home": {
        "hero_badge": "Healthcare, Simplified",
        "hero_title_lead": "Your Health Records,",
        "hero_title_emphasis": "All in One Place",
        "hero_subtitle": "Track lab results, review visits, and stay on top of your care. Stingray Health Portal keeps you connected to your care team.",
        "cta_authed": "Go to My Portal",
        "cta_guest": "Sign In to Your Portal",
        "cta_learn": "Learn More",
        "stat1_value": "10K+",
        "stat1_label": "Patients Served",
        "stat2_value": "50K+",
        "stat2_label": "Lab Results Delivered",
        "stat3_value": "99.9%",
        "stat3_label": "Uptime",
        "preview_record_title": "Lipid Panel",
        "preview_record_category": "Chemistry",
        "preview_record_status": "Normal",
        "preview_record_metric1_label": "Total Cholesterol",
        "preview_record_metric1_value": "180 mg/dL",
        "preview_record_metric2_label": "HDL",
        "preview_record_metric2_value": "Normal",
        "preview_record_footer": "Ordered by Dr. A. Reyes \u00b7 Jan 15, 2026",
        "preview_visit_title": "Annual Physical",
        "preview_visit_subtitle": "Preventive Care",
        "preview_pending_title": "Thyroid Panel",
        "preview_pending_subtitle": "Pending",
        "welcome_subtitle": "Your Stingray Health Portal account has been created successfully.",
        "welcome_cta_title": "Access Your Health Records",
        "welcome_cta_body": "View lab results, review visits, and stay connected to your care team.",
        "quicklink_records_desc": "View your lab results and history",
        "quicklink_visits_desc": "Review your visit history",
        "quicklink_about_desc": "Learn about Stingray Health",
    },
    "compliance": {
        "frameworks": ["HIPAA", "HITECH", "ISO 27001", "FHIR"],
        "note": "Synthetic demonstration data only. Health records modeled on HIPAA / FHIR practices; not a system of record and not real patient data.",
    },
    "theme": {
        "accent": {
            "50": "#f0fdfa",
            "100": "#ccfbf1",
            "300": "#5eead4",
            "400": "#2dd4bf",
            "500": "#14b8a6",
            "600": "#0d9488",
            "700": "#0f766e",
            "900": "#134e4a",
        },
        "accent2": {
            "400": "#22d3ee",
            "500": "#06b6d4",
            "600": "#0891b2",
            "700": "#0e7490",
        },
        "avatar_bg": "0d9488",
    },
}
