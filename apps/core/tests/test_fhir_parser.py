from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient

from apps.core.fhir.parser import (
    _load_ndjson_resources,
    first_display,
    is_abnormal_observation,
    load_encounters,
    load_patients,
    model_validate_json_dict,
    observation_reference_range_text,
    observation_unit_text,
    observation_value_text,
    parse_fhir_date,
    reference_id,
)

_SAMPLE_DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "sample-bulk-fhir-datasets-10-patients"
)


def _observation_payload(**extra: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "resourceType": "Observation",
        "id": "obs-test",
        "status": "final",
        "code": {"text": "Test Observation"},
    }
    payload.update(extra)
    return payload


def _observation(**extra: object) -> Observation:
    return model_validate_json_dict(Observation, _observation_payload(**extra))


def test_load_patients_uses_local_sample_dataset() -> None:
    patients = load_patients(_SAMPLE_DATA_PATH)

    assert len(patients) >= 10
    assert all(patient.id for patient in patients)


def test_load_encounters_uses_local_sample_dataset() -> None:
    encounters = load_encounters(_SAMPLE_DATA_PATH)

    assert len(encounters) >= 10
    assert any(
        getattr(getattr(encounter, "subject", None), "reference", "")
        for encounter in encounters
    )


def test_load_ndjson_resources_skips_blank_and_invalid_lines(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "Patient.000.ndjson"
    ndjson_path.write_text(
        "\n".join(
            [
                json.dumps({"resourceType": "Patient", "id": "patient-a"}),
                "",
                "{invalid-json",
                json.dumps({"resourceType": "Patient", "id": "patient-b"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    patients = _load_ndjson_resources(ndjson_path, Patient)

    assert [patient.id for patient in patients] == ["patient-a", "patient-b"]


@pytest.mark.parametrize(
    ("reference", "expected_prefix", "expected"),
    [
        ("Patient/abc-123", "Patient", "abc-123"),
        ("Observation/obs-1", "Patient", None),
        ("Patient/", "Patient", None),
        (None, "Patient", None),
    ],
)
def test_reference_id_extracts_expected_identifier(
    reference: str | None,
    expected_prefix: str,
    expected: str | None,
) -> None:
    assert reference_id(reference, expected_prefix) == expected


def test_parse_fhir_date_handles_datetime_and_plain_date() -> None:
    assert parse_fhir_date("2025-01-31T23:59:00Z").isoformat() == "2025-01-31"
    assert parse_fhir_date("2025-02-01").isoformat() == "2025-02-01"
    assert parse_fhir_date("not-a-date") is None
    assert parse_fhir_date(None) is None


def test_first_display_prefers_text_then_coding_display_then_code() -> None:
    from_text = [SimpleNamespace(text="From text", coding=[])]
    from_display = [
        SimpleNamespace(text=None, coding=[SimpleNamespace(display="From display")])
    ]
    from_code = [
        SimpleNamespace(text=None, coding=[SimpleNamespace(display=None, code="X1")])
    ]

    assert first_display(from_text) == "From text"
    assert first_display(from_display) == "From display"
    assert first_display(from_code) == "X1"
    assert first_display([]) == ""


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        (
            {"valueQuantity": {"value": 56, "unit": "mg/dL", "code": "mg/dL"}},
            "56.00",
        ),
        ({"valueCodeableConcept": {"text": "Positive"}}, "Positive"),
        ({"valueCodeableConcept": {"coding": [{"display": "Detected"}]}}, "Detected"),
        ({"valueString": "Trace"}, "Trace"),
        ({"valueInteger": 7}, "7.00"),
        ({"valueBoolean": True}, "True"),
        ({}, ""),
    ],
)
def test_observation_value_text_polymorphic_extraction(
    extra: dict[str, object],
    expected: str,
) -> None:
    assert observation_value_text(_observation(**extra)) == expected


def test_observation_unit_text_handles_optional_fields() -> None:
    with_unit = _observation(
        valueQuantity={"value": 1.2, "unit": "mmol/L", "code": "mmol/L"}
    )
    with_code_only = _observation(valueQuantity={"value": 1.2, "code": "mg/L"})
    without_quantity = _observation()

    assert observation_unit_text(with_unit) == "mmol/L"
    assert observation_unit_text(with_code_only) == "mg/L"
    assert observation_unit_text(without_quantity) == ""


def test_observation_reference_range_text_handles_text_and_bounds() -> None:
    with_text = _observation(
        referenceRange=[
            {
                "text": "Normal: 4-8",
                "low": {"value": 4.0},
                "high": {"value": 8.0},
            }
        ]
    )
    with_bounds_only = _observation(
        referenceRange=[{"low": {"value": 3.5}, "high": {"value": 7.5}}]
    )
    with_high_only = _observation(referenceRange=[{"high": {"value": 10.0}}])
    without_ranges = _observation()

    assert observation_reference_range_text(with_text) == "Normal: 4-8"
    assert observation_reference_range_text(with_bounds_only) == "3.50-7.50"
    assert observation_reference_range_text(with_high_only) == "10.00"
    assert observation_reference_range_text(without_ranges) == ""


def test_is_abnormal_observation_recognizes_text_and_coding_flags() -> None:
    with_text_flag = _observation(interpretation=[{"text": "Abnormal"}])
    with_coding_flag = _observation(interpretation=[{"coding": [{"code": "H"}]}])
    normal = _observation(interpretation=[{"text": "Normal"}])
    missing = _observation()

    assert is_abnormal_observation(with_text_flag) is True
    assert is_abnormal_observation(with_coding_flag) is True
    assert is_abnormal_observation(normal) is False
    assert is_abnormal_observation(missing) is False
