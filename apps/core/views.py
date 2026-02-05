import os

import stripe
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from djstripe import models as djstripe_models
from djstripe.settings import djstripe_settings
import json


def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def pricing(request):
    """Display pricing page with Stripe Pricing Table."""
    context = {
        "STRIPE_PUBLIC_KEY": djstripe_settings.STRIPE_PUBLIC_KEY,
        "pricing_table_id": os.environ.get("STRIPE_PRICING_TABLE_ID", "prctbl_1Sn3haBjJ6zCPbztehr74kjO"),
    }

    if request.user.is_authenticated:
        try:
            customer = djstripe_models.Customer.objects.get(subscriber=request.user)
            stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY

            customer_session = stripe.CustomerSession.create(
                customer=customer.id,
                components={"pricing_table": {"enabled": True}},
            )
            context["customer_session_client_secret"] = customer_session.client_secret
        except djstripe_models.Customer.DoesNotExist:
            pass

    return render(request, "core/pricing.html", context)

def free_tools(request):
    return render(request, 'core/free-tools.html')

@login_required
def welcome(request):
    """Welcome page after signup showing subscription status"""
    return render(request, 'core/welcome.html')

def calculate_compound_interest(initial_investment, monthly_contribution, annual_return, years):
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

    if request.method == 'GET' and any(key in request.GET for key in ['initial', 'monthly', 'return', 'years']):
        try:
            initial_investment = float(request.GET.get('initial', initial_investment))
            monthly_contribution = float(request.GET.get('monthly', monthly_contribution))
            annual_return = float(request.GET.get('return', annual_return))
            years = int(request.GET.get('years', years))
        except (ValueError, TypeError):
            pass

    results = calculate_compound_interest(
        initial_investment,
        monthly_contribution,
        annual_return,
        years
    )

    context = {
        'initial_investment': initial_investment,
        'monthly_contribution': monthly_contribution,
        'annual_return': annual_return,
        'years': years,
        'final_value': results['final_value'],
        'total_contributions': results['total_contributions'],
        'interest_earned': results['interest_earned'],
        'growth_multiple': results['growth_multiple'],
        'yearly_data': results['yearly_data'],
        'yearly_data_json': json.dumps(results['yearly_data'])
    }

    return render(request, 'core/investment-calculator.html', context)


@login_required
def patient_dashboard(request):
    """Patient dashboard showing overview of health records"""
    from .models import LabTest, DoctorVisit

    user = request.user

    recent_labs = LabTest.objects.filter(patient=user)[:5]
    total_labs = LabTest.objects.filter(patient=user).count()
    pending_labs = LabTest.objects.filter(patient=user, status='pending').count()
    abnormal_labs = LabTest.objects.filter(patient=user, is_abnormal=True).count()

    recent_visits = DoctorVisit.objects.filter(patient=user)[:5]
    total_visits = DoctorVisit.objects.filter(patient=user).count()

    from django.utils import timezone
    upcoming_followups = DoctorVisit.objects.filter(
        patient=user,
        follow_up_date__gte=timezone.now().date()
    ).order_by('follow_up_date')[:3]

    context = {
        'recent_labs': recent_labs,
        'total_labs': total_labs,
        'pending_labs': pending_labs,
        'abnormal_labs': abnormal_labs,
        'recent_visits': recent_visits,
        'total_visits': total_visits,
        'upcoming_followups': upcoming_followups,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def lab_tests(request):
    """Display patient's lab test results"""
    from .models import LabTest

    user = request.user
    tests = LabTest.objects.filter(patient=user)

    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        tests = tests.filter(status=status_filter)

    category_filter = request.GET.get('category', 'all')
    if category_filter != 'all':
        tests = tests.filter(test_category=category_filter)

    categories = LabTest.objects.filter(patient=user).values_list('test_category', flat=True).distinct()

    context = {
        'tests': tests,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
    }

    return render(request, 'core/lab_tests.html', context)


@login_required
def doctor_visits(request):
    """Display patient's doctor visit history"""
    from .models import DoctorVisit

    user = request.user
    visits = DoctorVisit.objects.filter(patient=user)

    type_filter = request.GET.get('type', 'all')
    if type_filter != 'all':
        visits = visits.filter(visit_type=type_filter)

    context = {
        'visits': visits,
        'type_filter': type_filter,
    }

    return render(request, 'core/doctor_visits.html', context)


@login_required
def invoice_list(request):
    """Display billing dashboard with all patient invoices for clinic staff"""
    from .models import Invoice

    invoices = Invoice.objects.all().select_related('patient').prefetch_related('line_items').order_by('-created_at')

    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        invoices = invoices.filter(status=status_filter)

    all_invoices = Invoice.objects.all()

    unpaid_invoices = all_invoices.filter(status__in=['pending', 'overdue'])
    total_unpaid_count = unpaid_invoices.count()
    total_unpaid_amount = sum(invoice.total for invoice in unpaid_invoices)

    overdue_invoices = all_invoices.filter(status='overdue')
    total_overdue_count = overdue_invoices.count()
    total_overdue_amount = sum(invoice.total for invoice in overdue_invoices)

    paid_invoices = all_invoices.filter(status='paid')
    total_paid_count = paid_invoices.count()
    total_paid_amount = sum(invoice.total for invoice in paid_invoices)

    total_revenue = sum(invoice.total for invoice in all_invoices)

    collection_rate = (total_paid_amount / total_revenue * 100) if total_revenue > 0 else 0

    context = {
        'invoices': invoices,
        'status_filter': status_filter,
        'total_unpaid_count': total_unpaid_count,
        'total_unpaid_amount': total_unpaid_amount,
        'total_overdue_count': total_overdue_count,
        'total_overdue_amount': total_overdue_amount,
        'total_paid_count': total_paid_count,
        'total_paid_amount': total_paid_amount,
        'total_revenue': total_revenue,
        'collection_rate': collection_rate,
    }

    return render(request, 'core/invoices_list.html', context)
