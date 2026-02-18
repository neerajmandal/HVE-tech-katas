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
        self._observations_by_patient: dict[str, list[object]] = {}
        for observation in self._observations:
            subject_reference = getattr(
                getattr(observation, "subject", None), "reference", None
            )
            patient_id = reference_id(subject_reference, "Patient")
            if patient_id:
                self._observations_by_patient.setdefault(patient_id, []).append(
                    observation
                )

    def get_dashboard_records(self, username: str) -> PortalRecordBundle:
        patient_id = self._resolve_patient_id(username)
        labs = tuple(self.get_lab_results(username))
        visits = tuple(self.get_visit_summaries(username))
        latest_vitals = self._resolve_latest_vitals(patient_id)

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
            latest_vitals_bp=latest_vitals["bp"]["value"],
            latest_vitals_heart_rate=latest_vitals["heart_rate"]["value"],
            latest_vitals_temperature=latest_vitals["temperature"]["value"],
            latest_vitals_weight=latest_vitals["weight"]["value"],
            latest_vitals_bp_status=latest_vitals["bp"]["status"],
            latest_vitals_heart_rate_status=latest_vitals["heart_rate"]["status"],
            latest_vitals_temperature_status=latest_vitals["temperature"]["status"],
            latest_vitals_weight_status=latest_vitals["weight"]["status"],
            latest_vitals_bp_trend=latest_vitals["bp"]["trend"],
            latest_vitals_heart_rate_trend=latest_vitals["heart_rate"]["trend"],
            latest_vitals_temperature_trend=latest_vitals["temperature"]["trend"],
            latest_vitals_weight_trend=latest_vitals["weight"]["trend"],
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

            report_name = first_display([getattr(report, "code", None)]) or "Lab Test"
            if "history and physical note" in report_name.lower():
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
                    test_name=report_name,
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
            visit_date = parse_fhir_date(period_start)
            visit_vitals = self._resolve_visit_vitals(
                patient_id,
                visit_date=visit_date,
                encounter_id=getattr(encounter, "id", ""),
            )

            visits.append(
                VisitSummary(
                    id=encounter.id,
                    doctor_name=doctor_name or "Care Team",
                    specialty=specialty,
                    visit_date=visit_date,
                    visit_type=encounter_type or "visit",
                    reason=reason,
                    diagnosis=reason,
                    vitals_bp=visit_vitals["bp"],
                    vitals_heart_rate=visit_vitals["heart_rate"],
                    vitals_temperature=visit_vitals["temperature"],
                    vitals_weight=visit_vitals["weight"],
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

    def _resolve_latest_vitals(
        self, patient_id: str | None
    ) -> dict[str, dict[str, str]]:
        empty = {
            "bp": {"value": "", "status": "unknown", "trend": "flat"},
            "heart_rate": {"value": "", "status": "unknown", "trend": "flat"},
            "temperature": {"value": "", "status": "unknown", "trend": "flat"},
            "weight": {"value": "", "status": "unknown", "trend": "flat"},
        }
        if not patient_id:
            return empty

        observations = self._observations_by_patient.get(patient_id, [])
        series: dict[str, list[tuple[date, str, float | None]]] = {
            "bp": [],
            "heart_rate": [],
            "temperature": [],
            "weight": [],
        }

        for observation in observations:
            vital_type = self._classify_vital_type(observation)
            if not vital_type:
                continue

            vital_value = self._vital_value_text(observation, vital_type)
            if not vital_value:
                continue

            observed_on = self._observation_date(observation) or date.min
            metric = self._vital_metric(vital_type, vital_value)
            series[vital_type].append((observed_on, vital_value, metric))

        resolved = dict(empty)
        for vital_type, readings in series.items():
            if not readings:
                continue

            readings.sort(key=lambda reading: reading[0])
            _, latest_value, latest_metric = readings[-1]
            previous_metric = readings[-2][2] if len(readings) > 1 else None
            resolved[vital_type] = {
                "value": latest_value,
                "status": self._vital_status(vital_type, latest_value, latest_metric),
                "trend": self._vital_trend(vital_type, latest_metric, previous_metric),
            }

        return resolved

    def _resolve_visit_vitals(
        self,
        patient_id: str,
        *,
        visit_date: date | None,
        encounter_id: str,
    ) -> dict[str, str]:
        empty = {"bp": "", "heart_rate": "", "temperature": "", "weight": ""}
        observations = self._observations_by_patient.get(patient_id, [])
        if not observations:
            return empty

        matched = dict(empty)

        encounter_observations = [
            observation
            for observation in observations
            if encounter_id
            and self._observation_encounter_id(observation) == encounter_id
        ]
        matched.update(self._pick_vitals_from_observations(encounter_observations))

        if visit_date is None:
            return matched

        remaining_types = [key for key, value in matched.items() if not value]
        if not remaining_types:
            return matched

        same_day_observations = [
            observation
            for observation in observations
            if self._observation_date(observation) == visit_date
        ]
        same_day_values = self._pick_vitals_from_observations(same_day_observations)
        for vital_type in remaining_types:
            matched[vital_type] = same_day_values.get(vital_type, "")

        return matched

    def _pick_vitals_from_observations(
        self,
        observations: Sequence[object],
    ) -> dict[str, str]:
        values = {"bp": "", "heart_rate": "", "temperature": "", "weight": ""}
        dates: dict[str, date | None] = {key: None for key in values}

        for observation in observations:
            vital_type = self._classify_vital_type(observation)
            if not vital_type:
                continue

            vital_value = self._vital_value_text(observation, vital_type)
            if not vital_value:
                continue

            observed_on = self._observation_date(observation)
            current_date = dates[vital_type]
            if current_date is None or (
                observed_on is not None and observed_on >= current_date
            ):
                dates[vital_type] = observed_on
                values[vital_type] = vital_value

        return values

    def _classify_vital_type(self, observation: object) -> str:
        codeable = getattr(observation, "code", None)
        text = (getattr(codeable, "text", "") or "").lower()
        code_values = {
            (getattr(coding, "code", "") or "").lower()
            for coding in getattr(codeable, "coding", []) or []
        }
        display_values = {
            (getattr(coding, "display", "") or "").lower()
            for coding in getattr(codeable, "coding", []) or []
        }

        if "85354-9" in code_values or "blood pressure" in text:
            return "bp"

        if "8867-4" in code_values or "heart rate" in text:
            return "heart_rate"

        if "8310-5" in code_values or "temperature" in text:
            return "temperature"

        if "29463-7" in code_values or "body weight" in text:
            return "weight"

        if any("heart rate" in display for display in display_values):
            return "heart_rate"
        if any("temperature" in display for display in display_values):
            return "temperature"
        if any("body weight" in display for display in display_values):
            return "weight"

        return ""

    def _vital_value_text(self, observation: object, vital_type: str) -> str:
        if vital_type == "bp":
            systolic = ""
            diastolic = ""
            for component in getattr(observation, "component", []) or []:
                component_code = getattr(component, "code", None)
                component_codes = {
                    (getattr(coding, "code", "") or "").lower()
                    for coding in getattr(component_code, "coding", []) or []
                }
                quantity = getattr(component, "valueQuantity", None)
                value = getattr(quantity, "value", None) if quantity else None
                if value is None:
                    continue

                value_text = str(value)
                if value_text.endswith(".0"):
                    value_text = value_text[:-2]

                if "8480-6" in component_codes:
                    systolic = value_text
                if "8462-4" in component_codes:
                    diastolic = value_text

            if systolic and diastolic:
                return f"{systolic}/{diastolic}"

        return observation_value_text(observation)

    def _observation_date(self, observation: object) -> date | None:
        effective_date = parse_fhir_date(
            getattr(observation, "effectiveDateTime", None)
        )
        if effective_date is not None:
            return effective_date

        effective_period = getattr(observation, "effectivePeriod", None)
        period_start = (
            getattr(effective_period, "start", None) if effective_period else None
        )
        period_date = parse_fhir_date(period_start)
        if period_date is not None:
            return period_date

        return parse_fhir_date(getattr(observation, "issued", None))

    def _observation_encounter_id(self, observation: object) -> str:
        encounter_reference = getattr(
            getattr(observation, "encounter", None), "reference", ""
        )
        return reference_id(encounter_reference, "Encounter") or ""

    def _vital_metric(self, vital_type: str, vital_value: str) -> float | None:
        if not vital_value:
            return None

        if vital_type == "bp":
            systolic, diastolic = self._parse_bp(vital_value)
            if systolic is None or diastolic is None:
                return None
            return (systolic + diastolic) / 2

        try:
            return float(vital_value)
        except ValueError:
            return None

    def _vital_status(
        self,
        vital_type: str,
        vital_value: str,
        metric: float | None,
    ) -> str:
        if not vital_value:
            return "unknown"

        if vital_type == "bp":
            systolic, diastolic = self._parse_bp(vital_value)
            if systolic is None or diastolic is None:
                return "unknown"
            if systolic < 90 or diastolic < 60:
                return "low"
            if systolic > 120 or diastolic > 80:
                return "high"
            return "normal"

        if metric is None:
            return "unknown"

        if vital_type == "heart_rate":
            if metric < 60:
                return "low"
            if metric > 100:
                return "high"
            return "normal"

        if vital_type == "temperature":
            if metric < 97.0:
                return "low"
            if metric > 99.5:
                return "high"
            return "normal"

        if vital_type == "weight":
            if metric < 100:
                return "low"
            if metric > 250:
                return "high"
            return "normal"

        return "unknown"

    def _vital_trend(
        self,
        vital_type: str,
        latest_metric: float | None,
        previous_metric: float | None,
    ) -> str:
        if latest_metric is None or previous_metric is None:
            return "flat"

        threshold = {
            "bp": 1.0,
            "heart_rate": 1.0,
            "temperature": 0.2,
            "weight": 0.5,
        }.get(vital_type, 0.1)
        delta = latest_metric - previous_metric
        if delta > threshold:
            return "up"
        if delta < -threshold:
            return "down"
        return "flat"

    def _parse_bp(self, value: str) -> tuple[float | None, float | None]:
        if "/" not in value:
            return None, None

        systolic_raw, diastolic_raw = value.split("/", maxsplit=1)
        try:
            return float(systolic_raw), float(diastolic_raw)
        except ValueError:
            return None, None
