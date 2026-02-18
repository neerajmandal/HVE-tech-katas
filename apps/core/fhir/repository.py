from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from django.conf import settings

from .file_repository import FilePortalRecordsRepository
from .models import InvoiceSummary, LabResultSummary, PortalRecordBundle, VisitSummary
from .rest_repository import RestPortalRecordsRepository


class LegacyOrmPortalRecordsRepository:
    def get_dashboard_records(self, username: str) -> PortalRecordBundle:
        from django.contrib.auth.models import User
        from django.utils import timezone

        from apps.core.models import DoctorVisit, LabTest

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return PortalRecordBundle()

        recent_labs = tuple(LabTest.objects.filter(patient=user)[:5])
        total_labs = LabTest.objects.filter(patient=user).count()
        pending_labs = LabTest.objects.filter(patient=user, status="pending").count()
        abnormal_labs = LabTest.objects.filter(patient=user, is_abnormal=True).count()

        recent_visits = tuple(DoctorVisit.objects.filter(patient=user)[:5])
        total_visits = DoctorVisit.objects.filter(patient=user).count()
        upcoming_followups = tuple(
            DoctorVisit.objects.filter(
                patient=user,
                follow_up_date__gte=timezone.now().date(),
            ).order_by("follow_up_date")[:3]
        )
        latest_visit = (
            DoctorVisit.objects.filter(patient=user).order_by("-visit_date").first()
        )

        return PortalRecordBundle(
            recent_labs=recent_labs,
            total_labs=total_labs,
            pending_labs=pending_labs,
            abnormal_labs=abnormal_labs,
            recent_visits=recent_visits,
            total_visits=total_visits,
            upcoming_followups=upcoming_followups,
            latest_vitals_bp=getattr(latest_visit, "vitals_bp", "") or "",
            latest_vitals_heart_rate=(
                str(getattr(latest_visit, "vitals_heart_rate", "") or "")
            ),
            latest_vitals_temperature=(
                str(getattr(latest_visit, "vitals_temperature", "") or "")
            ),
            latest_vitals_weight=str(getattr(latest_visit, "vitals_weight", "") or ""),
        )

    def get_lab_results(
        self,
        username: str,
        *,
        status: str | None = None,
        category: str | None = None,
    ) -> Sequence[LabResultSummary]:
        from django.contrib.auth.models import User

        from apps.core.models import LabTest

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return ()

        tests = LabTest.objects.filter(patient=user)
        if status:
            tests = tests.filter(status=status)
        if category:
            tests = tests.filter(test_category=category)
        return tuple(tests)

    def get_lab_categories(self, username: str) -> Sequence[str]:
        from django.contrib.auth.models import User

        from apps.core.models import LabTest

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return ()

        categories = LabTest.objects.filter(patient=user).values_list(
            "test_category", flat=True
        )
        return tuple(categories.distinct())

    def get_visit_summaries(
        self,
        username: str,
        *,
        visit_type: str | None = None,
    ) -> Sequence[VisitSummary]:
        from django.contrib.auth.models import User

        from apps.core.models import DoctorVisit

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return ()

        visits = DoctorVisit.objects.filter(patient=user)
        if visit_type:
            visits = visits.filter(visit_type=visit_type)
        return tuple(visits)

    def get_invoices(
        self,
        username: str | None = None,
        *,
        status: str | None = None,
    ) -> Sequence[InvoiceSummary]:
        from django.contrib.auth.models import User

        from apps.core.models import Invoice

        invoices = (
            Invoice.objects.all()
            .select_related("patient")
            .prefetch_related("line_items")
        )
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return ()
            invoices = invoices.filter(patient=user)
        if status:
            invoices = invoices.filter(status=status)

        return tuple(invoices.order_by("-created_at"))


class PortalRecordsRepository(Protocol):
    def get_dashboard_records(self, username: str) -> PortalRecordBundle: ...

    def get_lab_results(
        self,
        username: str,
        *,
        status: str | None = None,
        category: str | None = None,
    ) -> Sequence[LabResultSummary]: ...

    def get_lab_categories(self, username: str) -> Sequence[str]: ...

    def get_visit_summaries(
        self,
        username: str,
        *,
        visit_type: str | None = None,
    ) -> Sequence[VisitSummary]: ...

    def get_invoices(
        self,
        username: str | None = None,
        *,
        status: str | None = None,
    ) -> Sequence[InvoiceSummary]: ...


def get_portal_records_repository() -> PortalRecordsRepository:
    source = getattr(settings, "PORTAL_RECORDS_SOURCE", "fhir_file")

    if source == "fhir_file":
        return FilePortalRecordsRepository(
            data_path=getattr(settings, "FHIR_DATA_PATH", "")
        )

    if source == "fhir_rest":
        return RestPortalRecordsRepository(
            base_url=getattr(settings, "FHIR_REST_BASE_URL", "")
        )

    if source == "legacy_orm":
        return LegacyOrmPortalRecordsRepository()

    raise ValueError(f"Unsupported PORTAL_RECORDS_SOURCE: {source}")
