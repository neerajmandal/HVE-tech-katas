# Agent Guidance for Stingray Health Portal

This document provides guidance for agents working on the Stingray Health Portal project—a Django-based patient health portal with Tailwind CSS frontend.

## Project Overview

**Tech Stack:**
- Backend: Django 5.2 + Python 3.11+
- Frontend: Tailwind CSS 4.1 + Flowbite components
- Database: SQLite (development)
- Package Managers: pip + venv (Python), npm (Node.js)

> **Note:** All Python commands below assume the project virtual environment (`.venv`) is activated. Activate it with:
>
> - macOS / Linux / WSL: `source .venv/bin/activate`
> - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
> - Windows (Git Bash): `source .venv/Scripts/activate`

**Key Apps:**
- `apps.core`: Main portal features (patient dashboard, lab tests, doctor visits, invoices)
- Authentication: Django Allauth

To setup the project from scratch, run `npm run setup`.

## Running the Application

Start the Development Server with `npm run dev`, server runs at **http://localhost:8000** with hot-reload enabled.

Check listening ports before attempting to launch the server yourself in case the user already has it running.

### Run Migrations

After editing database migrations, run migrations with `python manage.py migrate` (or `npm run migrate`).

This runs the complete setup: downloads sample data, installs dependencies, compiles Tailwind, applies migrations, and seeds dummy data.

## Login Credentials

### Test Patient Accounts

The `seed_dummy_data` management command creates 20 test users (run automatically during setup):

- **Usernames:** `patient1`, `patient2`, ..., `patient20`
- **Password:** `password123` (same for all test accounts)

### Admin Access

The Django admin panel is available at **http://localhost:8000/admin/**. Admin credentials can be created with:

```bash
python manage.py createsuperuser
```

## Application Structure

### URL Routing

```
http://localhost:8000/                    # Home page
http://localhost:8000/portal/             # Patient dashboard (requires login)
http://localhost:8000/portal/lab-tests/   # Lab tests (requires login)
http://localhost:8000/portal/visits/      # Doctor visits (requires login)
http://localhost:8000/invoices/           # Invoices list (requires login)
http://localhost:8000/accounts/login/     # Login page
http://localhost:8000/accounts/signup/    # Sign-up page
http://localhost:8000/admin/              # Django admin
```

### Key Files and Directories

```
StingrayHealthPortal/          # Django project settings
├── settings.py               # Django configuration
├── urls.py                   # Main URL routing
└── wsgi.py / asgi.py        # Application entry points

apps/                          # Django applications
├── core/                      # Main portal app
│   ├── models.py            # application models
│   ├── views.py             # View functions for portal pages
│   ├── urls.py              # Core app URL routing
│   └── migrations/          # Database migrations
templates/                     # HTML templates
static/                        # Static assets
```

## Playwright Testing Guide

Use Playwright for end-to-end testing of the patient portal.

### Test Environment Setup

Before running Playwright tests:

1. **Ensure server is running:**
2. **Create a test user** (if not already seeded)
3. **Install Playwright** (if not already present):
   ```bash
   npm install --save-dev @playwright/test
   ```

### Example Playwright Test

```javascript
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8000';
const TEST_USERNAME = 'patient1';
const TEST_PASSWORD = 'password123';

test.describe('Patient Portal', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${BASE_URL}/accounts/login/`);
    await page.fill('input[name="login"]', TEST_USERNAME);
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button:has-text("Sign In")');
    await page.waitForNavigation();
  });

  test('should display patient dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/portal/`);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText('Dashboard');
  });

  test('should navigate to lab tests', async ({ page }) => {
    await page.goto(`${BASE_URL}/portal/lab-tests/`);
    await expect(page).toHaveTitle(/Lab Tests/i);
  });

  test('should navigate to doctor visits', async ({ page }) => {
    await page.goto(`${BASE_URL}/portal/visits/`);
    await expect(page).toHaveTitle(/Doctor Visits/i);
  });
});
```

### Common Testing Selectors

- **Login form:** `input[name="login"]`, `input[name="password"]`, `button:has-text("Sign In")`
- **Navigation links:** Look for `<a>` tags with `href` attributes
- **Headings:** `h1`, `h2`, `h3` for page titles
- **Tailwind/Flowbite components:** Use data attributes or class-based selectors

### Playwright validation best practices

- Visually validate in the browser, not just console logs. Render bugs can hide in executed code paths.
- Use Playwright to screenshot pages and compare against expectations.
- Check the browser console for JavaScript errors: Open DevTools → Console tab.
- For debugging, you can query the Django shell: `python manage.py shell`

## Common Development Tasks

```bash
npm run lint # Lint frontend (TypeScript/JavaScript)
npm run typecheck # Type check
npm run autofix:py # Auto-fix Python code
npm run autofix:ts # Auto-fix Typescript code
npm run autofix # Auto-fix all code
npm run build # Build Tailwind CSS and collect static assets
python manage.py makemigrations # Create a new migration
python manage.py migrate # Apply migrations
python manage.py showmigrations # Show migration status
python manage.py seed_dummy_data # Seed sample FHIR data and dummy patients
```

## Debugging Tips

### Database Inspection

To inspect the SQLite database:

```bash
# Open Django shell
python manage.py shell

# Query users
from django.contrib.auth.models import User
list(User.objects.values('username', 'email'))
```

### Reset Database (Development)

To start fresh remove `db.sqlite3` and re-run setup.

## General Guidelines

**Code Quality & Practices:**
- Do not add untracked files unless you created them as part of the feature/fix.
- Avoid unnecessary comments like "foo now handles bar" or "foo now lives in bar"—the git history provides this context.
- When adding debug prints, prefix them with a `// Debug:` comment for easy identification and removal later.
- Prefer using existing libraries and patterns in the codebase over custom solutions.
- When refactoring or removing code, grep for all remaining references to ensure clean removal.

**Django Migrations:**
- Always create migrations when models change: `python manage.py makemigrations`
- Review migration files before applying them.
- Test migrations in a fresh database: `rm db.sqlite3 && npm run setup`

**Static Files:**
- Static files must be collected after CSS changes: `npm run collectstatic`
- Do not manually edit `static/output.css`—it's generated from `static/input.css` by Tailwind.

**Important File Locations:**
- Test users: Created by `seed_dummy_data` command (patient1–patient20, password: password123)
- Sample FHIR data: `data/sample-bulk-fhir-datasets-10-patients/`
- Django settings: `StingrayHealthPortal/settings.py`
- Core models: `apps/core/models.py`

## Landing the Plane (Session Completion)

When finishing work, complete these steps in order. **Work is NOT done until all steps are complete.**

1. **Run quality gates:**
   ```bash
   npm run lint
   npm run typecheck
   npm run autofix:py
   ```

2. **Test the application:**
   - Verify the server starts: `npm run dev`
   - Manually test your feature in the browser at `http://localhost:8000`
   - Run Playwright tests if applicable

3. **Database state:**
   - Ensure all migrations are created and committed
   - Verify migrations apply cleanly: `rm db.sqlite3 && python manage.py migrate`

4. **Commit your work** (AFTER testing):**
   ```bash
   git add <files>
   git commit -m "feat(component): description of changes"
   ```
   Use conventional commit format: `feat(...)`, `fix(...)`, `refactor(...)`, etc.
   Example: `feat(messaging): add patient-to-doctor message threading`

5. **Push to remote:**
   ```bash
   git pull --rebase
   git push
   git status  # Verify "up to date with origin"
   ```

6. **Clean up:**
   - Remove debug prints and comments
   - Close any Playwright browser instances
   - Verify all changes are committed and pushed
