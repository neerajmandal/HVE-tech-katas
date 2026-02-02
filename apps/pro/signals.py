"""Stripe webhook event signal handlers for subscription management."""

from djstripe.event_handlers import djstripe_receiver


@djstripe_receiver("checkout.session.completed")
def handle_checkout_completed(sender, event, **kwargs):
    """Handle successful checkout session completion."""
    session = event.data["object"]
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")

    if subscription_id:
        print(f"New subscription {subscription_id} for customer {customer_id}")


@djstripe_receiver("customer.subscription.created")
def handle_subscription_created(sender, event, **kwargs):
    """Handle new subscription creation."""
    subscription = event.data["object"]
    print(f"Subscription created: {subscription['id']}")


@djstripe_receiver("customer.subscription.updated")
def handle_subscription_updated(sender, event, **kwargs):
    """Handle subscription updates including status changes."""
    subscription = event.data["object"]
    status = subscription["status"]
    print(f"Subscription {subscription['id']} status: {status}")

    if subscription.get("cancel_at_period_end"):
        print(f"Subscription {subscription['id']} scheduled for cancellation")


@djstripe_receiver("customer.subscription.deleted")
def handle_subscription_deleted(sender, event, **kwargs):
    """Handle subscription cancellation."""
    subscription = event.data["object"]
    print(f"Subscription cancelled: {subscription['id']}")


@djstripe_receiver("invoice.payment_succeeded")
def handle_payment_success(sender, event, **kwargs):
    """Handle successful invoice payment."""
    invoice = event.data["object"]
    print(f"Payment succeeded for invoice: {invoice['id']}")


@djstripe_receiver("invoice.payment_failed")
def handle_payment_failure(sender, event, **kwargs):
    """Handle failed invoice payment."""
    invoice = event.data["object"]
    print(f"Payment failed for invoice: {invoice['id']}")
