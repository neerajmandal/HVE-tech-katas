from __future__ import annotations

import pytest

from apps.core.fhir.mapper import resolve_username_to_patient_ordinal


@pytest.mark.parametrize("ordinal", range(1, 11))
def test_resolve_username_to_patient_ordinal_direct_mapping(ordinal: int) -> None:
    mapping = resolve_username_to_patient_ordinal(f"patient{ordinal}")

    assert mapping.username == f"patient{ordinal}"
    assert mapping.requested_ordinal == ordinal
    assert mapping.mapped_ordinal == ordinal
    assert mapping.used_fallback is False


@pytest.mark.parametrize("ordinal", range(11, 21))
def test_resolve_username_to_patient_ordinal_fallback_mapping(ordinal: int) -> None:
    mapping = resolve_username_to_patient_ordinal(f"patient{ordinal}")

    assert mapping.username == f"patient{ordinal}"
    assert mapping.requested_ordinal == ordinal
    assert mapping.mapped_ordinal == ((ordinal - 1) % 10) + 1
    assert mapping.used_fallback is True


def test_resolve_username_to_patient_ordinal_invalid_username_defaults_to_patient1() -> (
    None
):
    mapping = resolve_username_to_patient_ordinal("nurse-user")

    assert mapping.username == "nurse-user"
    assert mapping.requested_ordinal == 1
    assert mapping.mapped_ordinal == 1
    assert mapping.used_fallback is True
