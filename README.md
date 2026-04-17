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

Use of the VS Code devcontainer is recommended as the standard development environment.
It keeps Django, Playwright, and the visible browser session inside one Linux container and avoids host-specific setup drift.

For detailed installation instructions, see [SETUP.md](SETUP.md).

## Access the Application

- **App URL**: <http://localhost:8000>
- **Admin Panel**: <http://localhost:8000/admin>
- **Debugging View**: <http://localhost:6080>

### What's The Difference?

The App URL works in the browser in your host machine just like any other website.
However, the agent can't reach that browser because it's running in your container.
The [Debugging View](http://localhost:6080) has special support so the agent can use it, but it's a little ugly.

Because each has an advantage (ease of use vs agent use), we've provided both.

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

This repository is set up for an HVE coding kata (2.5 hours). See [CHALLENGES.md](CHALLENGES.md) for the full challenge description, or [CHALLENGES-v2.md](CHALLENGES-v2.md) for the v2 challenges.

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

Check the [CHALLENGES-v2.md](CHALLENGES-v2.md) files for:

- Detailed schedule with breaks
- Ticket descriptions for each HVE technique
- FHIR integration guidance
- Sample data for testing
