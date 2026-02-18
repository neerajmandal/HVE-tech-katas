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
