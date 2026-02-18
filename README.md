# Stingray Health Portal - Secure Patient Messaging

A patient portal system built with Django and Tailwind CSS for the HVE Tech Kata training program. This kata focuses on building a secure messaging feature for patient-doctor communication.

## The Problem

Currently, patients at our clinic have no direct way to communicate with their assigned doctor through the patient portal. When patients have non-urgent questions about their health, medications, or upcoming appointments, they must:

- Call the clinic and wait on hold
- Leave a voicemail and wait for a callback
- Schedule an unnecessary in-person visit
- Send emails that may go to a shared inbox and get lost

**Your Mission**: Build a secure messaging feature within the patient portal that enables patients to message their doctors, doctors to respond, and admins to manage assignments.

## Quick Start

```bash
# 1. Install Python dependencies
uv sync

# 2. Install Node dependencies for Tailwind CSS
npm install

# 3. Create database tables
uv run python manage.py migrate

# 4. Start the development server
uv run ./scripts/start.sh
```

## Access the Application

- **App URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## Test Credentials

- **Username**: `patient1` through `patient5`
- **Password**: `password123`

## What's Included

- ✅ Patient portal with appointments and lab results
- ✅ Patients assigned to a primary doctor
- ✅ Admin manages patient accounts
- ✅ Authentication system using django-allauth
- ✅ Responsive UI built with Tailwind CSS

## Tech Kata Challenge

This repository is set up for an HVE coding kata (2.5 hours). See [CHALLENGES.md](CHALLENGES.md) for the full challenge description.

## Technology Stack

- **Backend**: Django 5.2, Python 3.11
- **Frontend**: Tailwind CSS, Flowbite components
- **Database**: SQLite (development)
- **Authentication**: django-allauth
- **Standards**: FHIR (Fast Healthcare Interoperability Resources)

## Project Structure

```
├── apps/core/              # Main application
│   ├── models.py          # Patient, Doctor, Message models
│   ├── views.py           # Portal views
│   └── management/
│       └── commands/      # Management commands
├── templates/             # Django templates
│   ├── base.html         # Base template
│   └── core/             # Core app templates
├── StingrayHealthPortal/  # Django settings
├── tech-kata/            # Kata challenge documentation
│   └── HVE-secure-messaging-kata.md  # Full challenge description
└── scripts/              # Development scripts
```

## Need Help?

Check the [CHALLENGES.md](CHALLENGES.md) file for:
- Detailed schedule with breaks
- Ticket descriptions for each HVE technique
- FHIR integration guidance
- Sample data for testing
