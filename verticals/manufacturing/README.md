# Manufacturing Kata — Stingray Operations Portal

> One of two industry katas in this repository — a **self-contained Django app**
> that was **generated** from the [healthcare baseline](../healthcare/) by the
> [Industry Adapter](../../industry-adapter/), not hand-built. See the
> [repository README](../../README.md) for the three-pillar overview.

A plant-operations portal built with Django 5.2 and Tailwind CSS for the HVE Tech
Kata training program. It is the healthcare portal re-skinned for the factory
floor: operators instead of patients, equipment inspections instead of lab tests,
work orders instead of doctor visits, and purchase orders instead of medical
bills. This kata focuses on building an **inspection-escalation** workflow.

![Manufacturing adaptation — Operations Portal dashboard](dashboard-manufacturing.png)

## The Problem

Operators on the line run equipment inspections, and some come back **Out of
Spec**. Today there is no structured way to act on a failed reading: the operator
radios the maintenance shed, scribbles a paper note, or waits for the next shift
standup. Failed inspections fall through the cracks, the same machine gets flagged
twice, and nobody can see whether a fix is open, in progress, or done.

**Your Mission**: Build an **escalation** feature in the operations portal so an
Out-of-Spec inspection can be turned into a tracked maintenance **work order** —
assigned to a maintenance engineer, moved through a status workflow
(open → in progress → resolved), and visible to the shift supervisor on the
dashboard.

## What's included

- ✅ Operations portal with equipment inspections and maintenance work orders
- ✅ Inspection readings flagged **In Spec / Out of Spec**
- ✅ Purchase orders for parts and services
- ✅ Admin manages operator accounts
- ✅ Authentication via django-allauth
- ✅ Responsive UI built with Tailwind CSS
- ✅ Synthetic plant-operations seed data (`seed_manufacturing`)

## Run the portal

This kata is a self-contained Django app. Run it from **this folder**:

```bash
cd verticals/manufacturing
npm run setup     # one-time: deps, Tailwind build, migrate, seed operators
npm run dev       # http://localhost:8000
```

- **App URL**: <http://localhost:8000>
- **Admin Panel**: <http://localhost:8000/admin>
- **Debugging View** (agent-accessible browser): <http://localhost:6080>
- **Test credentials**: `operator1`, `operator2`, … / `password123`

For detailed setup see [SETUP.md](SETUP.md). For agent guidance specific to this
kata (adapter guardrails, entity mapping, validation), see [AGENTS.md](AGENTS.md).

## How this kata was generated

Unlike the healthcare baseline, this kata was **not hand-built** — it was produced
by running the four adapter skills in order against the healthcare baseline. Don't
hand-edit the skin; ask an agent to run the adapter pipeline (see
[`../../industry-adapter/`](../../industry-adapter/)):

```text
adapt-for-industry  →  customize-use-case  →  validate-adaptation  →  deploy-adaptation
   manifest + wiring      seed command           ui_contract gate        reseed → build → smoke
```

The app is **structurally identical** to healthcare (model fields, dashboard
context keys, portal URL names, `visit_type` codes); only the display copy and the
seed data change. The manufacturing skin is carried by a few files inside the app:

| File | Role |
| --- | --- |
| [`apps/core/domain.py`](apps/core/domain.py) | Domain manifest — all display copy: brand, role, entity terms, nav, page meta, `visit_type` labels, home page, compliance, **accent theme**. |
| [`apps/core/management/commands/seed_manufacturing.py`](apps/core/management/commands/seed_manufacturing.py) | Entity-mapped synthetic seed: operators, inspection readings, work orders, purchase orders mapped onto the existing six models. |
| `dashboard-manufacturing.png` | Screenshot of the rendered result. |

The accent palette lives in the manifest's `theme.accent` block and is applied at
runtime — no separate CSS file. The adapter wiring
(`apps/core/context_processors.py`, `apps/core/templatetags/`,
`templates/partials/`) is the same shape every vertical uses.

### Entity mapping

The mission above builds on these re-skinned entities — the inspection that fails
(`LabTest`) becomes the trigger, and the work order (`DoctorVisit`) is what you
escalate it into.

| Model | Healthcare meaning | Manufacturing role |
| --- | --- | --- |
| `User` / `PatientProfile` | Patient | Operator |
| `LabTest` | Lab result | Equipment inspection reading (In Spec / Out of Spec) |
| `DoctorVisit` | Appointment | Maintenance work order |
| `Invoice` / `InvoiceLineItem` | Medical bill | Purchase order |

## Technology stack

- **Backend**: Django 5.2, Python 3.11
- **Frontend**: Tailwind CSS 4.1, Flowbite components
- **Database**: SQLite (development)
- **Authentication**: django-allauth

## Compliance note

Synthetic demonstration data only. Quality and safety records modeled on
ISO 9001 / OSHA / ISO 55000 asset-management practices; not a system of record.
