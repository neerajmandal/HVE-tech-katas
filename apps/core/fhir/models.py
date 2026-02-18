from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True, slots=True)
class LabResultSummary:
    id: str
    test_name: str
    test_category: str
    status: str
    ordered_by: str = ""
    order_date: date | None = None
    result_date: date | None = None
    result_value: str = ""
    reference_range: str = ""
    unit: str = ""
    is_abnormal: bool = False
    notes: str = ""


@dataclass(frozen=True, slots=True)
class VisitSummary:
    id: str
    doctor_name: str
    specialty: str
    visit_date: date | None
    visit_type: str
    reason: str = ""
    diagnosis: str = ""
    treatment_plan: str = ""
    follow_up_date: date | None = None
    vitals_bp: str = ""
    vitals_heart_rate: str = ""
    vitals_temperature: str = ""
    vitals_weight: str = ""
    notes: str = ""


@dataclass(frozen=True, slots=True)
class InvoiceSummary:
    id: str
    invoice_number: str
    status: str
    total: float
    issue_date: date | None = None
    due_date: date | None = None
    patient_username: str = ""


@dataclass(frozen=True, slots=True)
class PortalRecordBundle:
    recent_labs: tuple[LabResultSummary, ...] = field(default_factory=tuple)
    total_labs: int = 0
    pending_labs: int = 0
    abnormal_labs: int = 0
    recent_visits: tuple[VisitSummary, ...] = field(default_factory=tuple)
    total_visits: int = 0
    upcoming_followups: tuple[VisitSummary, ...] = field(default_factory=tuple)
    latest_vitals_bp: str = ""
    latest_vitals_heart_rate: str = ""
    latest_vitals_temperature: str = ""
    latest_vitals_weight: str = ""
    latest_vitals_bp_status: str = "unknown"
    latest_vitals_heart_rate_status: str = "unknown"
    latest_vitals_temperature_status: str = "unknown"
    latest_vitals_weight_status: str = "unknown"
    latest_vitals_bp_trend: str = "flat"
    latest_vitals_heart_rate_trend: str = "flat"
    latest_vitals_temperature_trend: str = "flat"
    latest_vitals_weight_trend: str = "flat"
