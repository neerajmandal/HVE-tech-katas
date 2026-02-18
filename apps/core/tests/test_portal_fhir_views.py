from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date
from typing import Any

import pytest
from django.urls import reverse

from apps.core.fhir.mapper import resolve_username_to_patient_ordinal
from apps.core.fhir.models import LabResultSummary, PortalRecordBundle, VisitSummary


class _DeterministicPortalRepository:
    _dataset_size = 3

    def __init__(self) -> None:
        self._labs_by_patient = {
            1: (
                LabResultSummary(
                    id="lab-p1-1",
                    test_name="A1C",
                    test_category="Chemistry",
                    status="final",
                    result_value="5.9",
                ),
                LabResultSummary(
                    id="lab-p1-2",
                    test_name="CBC",
                    test_category="Hematology",
                    status="pending",
                    is_abnormal=True,
                ),
            ),
            2: (
                LabResultSummary(
                    id="lab-p2-1",
                    test_name="CMP",
                    test_category="Chemistry",
                    status="final",
                ),
            ),
            3: (),
        }
        self._visits_by_patient = {
            1: (
                VisitSummary(
                    id="visit-p1-1",
                    doctor_name="Dr. Deterministic",
                    specialty="Family Medicine",
                    visit_date=date(2025, 1, 10),
                    visit_type="checkup",
                    follow_up_date=date(2030, 1, 10),
                ),
            ),
            2: (
                VisitSummary(
                    id="visit-p2-1",
                    doctor_name="Dr. Repeatable",
                    specialty="Cardiology",
                    visit_date=date(2025, 2, 5),
                    visit_type="follow_up",
                ),
            ),
            3: (),
        }

    def _mapped_ordinal(self, username: str) -> int:
        return resolve_username_to_patient_ordinal(
            username,
            dataset_size=self._dataset_size,
        ).mapped_ordinal

    def get_dashboard_records(self, username: str) -> PortalRecordBundle:
        ordinal = self._mapped_ordinal(username)
        labs = self._labs_by_patient[ordinal]
        visits = self._visits_by_patient[ordinal]
        return PortalRecordBundle(
            recent_labs=labs[:5],
            total_labs=len(labs),
            pending_labs=sum(1 for lab in labs if lab.status != "final"),
            abnormal_labs=sum(1 for lab in labs if lab.is_abnormal),
            recent_visits=visits[:5],
            total_visits=len(visits),
            upcoming_followups=tuple(
                visit for visit in visits if visit.follow_up_date is not None
            )[:3],
        )

    def get_lab_results(
        self,
        username: str,
        *,
        status: str | None = None,
        category: str | None = None,
    ) -> Sequence[LabResultSummary]:
        ordinal = self._mapped_ordinal(username)
        labs = self._labs_by_patient[ordinal]
        if status:
            labs = tuple(lab for lab in labs if lab.status == status)
        if category:
            labs = tuple(lab for lab in labs if lab.test_category == category)
        return labs

    def get_lab_categories(self, username: str) -> Sequence[str]:
        ordinal = self._mapped_ordinal(username)
        return tuple(
            sorted(
                {
                    lab.test_category
                    for lab in self._labs_by_patient[ordinal]
                    if lab.test_category
                }
            )
        )

    def get_visit_summaries(
        self,
        username: str,
        *,
        visit_type: str | None = None,
    ) -> Sequence[VisitSummary]:
        ordinal = self._mapped_ordinal(username)
        visits = self._visits_by_patient[ordinal]
        if not visit_type:
            return visits
        return tuple(visit for visit in visits if visit.visit_type == visit_type)


@pytest.fixture
def deterministic_repository(monkeypatch: Any) -> _DeterministicPortalRepository:
    repository = _DeterministicPortalRepository()
    monkeypatch.setattr(
        "apps.core.views.get_portal_records_repository",
        lambda: repository,
    )
    return repository


@pytest.fixture
def login_as(client: Any, django_user_model: Any) -> Callable[[str], Any]:
    def _login(username: str) -> Any:
        user, _ = django_user_model.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        client.force_login(user)
        return user

    return _login


def _extract_ids(items: Iterable[object]) -> tuple[str, ...]:
    return tuple(str(getattr(item, "id", "")) for item in items)


def _dashboard_snapshot(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "recent_labs": _extract_ids(context["recent_labs"]),
        "total_labs": context["total_labs"],
        "pending_labs": context["pending_labs"],
        "abnormal_labs": context["abnormal_labs"],
        "recent_visits": _extract_ids(context["recent_visits"]),
        "total_visits": context["total_visits"],
        "upcoming_followups": _extract_ids(context["upcoming_followups"]),
    }


def _labs_snapshot(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "tests": _extract_ids(context["tests"]),
        "status_filter": context["status_filter"],
        "category_filter": context["category_filter"],
        "categories": tuple(context["categories"]),
    }


def _visits_snapshot(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "visits": _extract_ids(context["visits"]),
        "type_filter": context["type_filter"],
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url_name", "expected_keys"),
    [
        (
            "patient_dashboard",
            {
                "recent_labs",
                "total_labs",
                "pending_labs",
                "abnormal_labs",
                "recent_visits",
                "total_visits",
                "upcoming_followups",
            },
        ),
        (
            "lab_tests",
            {"tests", "status_filter", "category_filter", "categories"},
        ),
        ("doctor_visits", {"visits", "type_filter"}),
    ],
)
def test_portal_pages_expose_expected_context_contracts(
    deterministic_repository: _DeterministicPortalRepository,
    login_as: Callable[[str], Any],
    client: Any,
    url_name: str,
    expected_keys: set[str],
) -> None:
    login_as("patient1")

    response = client.get(reverse(url_name))

    assert response.status_code == 200
    assert response.context is not None
    for key in expected_keys:
        assert key in response.context


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url_name", "snapshot_builder"),
    [
        ("patient_dashboard", _dashboard_snapshot),
        ("lab_tests", _labs_snapshot),
        ("doctor_visits", _visits_snapshot),
    ],
)
def test_portal_pages_use_deterministic_fallback_mapping_for_unknown_usernames(
    deterministic_repository: _DeterministicPortalRepository,
    login_as: Callable[[str], Any],
    client: Any,
    url_name: str,
    snapshot_builder: Callable[[Mapping[str, Any]], dict[str, Any]],
) -> None:
    login_as("patient1")
    baseline_response = client.get(reverse(url_name))
    assert baseline_response.status_code == 200
    baseline_snapshot = snapshot_builder(baseline_response.context)

    login_as("patient4")
    wrapped_response = client.get(reverse(url_name))
    assert wrapped_response.status_code == 200
    wrapped_snapshot = snapshot_builder(wrapped_response.context)

    login_as("portal-user-without-patient-pattern")
    fallback_response = client.get(reverse(url_name))
    assert fallback_response.status_code == 200
    fallback_snapshot = snapshot_builder(fallback_response.context)

    assert wrapped_snapshot == baseline_snapshot
    assert fallback_snapshot == baseline_snapshot

    repeated_fallback_response = client.get(reverse(url_name))
    assert repeated_fallback_response.status_code == 200
    repeated_fallback_snapshot = snapshot_builder(repeated_fallback_response.context)
    assert repeated_fallback_snapshot == fallback_snapshot
