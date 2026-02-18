from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from apps.core.fhir.file_repository import FilePortalRecordsRepository


def _codeable(text: str) -> SimpleNamespace:
    return SimpleNamespace(text=text, coding=[])


def _vital_observation(
    *,
    code: str,
    display: str,
    value: object,
    effective: str,
    encounter_id: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=f"obs-{code}-{encounter_id}",
        subject=SimpleNamespace(reference="Patient/patient-1"),
        encounter=SimpleNamespace(reference=f"Encounter/{encounter_id}"),
        effectiveDateTime=effective,
        code=SimpleNamespace(
            text=display,
            coding=[SimpleNamespace(code=code, display=display)],
        ),
        valueQuantity=SimpleNamespace(value=value, unit=""),
        component=[],
    )


def _bp_observation(
    *,
    systolic: int,
    diastolic: int,
    effective: str,
    encounter_id: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=f"obs-bp-{encounter_id}",
        subject=SimpleNamespace(reference="Patient/patient-1"),
        encounter=SimpleNamespace(reference=f"Encounter/{encounter_id}"),
        effectiveDateTime=effective,
        code=SimpleNamespace(
            text="Blood pressure",
            coding=[SimpleNamespace(code="85354-9", display="Blood pressure")],
        ),
        component=[
            SimpleNamespace(
                code=SimpleNamespace(
                    coding=[SimpleNamespace(code="8480-6", display="Systolic")]
                ),
                valueQuantity=SimpleNamespace(value=systolic),
            ),
            SimpleNamespace(
                code=SimpleNamespace(
                    coding=[SimpleNamespace(code="8462-4", display="Diastolic")]
                ),
                valueQuantity=SimpleNamespace(value=diastolic),
            ),
        ],
    )


def test_history_and_physical_notes_classified_as_visits_not_labs(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_patients",
        lambda _path: [SimpleNamespace(id="patient-1")],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_encounters",
        lambda _path: [],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_observations",
        lambda _path: [],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_diagnostic_reports",
        lambda _path: [
            SimpleNamespace(
                id="report-hp",
                subject=SimpleNamespace(reference="Patient/patient-1"),
                code=_codeable("History and physical note"),
                category=[_codeable("Clinical")],
                status="final",
                result=[],
                performer=[SimpleNamespace(display="Dr. Note")],
                effectiveDateTime="2025-01-01T00:00:00Z",
                issued="2025-01-01T00:00:00Z",
                encounter=SimpleNamespace(reference="Encounter/e-hp"),
            ),
            SimpleNamespace(
                id="report-lab",
                subject=SimpleNamespace(reference="Patient/patient-1"),
                code=_codeable("Hemoglobin A1c"),
                category=[_codeable("Laboratory")],
                status="final",
                result=[],
                performer=[SimpleNamespace(display="Dr. Lab")],
                effectiveDateTime="2025-01-02T00:00:00Z",
                issued="2025-01-02T00:00:00Z",
                encounter=SimpleNamespace(reference="Encounter/e-lab"),
            ),
        ],
    )

    repository = FilePortalRecordsRepository(data_path="/tmp/unused")

    lab_ids = [summary.id for summary in repository.get_lab_results("patient1")]
    visit_ids = [summary.id for summary in repository.get_visit_summaries("patient1")]

    assert lab_ids == ["report-lab"]
    assert "report-hp" not in visit_ids


def test_dashboard_uses_latest_vitals_and_visit_uses_encounter_vitals(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_patients",
        lambda _path: [SimpleNamespace(id="patient-1")],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_diagnostic_reports",
        lambda _path: [],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_encounters",
        lambda _path: [
            SimpleNamespace(
                id="enc-1",
                subject=SimpleNamespace(reference="Patient/patient-1"),
                type=[SimpleNamespace(text="checkup", coding=[])],
                participant=[
                    SimpleNamespace(individual=SimpleNamespace(display="Dr. Visit"))
                ],
                serviceProvider=SimpleNamespace(display="Primary Care"),
                reasonCode=[SimpleNamespace(text="Routine follow-up", coding=[])],
                location=[SimpleNamespace(text="Clinic A", coding=[])],
                period=SimpleNamespace(start="2025-01-10T09:00:00Z"),
            )
        ],
    )
    monkeypatch.setattr(
        "apps.core.fhir.file_repository.load_observations",
        lambda _path: [
            _bp_observation(
                systolic=120,
                diastolic=80,
                effective="2025-01-10T08:30:00Z",
                encounter_id="enc-1",
            ),
            _vital_observation(
                code="8867-4",
                display="Heart rate",
                value=70,
                effective="2025-01-08T08:35:00Z",
                encounter_id="enc-0",
            ),
            _vital_observation(
                code="8867-4",
                display="Heart rate",
                value=72,
                effective="2025-01-10T08:35:00Z",
                encounter_id="enc-1",
            ),
            _vital_observation(
                code="29463-7",
                display="Body weight",
                value=178,
                effective="2025-01-08T08:45:00Z",
                encounter_id="enc-0",
            ),
            _vital_observation(
                code="29463-7",
                display="Body weight",
                value=180,
                effective="2025-01-10T08:45:00Z",
                encounter_id="enc-1",
            ),
            _vital_observation(
                code="8310-5",
                display="Body temperature",
                value=98.2,
                effective="2025-01-08T08:45:00Z",
                encounter_id="enc-0",
            ),
            _vital_observation(
                code="8310-5",
                display="Body temperature",
                value=98.6,
                effective="2025-01-15T08:45:00Z",
                encounter_id="enc-2",
            ),
        ],
    )

    repository = FilePortalRecordsRepository(data_path="/tmp/unused")

    bundle = repository.get_dashboard_records("patient1")
    visits = repository.get_visit_summaries("patient1")

    assert bundle.latest_vitals_bp == "120/80"
    assert bundle.latest_vitals_heart_rate == "72.00"
    assert bundle.latest_vitals_temperature == "98.60"
    assert bundle.latest_vitals_weight == "180.00"
    assert bundle.latest_vitals_bp_status == "normal"
    assert bundle.latest_vitals_heart_rate_status == "normal"
    assert bundle.latest_vitals_temperature_status == "normal"
    assert bundle.latest_vitals_weight_status == "normal"
    assert bundle.latest_vitals_bp_trend == "flat"
    assert bundle.latest_vitals_heart_rate_trend == "up"
    assert bundle.latest_vitals_temperature_trend == "up"
    assert bundle.latest_vitals_weight_trend == "up"

    assert len(visits) == 1
    visit = visits[0]
    assert visit.vitals_bp == "120/80"
    assert visit.vitals_heart_rate == "72.00"
    assert visit.vitals_temperature == ""
    assert visit.vitals_weight == "180.00"
