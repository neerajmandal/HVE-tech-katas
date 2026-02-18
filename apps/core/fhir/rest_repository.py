from __future__ import annotations

from collections.abc import Sequence

from .models import InvoiceSummary, LabResultSummary, PortalRecordBundle, VisitSummary


class RestPortalRecordsRepository:
    def __init__(self, *, base_url: str) -> None:
        self._base_url = base_url

    def get_dashboard_records(self, username: str) -> PortalRecordBundle:
        return PortalRecordBundle()

    def get_lab_results(
        self,
        username: str,
        *,
        status: str | None = None,
        category: str | None = None,
    ) -> Sequence[LabResultSummary]:
        return ()

    def get_lab_categories(self, username: str) -> Sequence[str]:
        return ()

    def get_visit_summaries(
        self,
        username: str,
        *,
        visit_type: str | None = None,
    ) -> Sequence[VisitSummary]:
        return ()

    def get_invoices(
        self,
        username: str | None = None,
        *,
        status: str | None = None,
    ) -> Sequence[InvoiceSummary]:
        return ()
