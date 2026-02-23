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

If you are using MacOS, or Windows with WSL there is a setup script to automatically provision your environment:

```bash
./scripts/setup.sh
```

Or do so manually:

```bash
# 1. Install Python dependencies
uv sync

# 2. Install Node dependencies
npm install

# 3. Run setup script
npm run setup
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

```text
├── apps/
│   ├── core/              # Main portal application
│   └── pro/               # Professional/Doctor features
├── StingrayHealthPortal/  # Django project
├── templates/             # Django templates
│   ├── base.html          # Base HTML page template
│   ├── account/           # Authentication templates
│   ├── core/              # Core app templates
│   └── pro/               # Pro app templates
├── static/                # Static assets (CSS, images)
├── data/                  # Sample FHIR datasets
├── docs/                  # Documentation
│   ├── ADRs/              # Architecture Decision Records
│   └── BRDs/              # Business Requirements Documents
├── scripts/               # Development and setup scripts
└── manage.py              # Django management script
```

## Need Help?

Check the [CHALLENGES.md](CHALLENGES.md) file for:

- Detailed schedule with breaks
- Ticket descriptions for each HVE technique
- FHIR integration guidance
- Sample data for testing
