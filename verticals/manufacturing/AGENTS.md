# Agent Guidance for Stingray Operations Portal (Manufacturing Kata)

This document provides guidance for agents working on the **Manufacturing Kata**—a
Django-based plant operations portal with a Tailwind CSS frontend.

> **This kata is a generated adaptation.** It was produced from the
> [healthcare baseline](../healthcare/) by the
> [Industry Adapter](../../industry-adapter/), not hand-built. It is
> **structurally identical** to healthcare: the same `apps/core` models, the same
> portal URL names, the same dashboard context keys, and the same `visit_type`
> enum codes. Only the **display copy** (via `apps/core/domain.py`) and the
> **seed data** differ. When changing this app, preserve those structural keys—
> re-skin through the manifest, do not rename model fields, URL names, context
> keys, or `visit_type` codes.

## Project Overview

**Tech Stack:**

- Backend: Django 5.2 + Python 3.11+
- Frontend: Tailwind CSS 4.1 + Flowbite components
- Database: SQLite (development)
- Package Managers: uv (Python), npm (Node.js)

**Key Apps:**

- `apps.core`: Main portal features (operator dashboard, inspections, work orders, purchase orders)
- Authentication: Django Allauth

**The manufacturing skin lives in a few files inside the app:**

- `apps/core/domain.py` — the domain manifest: all display copy (brand, role, entity terms, nav, page meta, `visit_type` labels, home page, compliance, accent theme).
- `apps/core/context_processors.py` — injects `{{ domain }}` into every template; `GET /portal/domain.json` mirrors it.
- `apps/core/management/commands/seed_manufacturing.py` — entity-mapped synthetic seed (operators, inspection readings, work orders, purchase orders) onto the existing six models.

To set up the project from scratch, run `npm run setup` (from this folder).

When browser debugging or visual validation is needed on macOS or Windows, prefer the existing devcontainer.
The supported workflow keeps Django, Playwright, and Chromium inside the container and exposes the visible desktop to the host on port 6080.

## Running the Application

Start the Development Server with `npm run dev`, server runs at **<http://localhost:8000>** with hot-reload enabled.

Check listening ports before attempting to launch the server yourself in case the user already has it running.

### Run Migrations

After editing database migrations, run migrations with `uv run python manage.py migrate`.

## Login Credentials

### Test Operator Accounts

The `seed_manufacturing` management command creates demo operators (run automatically during `npm run setup`):

- **Usernames:** `operator1`, `operator2`, …
- **Password:** `password123` (same for all test accounts)

### Admin Access

The Django admin panel is available at **<http://localhost:8000/admin/>**. Admin credentials can be created with:

```bash
uv run python manage.py createsuperuser
```

## Application Structure

### URL Routing

The URL **names and paths are identical to healthcare**; only the displayed
labels change (lab tests → equipment inspections, doctor visits → work orders,
invoices → purchase orders).

```text
http://localhost:8000/                    # Home page
http://localhost:8000/portal/             # Operator dashboard (requires login)
http://localhost:8000/portal/lab-tests/   # Equipment inspections (requires login)
http://localhost:8000/portal/visits/      # Maintenance work orders (requires login)
http://localhost:8000/invoices/           # Purchase orders (requires login)
http://localhost:8000/portal/domain.json  # Domain manifest as JSON
http://localhost:8000/accounts/login/     # Login page
http://localhost:8000/accounts/signup/    # Sign-up page
http://localhost:8000/admin/              # Django admin
```

### Entity Mapping

| Model | Healthcare meaning | Manufacturing role |
| --- | --- | --- |
| `User` / `PatientProfile` | Patient | Operator |
| `LabTest` | Lab result | Equipment inspection reading (In Spec / Out of Spec) |
| `DoctorVisit` | Appointment | Maintenance work order |
| `Invoice` / `InvoiceLineItem` | Medical bill | Purchase order |

### Key Files and Directories

```text
StingrayHealthPortal/          # Django project settings (name retained from baseline)
├── settings.py                # Django configuration
├── urls.py                    # Main URL routing
└── wsgi.py / asgi.py          # Application entry points

apps/                          # Django applications
├── core/                      # Main portal app
│   ├── models.py              # Application models (shared schema with healthcare)
│   ├── domain.py              # Manufacturing domain manifest (the skin)
│   ├── views.py               # View functions for portal pages
│   ├── urls.py                # Core app URL routing
│   └── management/commands/   # seed_manufacturing.py (operators + plant data)
templates/                     # HTML templates (read the manifest via {{ domain }})
static/                        # Static assets
```

## Playwright Testing Guide

Use Playwright for end-to-end testing of the operations portal.

### Test Environment Setup

Before running Playwright tests:

1. **Ensure server is running.**
2. **Seed operators** (done by `npm run setup`).
3. **Install Playwright** (if not already present):

```bash
npm run install:browser
```

In the devcontainer, one-time provisioning already installs Chromium and its Linux dependencies.
Use these commands from an in-container terminal when you need a visible browser session:

```bash
npm run browser:open
npm run browser:codegen
```

### Example Playwright Test

```javascript
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8000';
const TEST_USERNAME = 'operator1';
const TEST_PASSWORD = 'password123';

test.describe('Operations Portal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/accounts/login/`);
    await page.fill('input[name="login"]', TEST_USERNAME);
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button:has-text("Sign In")');
    await page.waitForNavigation();
  });

  test('should display operator dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/portal/`);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText('Dashboard');
  });
});
```

### Common Testing Selectors

- **Login form:** `input[name="login"]`, `input[name="password"]`, `button:has-text("Sign In")`
- **Navigation links:** Look for `<a>` tags with `href` attributes
- **Headings:** `h1`, `h2`, `h3` for page titles
- **Tailwind/Flowbite components:** Use data attributes or class-based selectors

### Playwright Validation Best Practices

- Visually validate in the browser, not just console logs. Render bugs can hide in executed code paths.
- In the devcontainer, advise the user to check the browser through the noVNC desktop on port 6080 so actions remain observable while Chromium stays inside the container.
- Use Playwright to screenshot pages and compare against expectations.
- For debugging, query the Django shell with `uv run python manage.py shell`.

### Browser Debugging Guardrails

- Treat port 6080 as a local development surface. Do not intentionally expose it outside trusted localhost forwarding.
- On Windows, prefer Docker Desktop with WSL2.
- Close headed browser windows when you finish validation so they do not interfere with later runs.

## Common Development Tasks

```bash
npm run lint # Lint frontend (TypeScript/JavaScript)
npm run typecheck # Type check
npm run autofix:py # Auto-fix Python code
npm run autofix:ts # Auto-fix Typescript code
npm run autofix # Auto-fix all code
npm run build # Build Tailwind CSS and collect static assets
uv run python manage.py makemigrations # Create a new migration
uv run python manage.py migrate # Apply migrations
uv run python manage.py showmigrations # Show migration status
uv run python manage.py seed_manufacturing # Seed operators + plant operations data
```

## Adapter Guardrails (manufacturing-specific)

- **Re-skin through the manifest, not the templates.** Display copy belongs in
  `apps/core/domain.py`; templates read it via `{{ domain }}`.
- **Never rename the frozen contract:** model fields, portal URL names, dashboard
  context keys, or the five `visit_type` codes. The validator
  (`../../.github/skills/validate-adaptation/validate.py`) enforces this; run it
  with `--app-root verticals/manufacturing` from the repo root.
- **`visit_type` labels** are re-skinned via the manifest `visit_type_labels`
  rendered with the `domain_extras` `dict_get` filter—never via
  `get_visit_type_display` or by editing model `VISIT_TYPE_CHOICES`.
- **Accent theming** is declared via `@theme` in `static/input.css`; after theme
  changes run `npm run build` (the generated `static/output.css` is gitignored).

## General Guidelines

**Code Quality & Practices:**

- Do not add untracked files unless you created them as part of the feature/fix.
- Avoid unnecessary comments like "foo now handles bar"—the git history provides this context.
- When adding debug prints, prefix them with a `// Debug:` comment for easy identification and removal later.
- Prefer using existing libraries and patterns in the codebase over custom solutions.
- When refactoring or removing code, grep for all remaining references to ensure clean removal.

**Django Migrations:**

- Always create migrations when models change: `uv run python manage.py makemigrations`
- Review migration files before applying them.
- Test migrations in a fresh database: `rm db.sqlite3 && npm run setup`

**Static Files:**

- Static files must be collected after CSS changes: `npm run collectstatic`
- Do not manually edit `static/output.css`—it's generated from `static/input.css` by Tailwind.
- Lists should start with a hyphen, not an asterisk.

**Important File Locations:**

- Test users: Created by `seed_manufacturing` (operator1…, password: password123)
- Domain manifest: `apps/core/domain.py`
- Django settings: `StingrayHealthPortal/settings.py`
- Core models: `apps/core/models.py`

**Browsers:**

- Do not use the VSCode integrated browser.
- If the user wants to manipulate the browser directly, default to references to the forwarded port <http://localhost:8000>.
- If the user wants the agent to manipulate the browser, leverage the Chromium instance at <http://localhost:6080>.

## Landing the Plane (Session Completion)

When finishing work, complete these steps in order. **Work is NOT done until all steps are complete.**

1. **Run quality gates:**

   ```bash
   npm run lint
   npm run typecheck
   npm run autofix:py
   ```

2. **Validate the adaptation** (from the repo root):

   ```bash
   python .github/skills/validate-adaptation/validate.py --app-root verticals/manufacturing
   ```

3. **Test the application:**
   - Verify the server starts: `npm run dev`
   - Manually test your feature in the browser at `http://localhost:8000`
   - Run Playwright tests if applicable

4. **Database state:**
   - Ensure all migrations are created and committed
   - Verify migrations apply cleanly: `rm db.sqlite3 && uv run python manage.py migrate`

5. **Commit your work** (AFTER testing) using conventional commit format:
   `feat(...)`, `fix(...)`, `refactor(...)`, etc.

6. **Clean up:**
   - Remove debug prints and comments
   - Close any Playwright browser instances
   - Verify all changes are committed
