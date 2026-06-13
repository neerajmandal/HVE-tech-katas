# Stingray Industry-Adapter Skill Pack (Django)

This repository ships as a **healthcare** patient portal (Django 5.2 backend with
server-rendered Tailwind templates). These skills let an agent **adapt the same
application to another industry** — manufacturing, financial services, legal,
education, energy, and so on — by *generating* the vertical instead of
hand-editing it.

The skills are the product. Running a skill **generates** the domain manifest,
the vertical calculators, the synthetic seed data, and the template wiring. The
committed baseline always stays healthcare; adaptations are produced on demand.

## The adapter idea

Keep the **structure** stable; swap the **skin** and the **data**.

| Layer | Stays stable (contract) | Generated/adapted per vertical |
| --- | --- | --- |
| Models (`apps/core/models.py`) | model + field names | row VALUES |
| Views (`apps/core/views.py`) | dashboard context keys, `visit_type` enum codes | — |
| URLs (`apps/core/urls.py`) | URL names + paths | — |
| Templates (`templates/`) | `{% url %}` targets, data bindings | brand, labels, titles, copy |
| Tools (`services/finance.py`, views, templates) | view/URL/context shape pattern | which calculators exist |

A single **domain manifest** is the source of truth for all vertical display
copy. It lives at `apps/core/domain.py` (a `DOMAIN` dict) and is injected into
**every** template by a context processor (`apps/core/context_processors.py`),
so templates read `{{ domain.brand.name }}`, `{{ domain.nav.records.label }}`,
etc. A parity endpoint `GET /portal/domain.json` returns the same dict for
smoke-testing. Because display labels are bound to stable keys through the
manifest, a re-skin can never silently break a data binding — and the
`ui_contract` validator check proves it.

## Entity-mapping anchor

Every vertical maps onto the existing six tables. Do not rename fields; map the
concept onto the field.

| Model | Healthcare meaning | Generic role | e.g. Manufacturing | e.g. Finance |
| --- | --- | --- | --- | --- |
| `User` (auth) | Patient login | The person who signs in | Operator | Client |
| `PatientProfile` | Patient profile | Per-user profile/affiliation | Operator / site | Account holder |
| `LabTest` | Lab result | A measured **observation** (name, category, value, reference range, unit, normal/abnormal, status) | Equipment inspection reading | Portfolio metric reading |
| `DoctorVisit` | Appointment | A scheduled **interaction/event** (provider, specialty, type, reason, notes, follow-up) | Maintenance work order | Advisory session |
| `Invoice` / `InvoiceLineItem` | Medical bill | A **billing document** with line items | Purchase order | Statement |

> `LabTest.is_abnormal` is the universal "outside expected range" flag
> (Out of Spec / Breach / At Risk). `DoctorVisit.visit_type` is a **closed
> enum** — `checkup`, `follow_up`, `urgent`, `specialist`, `preventive` — whose
> labels (the second element of each `VISIT_TYPE_CHOICES` tuple) are re-skinned
> per vertical but whose codes never change.

## Skills (run in order)

1. **`adapt-for-industry/`** — choose a target industry; generate the domain
   manifest (brand, role, entity terms, nav labels, theme, compliance), register
   the context processor, wire the templates to it, and stand up
   `GET /portal/domain.json`.
2. **`customize-use-case/`** — generate the vertical's calculators
   (`services/finance.py` + view + URL + template + free-tools card) and an
   entity-mapped synthetic seed management command.
3. **`validate-adaptation/`** — read-only, architecture-aware validator. The
   `ui_contract` check catches display-label-vs-binding drift. Safe to run on the
   baseline (vertical checks `skip` until an adaptation exists).
4. **`deploy-adaptation/`** — classify the change, validate, reseed the demo DB,
   build Tailwind, and run the smoke/Playwright checks that prove the new
   vertical renders. Owns all mutating steps.

## Guardrails the skills enforce

- **Sibling, not overwrite.** Generate into new files (manifest, context
  processor, seed command, calculator template); the only edits to existing
  files are mechanical string swaps to `{{ domain.* }}` and one settings line.
  Reverting an adaptation = `git restore` + delete the generated files.
- **Stable keys, swapped values.** Re-skin display copy and data values; keep
  model fields, dashboard context keys, URL names, and the `visit_type` enum
  codes stable.
- **Synthetic data only.** Seed data is fabricated for demonstration. Each
  vertical carries a compliance note (see each skill's examples).
- **Generation is separate from mutation.** `adapt-for-industry` and
  `customize-use-case` only write source files; `deploy-adaptation` is the only
  skill that migrates, reseeds the database, builds, or runs the app.

## Quick reference

```bash
# Validate (safe on the baseline)
python .github/skills/validate-adaptation/validate.py
python .github/skills/validate-adaptation/validate.py --self-test

# Apply migrations + (re)seed + build + run after an adaptation is generated
uv run python manage.py migrate
uv run python manage.py seed_<slug>     # generated by customize-use-case
npm run build                           # Tailwind CSS + collectstatic
npm run dev                             # http://localhost:8000

# Test login (baseline seed): patient1 .. patient20 / password123
```
