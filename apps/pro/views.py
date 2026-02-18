from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def dashboard(request):
    """Display Pro dashboard."""
    context = {
        "has_active_subscription": False,
    }
    return render(request, "pro/dashboard.html", context)


@login_required
def customer_portal(request):
    """Redirect user to pricing page (Stripe removed)."""
    return redirect("pricing")
