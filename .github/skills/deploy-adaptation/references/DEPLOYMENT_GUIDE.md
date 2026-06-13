# Deployment Guide — deploy-adaptation

Command planning and smoke-check detail for activating a Stingray industry
adaptation locally (Django). This skill owns all mutating steps; the generation
skills only write source.

## Environment facts

- Backend: Django dev server on `:8000` (`npm run dev` → `manage.py runserver`),
  SQLite at `db.sqlite3` (`StingrayHealthPortal/settings.py`), Python managed
  with `uv` (`pyproject.toml`).
- Frontend: server-rendered Django templates + Tailwind. CSS compiles from
  `static/input.css` → `static/output.css` (`npm run build:css`) and is collected
  with `collectstatic` (`npm run build:static`); `npm run build` runs both.
- The committed `db.sqlite3` is the demo database. Reseeds overwrite it; runtime
  writes (e.g. `last_login`) make it show as git-dirty — expected.
- `node_modules` and the Python env are git-ignored; install them in a fresh
  checkout before building/running (`npm install`, `uv sync`).

## Classification → required steps

| Category | Validate | Migrate | Reseed DB | Build CSS | Run + smoke |
| --- | --- | --- | --- | --- | --- |
| display-only | yes (`ui_contract`) | no | no | yes | yes (visual) |
| data-only | yes (`seed_contract`) | no | yes | no | yes (data shows) |
| backend-only | yes (`calculators`) | no | no | no | yes (page + value) |
| frontend-only | yes | no | no | yes | yes (visual) |
| mixed | all checks | only if a model field was added | as needed | yes | yes (full) |

> Display/data/calculator adaptations reuse the existing schema, so they need
> **no migration**. Only a genuine new model field triggers makemigrations/migrate.

## Command sequence

```bash
# 0. Install deps if missing
uv sync
npm install

# 1. Validate (stop on failure)
python .github/skills/validate-adaptation/validate.py

# 2. Static gates
npm run typecheck
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run

# 3. Migrate (only if a model field was added)
uv run python manage.py makemigrations
uv run python manage.py migrate

# 4. Reseed demo DB (only if a seed command changed)
uv run python manage.py seed_<slug>

# 5. Build CSS + collect static
npm run build

# 6. Run
npm run dev          # http://localhost:8000
```

> Check listening ports before starting the server — the user may already be
> running it. On Windows, get the PID first, then `Stop-Process -Id <pid>`.

## Smoke-check checklist

1. `curl http://localhost:8000/portal/domain.json` → the active vertical manifest
   (industry, brand, entities, compliance).
2. Log in via the UI with a seeded demo user (e.g. `operator1 / password123`) at
   `http://localhost:8000/accounts/login/`.
3. Sidebar: brand suffix, role label, nav group + labels, and the assistant
   button are the vertical's (no "Health Portal" / "Nurse AI" leftovers).
4. Dashboard: stat-card labels, section headings, and badges read vertical copy
   and show real numbers (not blank).
5. List pages (Inspections/Work Orders, etc.): titles, column/label copy, and
   empty-state text are vertical; rows render real seeded data.
6. Each new calculator page returns a result; the rendered headline equals the
   `calculate_<name>` function value for the same inputs.
7. No leftover healthcare strings on any re-skinned surface (the `ui_contract`
   check enforces this for the wired templates).
8. Accent theme: the brand accent (sidebar suffix, active nav, stat icons, View
   All links, filter chips, avatar background) is the vertical's color, not teal —
   driven by the manifest `theme` block (the `theme_contract` check enforces the
   wiring; the screenshot confirms it visually). If everything is still teal,
   `npm run build` didn't pick up the `@theme` scale or the `_theme_style` partial
   isn't included in the root layouts.

## Playwright outline

The repo's established pattern (AGENTS.md): log in, navigate, screenshot, and
assert a rendered value. Run from a checkout with Playwright installed
(`npm run install:browser` if needed).

```js
const { test, expect } = require("@playwright/test");
const BASE = "http://localhost:8000";

test("vertical renders", async ({ page, request }) => {
  await page.goto(`${BASE}/accounts/login/`);
  await page.fill('input[name="login"]', "operator1");
  await page.fill('input[name="password"]', "password123");
  await page.click('button:has-text("Sign In")');
  await page.waitForURL("**/portal/**");
  await expect(page.locator("aside")).toContainText("Operations Portal");
  await page.screenshot({ path: "dashboard.png", fullPage: true });

  // manifest parity: the JSON endpoint reflects the active vertical
  const domain = await (await request.get(`${BASE}/portal/domain.json`)).json();
  expect(domain.industry).toBe("manufacturing");
});
```

Close any headed browser when finished so it does not interfere with later runs.

## Rollback

- Source: `git restore` the wired templates + `StingrayHealthPortal/settings.py`,
  and `git rm`/delete the generated files (`apps/core/domain.py`,
  `apps/core/context_processors.py`, `apps/core/services/finance.py` calculators,
  `templates/core/<name>.html`, `apps/core/management/commands/seed_<slug>.py`,
  and the `domain_json` view/URL additions).
- Database: `git restore db.sqlite3` to return to the committed healthcare demo
  data, or rerun `manage.py seed_dummy_data`.
- CSS: **rerun `npm run build` after restoring the templates.** `static/output.css`
  is gitignored, so `git restore` leaves the prior vertical's compiled CSS in place.
  Tailwind v4 only emits the utilities its content scan finds in the *current*
  templates, so a stale build drops baseline-only classes (landing hero gradient,
  primary CTA button background, etc.) and the page renders with the wrong/broken
  colors even though the templates are correct. Rebuild from the healthcare-default
  `static/input.css`, then verify the landing page renders the teal hero.
