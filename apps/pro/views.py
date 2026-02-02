import stripe
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from djstripe import models as djstripe_models
from djstripe.settings import djstripe_settings


@login_required
def dashboard(request):
    """Display Pro dashboard with subscription status."""
    context = {
        "customer": None,
        "subscriptions": [],
        "has_active_subscription": False,
    }

    try:
        customer = djstripe_models.Customer.objects.get(subscriber=request.user)
        context["customer"] = customer
        context["subscriptions"] = customer.subscriptions.filter(
            status__in=["active", "trialing", "past_due"]
        )
        context["has_active_subscription"] = customer.subscriptions.filter(
            status__in=["active", "trialing"]
        ).exists()
    except djstripe_models.Customer.DoesNotExist:
        pass

    return render(request, "pro/dashboard.html", context)


@login_required
def customer_portal(request):
    """Redirect user to Stripe Customer Portal for billing management."""
    try:
        customer = djstripe_models.Customer.objects.get(subscriber=request.user)
    except djstripe_models.Customer.DoesNotExist:
        return redirect("pricing")

    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY

    portal_session = stripe.billing_portal.Session.create(
        customer=customer.id,
        return_url=request.build_absolute_uri("/pro/dashboard/"),
    )

    return redirect(portal_session.url)