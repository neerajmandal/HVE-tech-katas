# Healthcare Kata — Stingray Health Portal

> One of two industry katas in this repository — a **self-contained Django app**
> and the **baseline** the Industry Adapter starts from. See the
> [repository README](../../README.md) for the full three-pillar overview, and
> [`../manufacturing/`](../manufacturing/) for the adapted vertical.

A patient portal built with Django 5.2 and Tailwind CSS for the HVE Tech Kata
training program. This kata focuses on building a **secure messaging** feature
for patient–doctor communication.

![Healthcare patient portal dashboard](dashboard-healthcare.png)

## The Problem

Patients at our clinic have no direct way to communicate with their assigned
doctor through the portal. For non-urgent questions about health, medications,
or appointments they must call and wait on hold, leave a voicemail, schedule an
unnecessary visit, or send email that gets lost in a shared inbox.

**Your Mission**: Build a secure messaging feature within the patient portal
that enables patients to message their doctors, doctors to respond, and admins
to manage assignments.

## What's included

- ✅ Patient portal with appointments and lab results
- ✅ Patients assigned to a primary doctor
- ✅ Admin manages patient accounts
- ✅ Authentication via django-allauth
- ✅ Responsive UI built with Tailwind CSS
- ✅ Sample FHIR datasets under [`data/`](data/)

## Run the baseline

This kata is a self-contained Django app. Run it from **this folder**:

```bash
cd verticals/healthcare
npm run setup     # one-time: data, deps, Tailwind build, migrate, seed
npm run dev       # http://localhost:8000
```

- **App URL**: <http://localhost:8000>
- **Admin Panel**: <http://localhost:8000/admin>
- **Debugging View** (agent-accessible browser): <http://localhost:6080>
- **Test credentials**: `patient1`–`patient20` / `password123`

For detailed setup see [SETUP.md](SETUP.md). For the 2.5-hour kata schedule
and tickets see [CHALLENGES.md](CHALLENGES.md) / [CHALLENGES-v2.md](CHALLENGES-v2.md).

## No domain manifest (baseline)

The healthcare baseline ships **without** a domain manifest — its display copy is
the templates' default. The adapter *generates* a manifest when re-skinning to
another vertical; see [`../manufacturing/apps/core/domain.py`](../manufacturing/apps/core/domain.py)
for what that looks like. The baseline maps onto the same six models, dashboard
context keys, portal URL names, and `visit_type` enum codes that every vertical
preserves.

## Technology stack

- **Backend**: Django 5.2, Python 3.11
- **Frontend**: Tailwind CSS 4.1, Flowbite components
- **Database**: SQLite (development)
- **Authentication**: django-allauth
- **Standards**: FHIR (Fast Healthcare Interoperability Resources)
