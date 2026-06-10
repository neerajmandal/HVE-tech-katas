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

## Industry Adapter Skills

This repo ships an **agent skill pack** at [`.github/skills/`](.github/skills/) that
adapts the same application to other industries (manufacturing, financial services,
legal, education, …) by **generating** the vertical instead of hand-editing it. The
committed baseline always stays healthcare; verticals are produced on demand.

The idea: keep the **structure** stable (model fields, portal URL names, dashboard
context keys, the `visit_type` enum) and swap the **skin** and **data**. A single
domain manifest drives all vertical display copy — `apps/core/domain.py` defines it,
a context processor injects `{{ domain }}` into every template, and `GET
/portal/domain.json` mirrors it.

| Skill | Purpose |
| --- | --- |
| [`adapt-for-industry`](.github/skills/adapt-for-industry/SKILL.md) | Generate the domain manifest (brand, role, entity terms, nav, compliance) and wire templates to it |
| [`customize-use-case`](.github/skills/customize-use-case/SKILL.md) | Generate vertical calculators + an entity-mapped synthetic `seed_<slug>` management command |
| [`validate-adaptation`](.github/skills/validate-adaptation/SKILL.md) | Read-only, architecture-aware validator; `ui_contract` catches label↔binding drift (safe on the baseline) |
| [`deploy-adaptation`](.github/skills/deploy-adaptation/SKILL.md) | Classify → validate → migrate (only if needed) → reseed → build → smoke/Playwright (owns all mutating steps) |

The agent runs the skills as a pipeline — generate the skin and data, gate on the
contract, then mutate state only once everything validates:

```mermaid
flowchart LR
    A["adapt-for-industry<br/>manifest + wire templates"] --> B["customize-use-case<br/>calculators + seed command"]
    B --> C{"validate-adaptation<br/>ui_contract · seed_contract<br/>domain_manifest"}
    C -- "0 failed" --> D["deploy-adaptation<br/>reseed → build → smoke"]
    C -- "failures" --> A
    D --> E([Adapted vertical])
```

To adapt the portal, just ask an agent — it runs the whole pipeline
(adapt → customize → validate → deploy) for you. For example, from the repo root in
[GitHub Copilot CLI](https://github.com/github/copilot-cli):

```console
$ copilot

▌ Apply the industry adapter to this repo for the manufacturing industry.

  I'll use the adapter skills in .github/skills and run them in order.

  • adapt-for-industry
    Generated apps/core/domain.py (brand, role, entity terms, compliance), wired
    the context processor and the base/portal/dashboard templates to {{ domain }},
    and served it at GET /portal/domain.json.

  • customize-use-case
    Generated apps/core/management/commands/seed_manufacturing.py — operators,
    inspection readings, work orders, and invoices mapped onto the existing models.

  • validate-adaptation
    $ python .github/skills/validate-adaptation/validate.py
    Summary: 0 failed  (ui_contract, seed_contract, domain_manifest, … pass)

  • deploy-adaptation
    Reseeded the demo DB, built Tailwind/static assets, and ran the smoke test ✓

  Done — adapted to "manufacturing". Model fields, portal URL names, routes, and
  the visit_type enum are unchanged; the committed healthcare baseline is intact.
```

The same dashboard, generated for manufacturing — the structure (model fields,
dashboard context keys, portal URL names, `visit_type` codes) is identical to the
healthcare baseline; only the display copy and seed data change:

![Manufacturing adaptation — Operations Portal dashboard](docs/screenshots/dashboard-manufacturing.png)

The agent owns every step — you never run the validator or deploy commands by
hand. `validate-adaptation` is read-only and safe to invoke at any point (the
agent calls it between generation and deploy), so you can also just ask "validate
the current adaptation" to re-check without changing anything.

See [`.github/skills/README.md`](.github/skills/README.md) for the entity-mapping
anchor, the stable-key contract, and ready-to-adapt manufacturing/finance presets.

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
