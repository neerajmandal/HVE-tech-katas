---
name: deploy-adaptation
description: Safely validate, classify, migrate, reseed, build, and smoke-test a Stingray industry adaptation on the Django + Tailwind-templates stack. Owns every mutating step — database migrate/reseed, Tailwind build, and running the app — that the generation skills defer.
---

# Deploy Adaptation — Stingray Portal (Django)

## Context

This app runs locally: a Django dev server on `:8000` (`npm run dev` →
`manage.py runserver`) over a SQLite file (`db.sqlite3`). Tailwind CSS is compiled
from `static/input.css` to `static/output.css` (`npm run build:css`) and collected
with `collectstatic` (`npm run build:static`); `npm run build` does both. There is
no cloud deployment in this repo.

Use this skill **after** `adapt-for-industry` and/or `customize-use-case` have
produced reviewed source changes. This is the only skill that mutates state —
migrating, reseeding the database, building, or starting the server.

## Step 1: Read the change evidence

- The generated/edited files from the adaptation (manifest `apps/core/domain.py`,
  `context_processors.py`, the `settings.py` registration line, `domain_json`
  view/URL, calculators, seed command, wired templates).
- `.github/skills/README.md` (the stable-key contract table).
- `package.json` (scripts: `dev`, `build`, `build:css`, `build:static`, `lint`,
  `typecheck`), `StingrayHealthPortal/settings.py` (context processors, apps).
- `apps/core/management/commands/seed_<slug>.py` (the reseed entry point).

If a referenced file is missing or stale, pause and report it instead of
inventing steps.

## Step 2: Classify the change

Use exactly one category:

- `display-only` — manifest copy, template strings, `visit_type` labels, nav
  labels. No model or context-key change.
- `data-only` — a new/edited `seed_<slug>.py` command (data VALUES only).
- `backend-only` — calculators (`services/finance.py` + view + URL), the
  `domain_json` view, context processor.
- `frontend-only` — calculator templates, cards, manifest template wiring.
- `mixed` — more than one of the above, or any change touching a stable binding
  (model field, context key, URL name, `visit_type` code) — which also requires a
  migration. Treat uncertainty as mixed.

## Step 3: Preflight

Confirm: the working tree is the intended adaptation, the Python env is synced
(`uv sync` if needed), and `node_modules` is installed in this checkout
(`npm install` if not — it is git-ignored and may be absent after a fresh clone).
The committed `db.sqlite3` will be **overwritten** by a reseed — that is expected
for the demo DB; never point a reseed at real data.

## Step 4: Validate before mutating

Run the validator and stop on any failure:

```bash
python .github/skills/validate-adaptation/validate.py
```

Also run the static gates (no server needed):

```bash
npm run typecheck
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run   # fails if a model changed without a migration
```

The `ui_contract` and `domain_manifest` checks must pass for any display change;
`calculators` and `seed_contract` for backend/data changes.

## Step 5: Migrate (only for a `mixed` change that added a model field)

Display/data/calculator adaptations need **no** migration (they reuse the
existing schema). Only if the vertical genuinely added a model field:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

## Step 6: Reseed the demo database

Only when a seed command changed or the vertical's data must be loaded:

```bash
uv run python manage.py seed_<slug>
```

This deletes the demo rows and inserts the vertical's synthetic data (idempotent).
Reverting to healthcare = `git restore db.sqlite3`, or rerun
`manage.py seed_dummy_data`.

## Step 7: Build and activate

```bash
npm run build         # Tailwind CSS + collectstatic
npm run dev           # http://localhost:8000  (manage.py runserver)
```

> Check listening ports first — the user may already be running the server. On
> Windows, get the PID then `Stop-Process -Id <pid>`.

## Step 8: Smoke-test

Smoke checks that prove the adaptation is visible:

- `GET http://localhost:8000/portal/domain.json` returns the active vertical manifest.
- Log in with a seeded demo user (e.g. `operator1 / password123`).
- The portal sidebar (`portal_base.html`) shows the re-skinned brand, suffix,
  role, nav group + labels, and assistant button.
- Dashboard stat cards, list pages, and badges show vertical copy bound to real
  data (no empty/placeholder values, no leftover healthcare strings).
- Each new calculator page returns a result matching the finance function value
  for the same inputs.

Prefer **Playwright** for visual confirmation (this repo runs Chromium via
`npm run install:browser`; the AGENTS.md test pattern logs in, screenshots key
pages, and asserts a rendered headline). See `references/DEPLOYMENT_GUIDE.md` for
the smoke-check checklist and a Playwright outline. Close any headed browser when
done.

## Step 9: Roll back

Roll back source via Git (`git restore` of wired templates + `settings.py`, delete
generated files: `apps/core/domain.py`, `apps/core/context_processors.py`,
`apps/core/services/finance.py` calculators, calculator templates,
`management/commands/seed_<slug>.py`) and the demo DB via `git restore db.sqlite3`.
Because adaptations are sibling files plus mechanical string swaps, reverting to
the healthcare baseline is clean.

Detailed classification and command planning: `references/DEPLOYMENT_GUIDE.md`.
