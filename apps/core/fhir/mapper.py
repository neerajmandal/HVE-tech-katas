from __future__ import annotations

import re
from dataclasses import dataclass

_USERNAME_PATTERN = re.compile(r"^patient(?P<ordinal>\d+)$", re.IGNORECASE)
_DEFAULT_DATASET_SIZE = 10


@dataclass(frozen=True, slots=True)
class UsernamePatientMapping:
    username: str
    requested_ordinal: int
    mapped_ordinal: int
    used_fallback: bool


def resolve_username_to_patient_ordinal(
    username: str,
    *,
    dataset_size: int = _DEFAULT_DATASET_SIZE,
) -> UsernamePatientMapping:
    normalized_dataset_size = (
        dataset_size if dataset_size > 0 else _DEFAULT_DATASET_SIZE
    )
    match = _USERNAME_PATTERN.match(username.strip())

    if not match:
        return UsernamePatientMapping(
            username=username,
            requested_ordinal=1,
            mapped_ordinal=1,
            used_fallback=True,
        )

    requested_ordinal = int(match.group("ordinal"))
    if requested_ordinal <= 0:
        return UsernamePatientMapping(
            username=username,
            requested_ordinal=requested_ordinal,
            mapped_ordinal=1,
            used_fallback=True,
        )

    if requested_ordinal <= normalized_dataset_size:
        return UsernamePatientMapping(
            username=username,
            requested_ordinal=requested_ordinal,
            mapped_ordinal=requested_ordinal,
            used_fallback=False,
        )

    mapped_ordinal = ((requested_ordinal - 1) % normalized_dataset_size) + 1
    return UsernamePatientMapping(
        username=username,
        requested_ordinal=requested_ordinal,
        mapped_ordinal=mapped_ordinal,
        used_fallback=True,
    )
