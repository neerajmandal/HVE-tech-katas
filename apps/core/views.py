import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .fhir import get_portal_records_repository

VISIT_TYPE_DISPLAY = {
    "checkup": "Annual Checkup",
    "follow_up": "Follow-up",
    "urgent": "Urgent Care",
    "specialist": "Specialist Referral",
    "preventive": "Preventive Care",
    "history_physical": "History Physical",
}


class VisitTemplateAdapter:
    def __init__(self, visit: object) -> None:
        self._visit = visit

        self.id = getattr(visit, "id", "")
        self.doctor_name = getattr(visit, "doctor_name", "")
        self.specialty = getattr(visit, "specialty", "")
        self.visit_date = getattr(visit, "visit_date", None)
        self.visit_type = getattr(visit, "visit_type", "")
        self.reason = getattr(visit, "reason", "")
        self.diagnosis = getattr(visit, "diagnosis", "")
        self.treatment_plan = getattr(visit, "treatment_plan", "")
        self.follow_up_date = getattr(visit, "follow_up_date", None)
        self.notes = getattr(visit, "notes", "")
        self.vitals_bp = getattr(visit, "vitals_bp", "")
        self.vitals_heart_rate = getattr(visit, "vitals_heart_rate", "")
        self.vitals_temperature = getattr(visit, "vitals_temperature", "")
        self.vitals_weight = getattr(visit, "vitals_weight", "")

    def get_visit_type_display(self) -> str:
        if hasattr(self._visit, "get_visit_type_display"):
            return self._visit.get_visit_type_display()
        return VISIT_TYPE_DISPLAY.get(
            self.visit_type, self.visit_type.replace("_", " ").title()
        )


def adapt_visits_for_template(visits: object) -> tuple[object, ...]:
    adapted: list[object] = []
    for visit in visits:
        if hasattr(visit, "get_visit_type_display"):
            adapted.append(visit)
        else:
            adapted.append(VisitTemplateAdapter(visit))
    return tuple(adapted)


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def pricing(request):
    """Display pricing page."""
    context = {}
    return render(request, "core/pricing.html", context)


def free_tools(request):
    return render(request, "core/free-tools.html")


@login_required
def welcome(request):
    """Welcome page after signup showing subscription status"""
    return render(request, "core/welcome.html")


def calculate_compound_interest(
    initial_investment, monthly_contribution, annual_return, years
):
    """
    Calculate compound interest with monthly contributions
    Returns: dict with final value, total contributions, interest earned, growth multiple, and yearly data
    """
    pass


def investment_calculator(request):
    initial_investment = 10000
    monthly_contribution = 500
    annual_return = 10
    years = 30

    if request.method == "GET" and any(
        key in request.GET for key in ["initial", "monthly", "return", "years"]
    ):
        try:
            initial_investment = float(request.GET.get("initial", initial_investment))
            monthly_contribution = float(
                request.GET.get("monthly", monthly_contribution)
            )
            annual_return = float(request.GET.get("return", annual_return))
            years = int(request.GET.get("years", years))
        except (ValueError, TypeError):
            pass

    results = calculate_compound_interest(
        initial_investment, monthly_contribution, annual_return, years
    )

    context = {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "annual_return": annual_return,
        "years": years,
        "final_value": results["final_value"],
        "total_contributions": results["total_contributions"],
        "interest_earned": results["interest_earned"],
        "growth_multiple": results["growth_multiple"],
        "yearly_data": results["yearly_data"],
        "yearly_data_json": json.dumps(results["yearly_data"]),
    }

    return render(request, "core/investment-calculator.html", context)


@login_required
def patient_dashboard(request):
    """Patient dashboard showing overview of health records"""
    repository = get_portal_records_repository()
    bundle = repository.get_dashboard_records(request.user.username)

    context = {
        "recent_labs": bundle.recent_labs,
        "total_labs": bundle.total_labs,
        "pending_labs": bundle.pending_labs,
        "abnormal_labs": bundle.abnormal_labs,
        "recent_visits": adapt_visits_for_template(bundle.recent_visits),
        "total_visits": bundle.total_visits,
        "upcoming_followups": adapt_visits_for_template(bundle.upcoming_followups),
        "latest_vitals_bp": getattr(bundle, "latest_vitals_bp", ""),
        "latest_vitals_heart_rate": getattr(bundle, "latest_vitals_heart_rate", ""),
        "latest_vitals_temperature": getattr(bundle, "latest_vitals_temperature", ""),
        "latest_vitals_weight": getattr(bundle, "latest_vitals_weight", ""),
        "latest_vitals_bp_status": getattr(
            bundle, "latest_vitals_bp_status", "unknown"
        ),
        "latest_vitals_heart_rate_status": getattr(
            bundle, "latest_vitals_heart_rate_status", "unknown"
        ),
        "latest_vitals_temperature_status": getattr(
            bundle, "latest_vitals_temperature_status", "unknown"
        ),
        "latest_vitals_weight_status": getattr(
            bundle, "latest_vitals_weight_status", "unknown"
        ),
        "latest_vitals_bp_trend": getattr(bundle, "latest_vitals_bp_trend", "flat"),
        "latest_vitals_heart_rate_trend": getattr(
            bundle, "latest_vitals_heart_rate_trend", "flat"
        ),
        "latest_vitals_temperature_trend": getattr(
            bundle, "latest_vitals_temperature_trend", "flat"
        ),
        "latest_vitals_weight_trend": getattr(
            bundle, "latest_vitals_weight_trend", "flat"
        ),
    }

    return render(request, "core/dashboard.html", context)


@login_required
def lab_tests(request):
    """Display patient's lab test results"""
    repository = get_portal_records_repository()

    status_filter = request.GET.get("status", "all")
    status = status_filter if status_filter != "all" else None

    category_filter = request.GET.get("category", "all")
    category = category_filter if category_filter != "all" else None

    tests = repository.get_lab_results(
        request.user.username,
        status=status,
        category=category,
    )
    categories = repository.get_lab_categories(request.user.username)

    context = {
        "tests": tests,
        "status_filter": status_filter,
        "category_filter": category_filter,
        "categories": categories,
    }

    return render(request, "core/lab_tests.html", context)


@login_required
def doctor_visits(request):
    """Display patient's doctor visit history"""
    repository = get_portal_records_repository()

    type_filter = request.GET.get("type", "all")
    visit_type = type_filter if type_filter != "all" else None
    visits = repository.get_visit_summaries(
        request.user.username,
        visit_type=visit_type,
    )

    context = {
        "visits": adapt_visits_for_template(visits),
        "type_filter": type_filter,
    }

    return render(request, "core/doctor_visits.html", context)


@login_required
def invoice_list(request):
    """Display billing dashboard with all patient invoices for clinic staff"""
    repository = get_portal_records_repository()

    status_filter = request.GET.get("status", "all")
    status = status_filter if status_filter != "all" else None

    invoices = tuple(repository.get_invoices(status=status))
    all_invoices = tuple(repository.get_invoices())

    unpaid_invoices = [
        invoice
        for invoice in all_invoices
        if getattr(invoice, "status", "") in ["pending", "overdue"]
    ]
    total_unpaid_count = len(unpaid_invoices)
    total_unpaid_amount = sum(
        float(getattr(invoice, "total", 0) or 0) for invoice in unpaid_invoices
    )

    overdue_invoices = [
        invoice
        for invoice in all_invoices
        if getattr(invoice, "status", "") == "overdue"
    ]
    total_overdue_count = len(overdue_invoices)
    total_overdue_amount = sum(
        float(getattr(invoice, "total", 0) or 0) for invoice in overdue_invoices
    )

    paid_invoices = [
        invoice for invoice in all_invoices if getattr(invoice, "status", "") == "paid"
    ]
    total_paid_count = len(paid_invoices)
    total_paid_amount = sum(
        float(getattr(invoice, "total", 0) or 0) for invoice in paid_invoices
    )

    total_revenue = sum(
        float(getattr(invoice, "total", 0) or 0) for invoice in all_invoices
    )

    collection_rate = (
        (total_paid_amount / total_revenue * 100) if total_revenue > 0 else 0
    )

    context = {
        "invoices": invoices,
        "status_filter": status_filter,
        "total_unpaid_count": total_unpaid_count,
        "total_unpaid_amount": total_unpaid_amount,
        "total_overdue_count": total_overdue_count,
        "total_overdue_amount": total_overdue_amount,
        "total_paid_count": total_paid_count,
        "total_paid_amount": total_paid_amount,
        "total_revenue": total_revenue,
        "collection_rate": collection_rate,
    }

    return render(request, "core/invoices_list.html", context)
