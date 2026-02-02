# Tech Kata: Stingrays CarePayments - Hospital Invoice & Payment Portal

**Duration:** 90 minutes
**Difficulty:** Intermediate
**Technologies:** Django 5.2, Stripe API, dj-stripe, Tailwind CSS, SQLite

## Overview

You are a Full-Stack Engineer at Stingrays Hospital. The billing department needs a way for clinic staff to send secure payment links to patients who have outstanding balances. Currently, the system can track invoices, but there's no way for patients to pay online.

Your task is to integrate Stripe payment processing so clinic staff can generate payment links and patients can pay their medical bills securely online.

The application already has:
- ✅ Authentication system for clinic staff
- ✅ Invoice database models (Patient, Invoice, InvoiceLineItem)
- ✅ Billing dashboard showing patient invoices and outstanding balances
- ✅ Dummy patient data with sample invoices

**Your mission:** Add Stripe payment integration so clinic staff can send payment links to patients and track when invoices are paid.

---

## Setup Instructions

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies for Tailwind
npm install

# Run database migrations
python manage.py migrate

# Seed dummy data (patients and invoices)
python manage.py seed_dummy_data

# Start development server
chmod +x ./start.sh
./start.sh
```

**Access the app:**
- App URL: http://localhost:8000
- Admin panel: http://localhost:8000/admin

**Test Login Credentials:**
- Username: `patient1`, `patient2`, `patient3`, `patient4`, or `patient5`
- Password: `password123`

---

## Current Application State

### What's Already Built

1. **Models** ([apps/core/models.py](apps/core/models.py)):
   - `PatientProfile` - Extended user profile with healthcare info
   - `Invoice` - Medical invoices with status tracking (pending, paid, overdue, cancelled)
   - `InvoiceLineItem` - Individual charges (X-rays, checkups, etc.)

2. **Views** ([apps/core/views.py](apps/core/views.py)):
   - `invoice_list` - Displays all invoices for logged-in patient with filtering

3. **Templates**:
   - [base.html](templates/base.html) - Base template with navigation
   - [invoices_list.html](templates/core/invoices_list.html) - Invoice dashboard with "Pay Now" buttons (non-functional)

4. **Dummy Data:**
   - 5 test patients with medical histories
   - 15 invoices with varying statuses (mostly unpaid)
   - Realistic healthcare services (X-rays, checkups, MRI scans, etc.)

### What's Missing (Your Tasks)

The "Pay Now" buttons don't do anything yet. You need to implement the complete payment flow using Stripe.

---

## Tasks

### 💳 TICKET-001: Set Up Stripe Integration

**Type:** Feature
**Priority:** Critical
**Estimated Time:** 15 minutes

**Description:**
Configure Stripe API keys and install the necessary dependencies to enable payment processing.

**Acceptance Criteria:**
- [ ] Add `dj-stripe` package to [requirements.txt](requirements.txt) (if not already present)
- [ ] Configure Stripe API keys in [settings.py](StingraysCarePayments/settings.py)
- [ ] Create Stripe account and get test API keys from https://dashboard.stripe.com/test/apikeys
- [ ] Add environment variables or hardcode test keys for development
- [ ] Verify Stripe configuration by creating a test PaymentIntent

**Technical Specifications:**
- Use Stripe test mode keys (start with `pk_test_` and `sk_test_`)
- Recommended: Store keys as environment variables
- Test publishable key needed in templates
- Test secret key needed in backend views

**Resources:**
- Stripe Python SDK: https://stripe.com/docs/api/python
- dj-stripe docs: https://dj-stripe.dev/

---

### 📄 TICKET-002: Create Invoice Detail Page

**Type:** Feature
**Priority:** High
**Estimated Time:** 20 minutes

**Description:**
Create a detailed invoice view that shows all line items, totals, and payment history before redirecting to payment.

**Acceptance Criteria:**
- [ ] Create view at `/invoices/<invoice_id>/`
- [ ] Display invoice header (number, dates, status)
- [ ] Show patient information
- [ ] Display line items table with:
  - Service description
  - Quantity
  - Unit price
  - Total price
  - Service date
  - Provider name
- [ ] Show subtotal, tax, and grand total
- [ ] Show "Pay Now" button only if status is `pending` or `overdue`
- [ ] Button should redirect to payment page
- [ ] Template uses Tailwind CSS for styling

**Technical Notes:**
- URL pattern: `path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail')`
- Use `@login_required` decorator
- Verify user owns the invoice (security check)
- Template: `templates/core/invoice_detail.html`

---

### 💰 TICKET-003: Stripe Payment Intent Integration

**Type:** Feature
**Priority:** Critical
**Estimated Time:** 30 minutes

**Description:**
Implement the payment page with Stripe PaymentIntent API to process credit card payments securely.

**Acceptance Criteria:**
- [ ] Create payment view at `/invoices/<invoice_id>/pay/`
- [ ] Create Stripe PaymentIntent when page loads:
  - Amount = `invoice.total * 100` (convert to cents)
  - Currency = 'usd'
  - Metadata includes `invoice_id`
- [ ] Display invoice summary (amount, due date, invoice number)
- [ ] Integrate Stripe Payment Element in frontend
- [ ] Handle successful payment:
  - Update invoice status to 'paid'
  - Create Payment record (if you create a Payment model)
  - Redirect to success page
- [ ] Handle payment errors and display to user
- [ ] Template: `templates/core/invoice_pay.html`

**Technical Specifications:**

**Backend** (`apps/core/views.py`):
```python
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def invoice_pay(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, patient=request.user)

    if request.method == 'POST':
        # Handle payment confirmation
        pass
    else:
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(invoice.total * 100),
            currency='usd',
            metadata={'invoice_id': invoice.id}
        )

        context = {
            'invoice': invoice,
            'client_secret': intent.client_secret,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY
        }
        return render(request, 'core/invoice_pay.html', context)
```

**Frontend** (JavaScript in template):
```javascript
const stripe = Stripe('{{ STRIPE_PUBLIC_KEY }}');
const elements = stripe.elements({clientSecret: '{{ client_secret }}'});
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// Handle form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const {error} = await stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: 'http://localhost:8000/invoices/{{ invoice.id }}/payment-success/',
        },
    });
    // Handle errors
});
```

**Resources:**
- Payment Intents: https://stripe.com/docs/payments/payment-intents
- Payment Element: https://stripe.com/docs/payments/payment-element
- Test Cards: Use `4242 4242 4242 4242` with any future date and CVC

---

### ✅ TICKET-004: Payment Confirmation & Invoice Update

**Type:** Feature
**Priority:** High
**Estimated Time:** 15 minutes

**Description:**
Create a success page that confirms payment and updates the invoice status in the database.

**Acceptance Criteria:**
- [ ] Create view at `/invoices/<invoice_id>/payment-success/`
- [ ] Verify payment was successful with Stripe API
- [ ] Update invoice status from 'pending' to 'paid'
- [ ] Display success message with:
  - Confirmation number (Stripe payment_intent ID)
  - Amount paid
  - Invoice number
  - Date paid
- [ ] Provide button to return to invoice list
- [ ] Template: `templates/core/invoice_payment_success.html`

**Technical Notes:**
- Retrieve `payment_intent` param from URL query string
- Use `stripe.PaymentIntent.retrieve()` to verify payment
- Only update invoice if payment status is 'succeeded'
- Consider creating a Payment model to track all transactions

---

### 📧 TICKET-005: Email Notifications (Optional Bonus)

**Type:** Enhancement
**Priority:** Low
**Estimated Time:** 15 minutes

**Description:**
Send email notifications when:
1. A new invoice is created (with payment link)
2. A payment is successfully processed (receipt)

**Acceptance Criteria:**
- [ ] HTML email template: `templates/emails/invoice_notification.html`
- [ ] Email includes invoice summary and payment link
- [ ] Receipt email includes payment confirmation details
- [ ] Emails sent via Django's email backend
- [ ] For development, use console email backend

**Technical Notes:**
```python
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Generate payment URL
payment_url = request.build_absolute_uri(
    reverse('invoice_pay', args=[invoice.id])
)

# Send email
send_mail(
    subject=f'Invoice #{invoice.invoice_number}',
    message=f'You have a new invoice. Pay here: {payment_url}',
    from_email='billing@stingrayscarepayments.com',
    recipient_list=[invoice.patient.email],
    html_message=render_to_string('emails/invoice_notification.html', {
        'invoice': invoice,
        'payment_url': payment_url
    })
)
```

---

### 🔐 TICKET-006: Webhook Handler (Advanced Bonus)

**Type:** Enhancement
**Priority:** Low
**Estimated Time:** 20 minutes

**Description:**
Implement Stripe webhook to handle `payment_intent.succeeded` events for more reliable payment confirmation.

**Acceptance Criteria:**
- [ ] Create webhook endpoint at `/stripe/webhook/`
- [ ] Verify webhook signature
- [ ] Handle `payment_intent.succeeded` event
- [ ] Update invoice status when payment succeeds
- [ ] Log webhook events for debugging
- [ ] Configure webhook URL in Stripe Dashboard

**Technical Specifications:**
```python
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        invoice_id = payment_intent['metadata']['invoice_id']

        invoice = Invoice.objects.get(id=invoice_id)
        invoice.status = 'paid'
        invoice.save()

    return HttpResponse(status=200)
```

**Resources:**
- Webhooks: https://stripe.com/docs/webhooks
- Test webhooks locally with Stripe CLI: `stripe listen --forward-to localhost:8000/stripe/webhook/`

---

## Project Structure

```
/workspaces/hve-tech-katas/
├── apps/
│   └── core/
│       ├── models.py              # Invoice, PatientProfile, InvoiceLineItem
│       ├── views.py               # invoice_list (add payment views here)
│       ├── urls.py                # URL routing
│       └── management/
│           └── commands/
│               └── seed_dummy_data.py   # Dummy data generator
├── templates/
│   ├── base.html                  # Base template with nav
│   ├── core/
│   │   └── invoices_list.html     # Invoice dashboard
│   └── emails/                    # (Create this for email templates)
├── StingraysCarePayments/
│   ├── settings.py                # Django settings (add Stripe keys here)
│   └── urls.py                    # Root URL config
├── manage.py
├── requirements.txt               # Python dependencies
└── tech-kata/
    └── problem-1.md              # This file
```

---

## Testing Your Implementation

### Manual Test Flow:

1. **Setup:**
   ```bash
   python manage.py migrate
   python manage.py seed_dummy_data
   python manage.py runserver
   ```

2. **Patient Login:**
   - Go to http://localhost:8000
   - Click "View My Invoices" → Login
   - Username: `patient1`, Password: `password123`

3. **View Invoices:**
   - Should see list of invoices with statuses
   - Filter by Pending/Overdue/Paid
   - Verify summary cards show correct totals

4. **Payment Flow:**
   - Click "Pay Now" on a pending invoice
   - Should see invoice detail page (if implemented)
   - Click "Pay" to go to payment page
   - Enter test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits
   - Submit payment

5. **Verify Success:**
   - Should redirect to success page
   - Invoice status should change to "Paid"
   - Invoice should disappear from Pending filter
   - Should appear in Paid filter

6. **Test Error Handling:**
   - Try declined card: `4000 0000 0000 0002`
   - Should display error message

---

## Evaluation Criteria

- **Functionality (40%)**: Payment flow works end-to-end
- **Stripe Integration (20%)**: Correct use of PaymentIntent API
- **Security (15%)**: Proper authentication checks, amount verification
- **UI/UX (15%)**: Clean, professional payment interface
- **Error Handling (10%)**: Graceful handling of payment failures

---

## Helpful Resources

**Stripe Documentation:**
- Quick start: https://stripe.com/docs/payments/quickstart
- Payment Intents: https://stripe.com/docs/payments/payment-intents
- Payment Element: https://stripe.com/docs/payments/payment-element
- Test cards: https://stripe.com/docs/testing

**Django Resources:**
- Class-based views: https://docs.djangoproject.com/en/5.2/topics/class-based-views/
- URL dispatcher: https://docs.djangoproject.com/en/5.2/topics/http/urls/
- Email: https://docs.djangoproject.com/en/5.2/topics/email/

**Tailwind CSS:**
- Forms: https://tailwindcss.com/docs/forms
- Buttons: https://tailwindcss.com/docs/button
- Cards: https://flowbite.com/docs/components/card/

---

## Submission

1. Ensure all acceptance criteria are met
2. Test the complete payment flow
3. Verify invoice status updates correctly
4. Check that dummy data loads properly
5. Document any additional features or improvements

**Bonus Points:**
- Add payment history section to invoice detail page
- Implement payment receipt PDF download
- Add invoice search functionality
- Create admin dashboard for hospital staff
- Implement email notifications
- Set up Stripe webhooks for reliability

---

## Need Help?

- Check existing models in [apps/core/models.py](apps/core/models.py)
- Review the invoice list view in [apps/core/views.py](apps/core/views.py)
- Look at the invoice template styling in [templates/core/invoices_list.html](templates/core/invoices_list.html)
- Stripe has excellent error messages - read them carefully!
- Use `print()` or Django Debug Toolbar to debug

Good luck! 🏥💳
