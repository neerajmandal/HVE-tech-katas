import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .domain import DOMAIN


def domain_json(request):
    return JsonResponse(DOMAIN)


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
    monthly_rate = (annual_return / 100) / 12
    balance = initial_investment
    total_contributions = initial_investment
    yearly_data = []

    for year in range(1, int(years) + 1):
        for _ in range(12):
            balance += monthly_contribution
            total_contributions += monthly_contribution
            balance += balance * monthly_rate

        yearly_data.append(
            {
                "year": year,
                "balance": round(balance, 2),
                "contributions": round(total_contributions, 2),
                "interest": round(balance - total_contributions, 2),
            }
        )

    final_value = round(balance, 2)
    total_contributions = round(total_contributions, 2)
    interest_earned = round(final_value - total_contributions, 2)
    growth_multiple = (
        round(final_value / total_contributions, 2) if total_contributions else 0
    )

    return {
        "final_value": final_value,
        "total_contributions": total_contributions,
        "interest_earned": interest_earned,
        "growth_multiple": growth_multiple,
        "yearly_data": yearly_data,
    }


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
    from .models import DoctorVisit, LabTest

    user = request.user

    recent_labs = LabTest.objects.filter(patient=user)[:5]
    total_labs = LabTest.objects.filter(patient=user).count()
    pending_labs = LabTest.objects.filter(patient=user, status="pending").count()
    abnormal_labs = LabTest.objects.filter(patient=user, is_abnormal=True).count()

    recent_visits = DoctorVisit.objects.filter(patient=user)[:5]
    total_visits = DoctorVisit.objects.filter(patient=user).count()

    from django.utils import timezone

    upcoming_followups = DoctorVisit.objects.filter(
        patient=user, follow_up_date__gte=timezone.now().date()
    ).order_by("follow_up_date")[:3]

    context = {
        "recent_labs": recent_labs,
        "total_labs": total_labs,
        "pending_labs": pending_labs,
        "abnormal_labs": abnormal_labs,
        "recent_visits": recent_visits,
        "total_visits": total_visits,
        "upcoming_followups": upcoming_followups,
    }

    return render(request, "core/dashboard.html", context)


@login_required
def lab_tests(request):
    """Display patient's lab test results"""
    from .models import LabTest

    user = request.user
    tests = LabTest.objects.filter(patient=user)

    status_filter = request.GET.get("status", "all")
    if status_filter != "all":
        tests = tests.filter(status=status_filter)

    category_filter = request.GET.get("category", "all")
    if category_filter != "all":
        tests = tests.filter(test_category=category_filter)

    categories = (
        LabTest.objects.filter(patient=user)
        .order_by()
        .values_list("test_category", flat=True)
        .distinct()
    )

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
    from .models import DoctorVisit

    user = request.user
    visits = DoctorVisit.objects.filter(patient=user)

    type_filter = request.GET.get("type", "all")
    if type_filter != "all":
        visits = visits.filter(visit_type=type_filter)

    context = {
        "visits": visits,
        "type_filter": type_filter,
    }

    return render(request, "core/doctor_visits.html", context)


@login_required
def invoice_list(request):
    """Display billing dashboard with all patient invoices for clinic staff"""
    from .models import Invoice

    invoices = (
        Invoice.objects.all()
        .select_related("patient")
        .prefetch_related("line_items")
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status", "all")
    if status_filter != "all":
        invoices = invoices.filter(status=status_filter)

    all_invoices = Invoice.objects.all()

    unpaid_invoices = all_invoices.filter(status__in=["pending", "overdue"])
    total_unpaid_count = unpaid_invoices.count()
    total_unpaid_amount = sum(invoice.total for invoice in unpaid_invoices)

    overdue_invoices = all_invoices.filter(status="overdue")
    total_overdue_count = overdue_invoices.count()
    total_overdue_amount = sum(invoice.total for invoice in overdue_invoices)

    paid_invoices = all_invoices.filter(status="paid")
    total_paid_count = paid_invoices.count()
    total_paid_amount = sum(invoice.total for invoice in paid_invoices)

    total_revenue = sum(invoice.total for invoice in all_invoices)

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
