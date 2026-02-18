from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path

from .mapper import resolve_username_to_patient_ordinal
from .models import InvoiceSummary, LabResultSummary, PortalRecordBundle, VisitSummary
from .parser import (
    first_display,
    is_abnormal_observation,
    load_diagnostic_reports,
    load_encounters,
    load_observations,
    load_patients,
    observation_reference_range_text,
    observation_unit_text,
    observation_value_text,
    parse_fhir_date,
    reference_id,
)


class FilePortalRecordsRepository:
    def __init__(self, *, data_path: str | Path) -> None:
        self._data_path = Path(data_path)
        self._patients = load_patients(self._data_path)
        self._encounters = load_encounters(self._data_path)
        self._reports = load_diagnostic_reports(self._data_path)
        self._observations = load_observations(self._data_path)

        self._patient_ids_by_ordinal = [
            patient.id for patient in self._patients if getattr(patient, "id", None)
        ]
        self._observations_by_id = {
            observation.id: observation
            for observation in self._observations
            if getattr(observation, "id", None)
        }

    def get_dashboard_records(self, username: str) -> PortalRecordBundle:
        labs = tuple(self.get_lab_results(username))
        visits = tuple(self.get_visit_summaries(username))

        pending_labs = sum(
            1 for lab in labs if lab.status.lower() not in {"final", "completed"}
        )
        abnormal_labs = sum(1 for lab in labs if lab.is_abnormal)
        today = date.today()
        followups = tuple(
            visit
            for visit in visits
            if visit.follow_up_date is not None and visit.follow_up_date >= today
        )[:3]

        return PortalRecordBundle(
            recent_labs=labs[:5],
            total_labs=len(labs),
            pending_labs=pending_labs,
            abnormal_labs=abnormal_labs,
            recent_visits=visits[:5],
            total_visits=len(visits),
            upcoming_followups=followups,
        )

    def get_lab_results(
        self,
        username: str,
        *,
        status: str | None = None,
        category: str | None = None,
    ) -> Sequence[LabResultSummary]:
        patient_id = self._resolve_patient_id(username)
        if not patient_id:
            return ()

        normalized_status = (status or "").strip().lower()
        normalized_category = (category or "").strip().lower()
        lab_summaries: list[LabResultSummary] = []

        for report in self._reports:
            subject_reference = getattr(
                getattr(report, "subject", None), "reference", None
            )
            report_patient_id = reference_id(subject_reference, "Patient")
            if report_patient_id != patient_id:
                continue

            report_category = (
                first_display(getattr(report, "category", None)) or "Laboratory"
            )
            if normalized_category and normalized_category != report_category.lower():
                continue

            report_status = (getattr(report, "status", None) or "unknown").lower()
            if normalized_status and normalized_status != report_status:
                continue

            observations = self._resolve_report_observations(report)
            primary_observation = observations[0] if observations else None
            performer = first_display(getattr(report, "performer", None))
            effective_date = parse_fhir_date(getattr(report, "effectiveDateTime", None))
            issued_date = parse_fhir_date(getattr(report, "issued", None))

            lab_summaries.append(
                LabResultSummary(
                    id=report.id,
                    test_name=first_display([getattr(report, "code", None)])
                    or "Lab Test",
                    test_category=report_category,
                    status=report_status,
                    ordered_by=performer,
                    order_date=effective_date,
                    result_date=issued_date or effective_date,
                    result_value=(
                        observation_value_text(primary_observation)
                        if primary_observation is not None
                        else ""
                    ),
                    reference_range=(
                        observation_reference_range_text(primary_observation)
                        if primary_observation is not None
                        else ""
                    ),
                    unit=(
                        observation_unit_text(primary_observation)
                        if primary_observation is not None
                        else ""
                    ),
                    is_abnormal=any(
                        is_abnormal_observation(observation)
                        for observation in observations
                    ),
                )
            )

        lab_summaries.sort(
            key=lambda summary: (
                summary.result_date or summary.order_date or date.min,
                summary.id,
            ),
            reverse=True,
        )
        return tuple(lab_summaries)

    def get_lab_categories(self, username: str) -> Sequence[str]:
        categories = {
            summary.test_category
            for summary in self.get_lab_results(username)
            if summary.test_category
        }
        return tuple(sorted(categories))

    def get_visit_summaries(
        self,
        username: str,
        *,
        visit_type: str | None = None,
    ) -> Sequence[VisitSummary]:
        patient_id = self._resolve_patient_id(username)
        if not patient_id:
            return ()

        normalized_visit_type = (visit_type or "").strip().lower()
        visits: list[VisitSummary] = []

        for encounter in self._encounters:
            subject_reference = getattr(
                getattr(encounter, "subject", None), "reference", None
            )
            encounter_patient_id = reference_id(subject_reference, "Patient")
            if encounter_patient_id != patient_id:
                continue

            encounter_type = first_display(getattr(encounter, "type", None))
            if (
                normalized_visit_type
                and normalized_visit_type != encounter_type.lower()
            ):
                continue

            doctor_name = ""
            for participant in getattr(encounter, "participant", []) or []:
                doctor_name = getattr(
                    getattr(participant, "individual", None), "display", ""
                )
                if doctor_name:
                    break

            specialty = (
                getattr(getattr(encounter, "serviceProvider", None), "display", "")
                or "General Medicine"
            )
            reason = first_display(getattr(encounter, "reasonCode", None))
            location = first_display(getattr(encounter, "location", None))
            period_start = getattr(getattr(encounter, "period", None), "start", None)

            visits.append(
                VisitSummary(
                    id=encounter.id,
                    doctor_name=doctor_name or "Care Team",
                    specialty=specialty,
                    visit_date=parse_fhir_date(period_start),
                    visit_type=encounter_type or "visit",
                    reason=reason,
                    diagnosis=reason,
                    notes=location,
                )
            )

        visits.sort(
            key=lambda summary: (summary.visit_date or date.min, summary.id),
            reverse=True,
        )
        return tuple(visits)

    def get_invoices(
        self,
        username: str | None = None,
        *,
        status: str | None = None,
    ) -> Sequence[InvoiceSummary]:
        return ()

    def _resolve_patient_id(self, username: str) -> str | None:
        if not self._patient_ids_by_ordinal:
            return None

        mapping = resolve_username_to_patient_ordinal(
            username,
            dataset_size=len(self._patient_ids_by_ordinal),
        )
        index = mapping.mapped_ordinal - 1
        if index < 0 or index >= len(self._patient_ids_by_ordinal):
            return None

        return self._patient_ids_by_ordinal[index]

    def _resolve_report_observations(self, report: object) -> tuple[object, ...]:
        matched: list[object] = []
        for result in getattr(report, "result", []) or []:
            reference = getattr(result, "reference", None)
            observation_id = reference_id(reference, "Observation")
            if not observation_id:
                continue

            observation = self._observations_by_id.get(observation_id)
            if observation is not None:
                matched.append(observation)

        return tuple(matched)
