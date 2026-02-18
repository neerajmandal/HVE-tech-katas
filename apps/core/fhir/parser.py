from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path
from typing import TypeVar

from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.encounter import Encounter
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from pydantic import ValidationError

logger = logging.getLogger(__name__)

_TResource = TypeVar("_TResource")


def load_patients(data_path: Path) -> list[Patient]:
    return _load_ndjson_resources(data_path / "Patient.000.ndjson", Patient)


def load_encounters(data_path: Path) -> list[Encounter]:
    return _load_ndjson_resources(data_path / "Encounter.000.ndjson", Encounter)


def load_diagnostic_reports(data_path: Path) -> list[DiagnosticReport]:
    return _load_ndjson_resources(
        data_path / "DiagnosticReport.000.ndjson", DiagnosticReport
    )


def load_observations(data_path: Path) -> list[Observation]:
    return _load_ndjson_resources(data_path / "Observation.000.ndjson", Observation)


def _load_ndjson_resources(
    file_path: Path, resource_type: type[_TResource]
) -> list[_TResource]:
    resources: list[_TResource] = []

    if not file_path.exists():
        logger.warning("FHIR source file does not exist: %s", file_path)
        return resources

    with file_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            payload = line.strip()
            if not payload:
                continue

            try:
                resource = resource_type.model_validate_json(payload)
            except ValidationError as error:
                logger.warning(
                    "Skipping invalid %s at %s:%s (%s)",
                    resource_type.__name__,
                    file_path,
                    line_number,
                    error,
                )
                continue

            resources.append(resource)

    return resources


def reference_id(reference: str | None, expected_prefix: str) -> str | None:
    if not reference:
        return None

    token = f"{expected_prefix}/"
    if token not in reference:
        return None

    _, suffix = reference.split(token, maxsplit=1)
    return suffix or None


def parse_fhir_date(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            logger.debug("Unable to parse FHIR date value: %s", value)
            return None


def first_display(items: Iterable[object] | None) -> str:
    if not items:
        return ""

    for item in items:
        text_value = getattr(item, "text", None)
        if text_value:
            return str(text_value)

        for coding in getattr(item, "coding", []) or []:
            display = getattr(coding, "display", None)
            if display:
                return str(display)

            code = getattr(coding, "code", None)
            if code:
                return str(code)

    return ""


def observation_value_text(observation: Observation) -> str:
    value_quantity = getattr(observation, "valueQuantity", None)
    if value_quantity is not None:
        quantity_value = getattr(value_quantity, "value", None)
        if quantity_value is not None:
            return str(quantity_value)

    value_codeable_concept = getattr(observation, "valueCodeableConcept", None)
    if value_codeable_concept is not None:
        text = getattr(value_codeable_concept, "text", None)
        if text:
            return str(text)

        for coding in getattr(value_codeable_concept, "coding", []) or []:
            display = getattr(coding, "display", None)
            if display:
                return str(display)

    direct_fields = (
        "valueString",
        "valueInteger",
        "valueBoolean",
        "valueDateTime",
        "valueDate",
        "valueTime",
    )
    for field_name in direct_fields:
        value = getattr(observation, field_name, None)
        if value is not None:
            return str(value)

    return ""


def observation_unit_text(observation: Observation) -> str:
    value_quantity = getattr(observation, "valueQuantity", None)
    if value_quantity is None:
        return ""

    unit = getattr(value_quantity, "unit", None)
    if unit:
        return str(unit)

    code = getattr(value_quantity, "code", None)
    if code:
        return str(code)

    return ""


def observation_reference_range_text(observation: Observation) -> str:
    ranges = getattr(observation, "referenceRange", None)
    if not ranges:
        return ""

    first_range = ranges[0]
    text = getattr(first_range, "text", None)
    if text:
        return str(text)

    low = getattr(first_range, "low", None)
    high = getattr(first_range, "high", None)
    low_value = getattr(low, "value", None) if low else None
    high_value = getattr(high, "value", None) if high else None
    if low_value is not None or high_value is not None:
        low_part = "" if low_value is None else str(low_value)
        high_part = "" if high_value is None else str(high_value)
        return f"{low_part}-{high_part}".strip("-")

    return ""


def is_abnormal_observation(observation: Observation) -> bool:
    for interpretation in getattr(observation, "interpretation", []) or []:
        text = (getattr(interpretation, "text", "") or "").upper()
        if text in {"ABNORMAL", "HIGH", "LOW"}:
            return True

        for coding in getattr(interpretation, "coding", []) or []:
            code = (getattr(coding, "code", "") or "").upper()
            if code in {"A", "H", "HH", "L", "LL"}:
                return True

    return False


def model_validate_json_dict(
    resource_type: type[_TResource], payload: dict[str, object]
) -> _TResource:
    return resource_type.model_validate_json(json.dumps(payload))
