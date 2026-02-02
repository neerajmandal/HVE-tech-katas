# Stingrays CarePayments

A hospital invoice and payment management system built with Django, Stripe, and Tailwind CSS for the HVE Tech Kata training program.

## Quick Start

After cloning the repository, follow these steps to set up the application:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node dependencies for Tailwind CSS
npm install

# 3. Create database tables
python manage.py migrate

# 4. Populate database with 20 dummy patients and sample invoices
python manage.py seed_dummy_data

# 5. Start the development server
chmod +x ./start.sh
./start.sh
```

## Access the Application

- **App URL**: http://localhost:8000
- **Billing Dashboard**: http://localhost:8000/invoices/
- **Admin Panel**: http://localhost:8000/admin

## Test Credentials

After running `seed_dummy_data`, you can login with any of these accounts:

- **Username**: `patient1` through `patient20`
- **Password**: `password123`

## What's Included

- ✅ 20 dummy patient profiles with realistic healthcare data
- ✅ Sample invoices with varying statuses (pending, paid, overdue)
- ✅ Authentication system using django-allauth
- ✅ Billing dashboard with metrics (unpaid balance, overdue amounts, collection rate)
- ✅ Responsive UI built with Tailwind CSS

## Tech Kata Challenge

This repository is set up for a coding kata where participants will integrate Stripe payment processing. See [tech-kata/problem-1.md](tech-kata/problem-1.md) for the full challenge description.

**Your Mission**: Add Stripe payment integration so clinic staff can send payment links to patients and track when invoices are paid.

## Technology Stack

- **Backend**: Django 5.2, Python 3.11
- **Frontend**: Tailwind CSS, Flowbite components
- **Payment**: Stripe API, dj-stripe
- **Database**: SQLite (development)
- **Authentication**: django-allauth

## Project Structure

```
/workspaces/hve-tech-katas/
├── apps/core/              # Main application
│   ├── models.py          # PatientProfile, Invoice, InvoiceLineItem
│   ├── views.py           # Billing dashboard views
│   └── management/
│       └── commands/
│           └── seed_dummy_data.py  # Database population script
├── templates/             # Django templates
│   ├── base.html         # Base template
│   └── core/
│       ├── home.html     # Landing page
│       └── invoices_list.html  # Billing dashboard
├── StingraysCarePayments/  # Django settings
├── tech-kata/            # Kata challenge documentation
│   └── problem-1.md      # Full challenge description
└── start.sh              # Development server startup script
```

## Need Help?

Check the [tech-kata/problem-1.md](tech-kata/problem-1.md) file for:
- Detailed setup instructions
- Ticket descriptions for implementing Stripe payments
- Testing guidelines
- Helpful resources and documentation links
