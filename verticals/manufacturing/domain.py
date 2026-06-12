"""Domain manifest — single source of truth for vertical display copy.

Industry adaptation: Manufacturing (plant operations). Re-skins brand, role,
entity terminology, page copy, nav labels, theme, and compliance context while
preserving model field names, dashboard context keys, URL names/paths, and the
``visit_type`` enum codes.
"""

DOMAIN = {
    "industry": "manufacturing",
    "brand": {
        "name": "Stingray",
        "suffix": "Operations Portal",
        "tagline": "Plant performance and asset reliability at a glance",
    },
    "role_label": "Operator",
    "assistant_label": "Maintenance AI",
    "nav": {
        "group": "Operations",
        "records": {"url_name": "lab_tests", "label": "Inspections"},
        "visits": {"url_name": "doctor_visits", "label": "Work Orders"},
    },
    "page_meta": {
        "patient_dashboard": {
            "title": "Operations Dashboard",
            "subtitle": "Your plant performance overview at a glance",
        },
        "lab_tests": {
            "title": "Inspections",
            "subtitle": "Equipment inspection readings",
        },
        "doctor_visits": {
            "title": "Work Orders",
            "subtitle": "Maintenance activity and work order details",
        },
    },
    "entities": {
        "record": {
            "singular": "Inspection",
            "plural": "Inspections",
            "category": "Discipline",
            "abnormal": "Out of Spec",
            "normal": "In Spec",
            "pending": "Pending",
            "ordered_by": "Inspector",
        },
        "visit": {
            "singular": "Work Order",
            "plural": "Work Orders",
            "provider": "Technician",
            "specialty": "Discipline",
            "reason_label": "Work Requested",
            "diagnosis_label": "Findings",
            "plan_label": "Corrective Action",
        },
        "invoice": {
            "singular": "Purchase Order",
            "plural": "Purchase Orders",
            "party": "Supplier",
        },
    },
    "dashboard": {
        "stats": {
            "total": "Total Inspections",
            "pending": "Pending Inspections",
            "abnormal": "Out of Spec",
            "visits": "Work Orders",
        },
        "recent_records": "Recent Inspections",
        "recent_visits": "Recent Work Orders",
        "followups": "Upcoming Scheduled Maintenance",
        "followup_prefix": "Next service for",
    },
    "invoices": {
        "title": "Procurement Dashboard",
        "subtitle": "Manage purchase orders and supplier billing",
    },
    "visit_type_labels": {
        "checkup": "Routine Inspection",
        "follow_up": "Re-inspection",
        "urgent": "Breakdown Repair",
        "specialist": "Specialist Service",
        "preventive": "Preventive Maintenance",
    },
    "home": {
        "hero_badge": "Operations, Simplified",
        "hero_title_lead": "Your Equipment Health,",
        "hero_title_emphasis": "All in One Place",
        "hero_subtitle": "Track inspections, review work orders, and stay ahead of downtime. Stingray Operations Portal keeps you connected to your maintenance team.",
        "cta_authed": "Go to My Portal",
        "cta_guest": "Sign In to Your Portal",
        "cta_learn": "Learn More",
        "stat1_value": "10K+",
        "stat1_label": "Assets Tracked",
        "stat2_value": "50K+",
        "stat2_label": "Inspections Logged",
        "stat3_value": "99.9%",
        "stat3_label": "Uptime",
        "preview_record_title": "Vibration Analysis",
        "preview_record_category": "Mechanical",
        "preview_record_status": "In Spec",
        "preview_record_metric1_label": "RMS Velocity",
        "preview_record_metric1_value": "2.1 mm/s",
        "preview_record_metric2_label": "Bearing Temp",
        "preview_record_metric2_value": "Normal",
        "preview_record_footer": "Inspected by A. Reyes \u00b7 Jan 15, 2026",
        "preview_visit_title": "Line 3 - Conveyor",
        "preview_visit_subtitle": "Preventive Maintenance",
        "preview_pending_title": "Hydraulic Pressure Check",
        "preview_pending_subtitle": "Pending",
        "welcome_subtitle": "Your Stingray Operations Portal account has been created successfully.",
        "welcome_cta_title": "Access Your Work Orders",
        "welcome_cta_body": "View inspections, review work orders, and stay connected to your maintenance team.",
        "quicklink_records_desc": "View your inspections and history",
        "quicklink_visits_desc": "Review your work order history",
        "quicklink_about_desc": "Learn about Stingray Operations",
    },
    "compliance": {
        "frameworks": ["ISO 9001", "OSHA", "ISO 27001", "ISO 55000"],
        "note": "Synthetic demonstration data only. Quality and safety records modeled on ISO 9001 / OSHA / ISO 55000 asset-management practices; not a system of record.",
    },
    "theme": {
        "accent": {
            "50": "#fffbeb",
            "100": "#fef3c7",
            "300": "#fcd34d",
            "400": "#fbbf24",
            "500": "#f59e0b",
            "600": "#d97706",
            "700": "#b45309",
            "900": "#78350f",
        },
        "accent2": {
            "400": "#fb923c",
            "500": "#f97316",
            "600": "#ea580c",
            "700": "#c2410c",
        },
        "avatar_bg": "d97706",
    },
}
