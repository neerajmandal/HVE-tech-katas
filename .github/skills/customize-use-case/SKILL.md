---
name: customize-use-case
description: Generate a new use case for the Stingray portal (Django 5.2 + Tailwind templates) — vertical calculators (services/finance.py function + view + URL + template + free-tools card) and an entity-mapped synthetic seed management command — while preserving model fields, dashboard context keys, URL names, and visit_type codes. Routes all migrate/reseed/build/run steps through deploy-adaptation.
---

# Customize Use Case — Stingray Portal (Django)

## Context

The Stingray portal demonstrates a patient health portal with a free-tools
section of financial calculators. A "use case" customization adds the
**vertical's calculators** and **synthetic data** on top of an industry skin
(from `adapt-for-industry`). The data lives in SQLite via the Django ORM
(`apps/core/models.py`); calculators follow a fixed, server-rendered pattern:

```
finance function (apps/core/services/finance.py)
  -> Django view (apps/core/views.py): read GET params -> call function -> context
  -> URL (apps/core/urls.py): path("free-tools/<name>/", views.<name>, name="<name>")
  -> template (templates/core/<name>.html) rendering the context
  -> card in templates/core/free-tools.html linking to the new page
```

This skill **generates** those artifacts. It does not migrate, reseed the
database, build, or run the app — that is `deploy-adaptation`.

> Note: calculators here render **server-side** from GET parameters (see the
> existing `investment_calculator` view + `templates/core/investment-calculator.html`).
> There is no JSON POST API; the "binding contract" is the dict the function
> returns ↔ the keys the template reads.

## Step 1: Read the existing patterns

- `apps/core/views.py` — `investment_calculator` (the view pattern: defaults,
  GET-param parsing in a `try/except`, call the finance function, build context,
  render) and `calculate_compound_interest` (a stub to model your function on:
  plain function, guarded divisions, returns a dict the template reads).
- `templates/core/investment-calculator.html` — the page pattern: a GET form,
  result panels, optional chart fed by a JSON-dumped `*_data` context value.
- `templates/core/free-tools.html`, `apps/core/urls.py` — where the card and
  route go.
- `apps/core/management/commands/seed_dummy_data.py` — the create/delete pattern
  to mirror in a new seed command (uses `User.objects.create_user`, bulk model
  creates, `password123`).
- `apps/core/models.py` — the six models and exact field names (the contract).

## Step 2: Gather requirements

Ask the user for:

1. Use-case slug (lowercase, words joined by underscores, e.g. `plant_ops`).
2. Which **calculators** the vertical needs: name, inputs (with units/ranges),
   the formula, and the result fields (including any series for charting).
3. Whether the existing model schema is sufficient (it almost always is — map
   onto existing fields).
4. **Seed data** scope: how many users, and how the vertical's records map onto
   `LabTest` (observations), `DoctorVisit` (interactions), and `Invoice`
   (billing). Confirm the `visit_type` code distribution.
5. Display copy for the new calculator pages and free-tools cards.

## Step 3: Generate calculators

For each calculator, generate all layers, matching the existing style:

- **`apps/core/services/finance.py`**: `def calculate_<name>(...) -> dict`.
  Create this module if absent (the baseline keeps `calculate_compound_interest`
  in `views.py`; new calculators belong in `services/finance.py`). Guard every
  division by zero. Round monetary/percent outputs sensibly. Include a
  JSON-serializable list (e.g. `breakdown`/`yearly_data`) when the template will
  chart it.
- **`apps/core/views.py`**: a `@login_required`-free public view (free tools are
  public) that parses GET params defensively, calls the function, and renders the
  template with the result keys in context.
- **`apps/core/urls.py`**: add `path("free-tools/<name>/", views.<name>, name="<name>")`.
- **`templates/core/<name>.html`**: a calculator page extending the public
  layout, following `investment-calculator.html` (GET form whose inputs are the
  function params; result panels reading the context keys).
- **`templates/core/free-tools.html`**: add a card linking to `{% url '<name>' %}`.

> Keep the function's returned dict keys identical to the context keys the
> template reads — they are the binding contract. The validator's `calculators`
> check verifies every URL resolves to a defined view and every `calculate_*`
> a view calls is defined.

See `references/GENERATION_GUIDE.md` for a worked calculator template (OEE).

## Step 4: Generate the seed command

Create `apps/core/management/commands/seed_<slug>.py`, runnable as
`uv run python manage.py seed_<slug>`, mirroring `seed_dummy_data.py`:

- Subclass `BaseCommand`; in `handle()`, delete existing rows in FK-safe order
  (`InvoiceLineItem`, `Invoice`, `DoctorVisit`, `LabTest`, `PatientProfile`, then
  the demo `User`s) before inserting — idempotent reseed.
- **Switch the persona, not just the records.** Create NEW industry logins with
  `User.objects.create_user(username="operator1", password="password123", ...)` <!-- pragma: allowlist secret -->
  and industry-appropriate `first_name`/`last_name` (e.g. "Marcus Reyes"). Do NOT
  reuse the healthcare `patient*` users — the sidebar shows `user.get_full_name`,
  so a reused patient keeps a healthcare identity on screen. State the new demo
  usernames in handoff (deploy-adaptation logs in as `operator1`, not `patient1`).
- **Re-skin every surface.** Populate `PatientProfile` (operator site/plant/badge
  metadata), `LabTest`, `DoctorVisit`, and `Invoice` + `InvoiceLineItem` (industry
  purchase orders / line items) with synthetic vertical data, mapping concepts onto
  **existing fields only** (e.g. an inspection reading → `result_value`/
  `reference_range`/`unit`, `is_abnormal` for out-of-spec). A seed that re-skins
  only labs and visits leaves the Invoices page and profile reading healthcare.
  Use only the five `visit_type` codes.
- Leave fields that don't apply to the vertical empty/None (e.g. manufacturing
  work orders leave `vitals_*` null — the UI hides empty panels).
- Print inserted counts at the end with `self.stdout.write(...)`.

> The `seed_contract` validator check parses the seed command and fails if it
> sets any field name not on a model — keep to the existing fields. FK aliases
> (`patient_id`, `user_id`, `invoice_id`, `created_by_id`) and `defaults=` are
> allowed. It also enforces a **full persona switch**: the seed must call
> `User.objects.create_user(...)` (new industry logins, not reused `patient*`)
> and reseed all five demo tables (`PatientProfile`, `LabTest`, `DoctorVisit`,
> `Invoice`, `InvoiceLineItem`) so no healthcare identity or billing leaks through.

## Step 5: Handoff

This skill writes source only. Record:

- Files created/modified and, for each calculator, the GET param names ↔ the
  result context keys (so the template binds correctly).
- That `deploy-adaptation` must run the seed command, `npm run build` (Tailwind +
  collectstatic), and smoke-test. If you added a new model field (rare),
  `deploy-adaptation` must also `makemigrations` + `migrate`.

## Step C: Validate

```bash
python .github/skills/validate-adaptation/validate.py
```

The `calculators` and `seed_contract` checks cover this skill's output. See
`../validate-adaptation/VALIDATE.md`.

## Step D: Deploy

Do not migrate, reseed, build, or run the app from this skill. Hand off to
`../deploy-adaptation/SKILL.md` for the reseed + build + smoke/Playwright run.
