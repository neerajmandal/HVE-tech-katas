---
name: validate-adaptation
description: Read-only, architecture-aware validator for a Stingray industry adaptation on the Django + Tailwind-templates stack. Proves the domain manifest is wired (context processor registered, nav names resolve), display copy has not drifted from data bindings (ui_contract), seed commands touch only existing model fields, and the six-table schema, dashboard context keys, and visit_type codes stay stable. Safe to run on the healthcare baseline — adaptation-dependent checks skip until an adaptation exists.
---

# Validate Adaptation — Stingray Portal (Django)

## Context

This app is a Django 5.2 patient portal with server-rendered Tailwind templates.
The models live in `apps/core/models.py`; the views build template context in
`apps/core/views.py`; the display surfaces are Django templates under
`templates/`. Industry adaptations re-skin **display copy and data VALUES**
through a domain manifest (`apps/core/domain.py`) injected into every template by
a context processor, while preserving model fields, URL names, dashboard context
keys, and the `visit_type` enum codes.

`validate.py` is the read-only gate that proves an adaptation kept those
contracts. It never mutates state and is safe on the baseline.

## When to use

- After `adapt-for-industry` or `customize-use-case` generates source.
- Before `deploy-adaptation` runs any mutating step.
- Any time you want to confirm the baseline is intact (`Summary: 0 failed`).

## Run it

```bash
# All checks, from the repo root
python .github/skills/validate-adaptation/validate.py

# Targeted checks
python .github/skills/validate-adaptation/validate.py --check ui_contract --check seed_contract

# Validator self-tests (reads no app files)
python .github/skills/validate-adaptation/validate.py --self-test
```

Exit code is `0` when no non-skipped check fails, `1` otherwise. Stop and fix on
any `FAIL` before deploying.

## What each check proves

See `VALIDATE.md` for the full table. The adaptation-critical checks:

- **domain_manifest** — the generated `DOMAIN` dict is returned by a registered
  context processor and its nav targets resolve to real `{% url %}` names.
- **ui_contract** — every wired template reads `domain.*` and contains no
  leftover hardcoded healthcare strings (catches half-finished re-skins).
- **theme_contract** — per-industry accent theming is wired: manifest `theme`
  block, the `@theme` accent scale in `input.css`, the `_theme_style` override
  partial included in both root layouts, and no hardcoded `teal-*`/`cyan-*` brand
  classes left in themed templates.
- **seed_contract** — generated `seed_<slug>` commands set only existing model
  fields and use the five `visit_type` codes.
- **schema_integrity / api_contract / visit_type_enum / calculators** — the
  frozen structural contract is intact.

## Extending the contract

If a vertical genuinely needs a new model field, update the model, create the
migration, update the view/template/seed consumers together, and then update the
frozen constants at the top of `validate.py` (`MODEL_FIELDS`,
`DASHBOARD_CONTEXT_KEYS`, `VISIT_TYPE_CODES`, `PORTAL_URL_NAMES`,
`WIRED_BASELINE_STRINGS`) so the validator tracks the new baseline. Document the
reason in the PR.
