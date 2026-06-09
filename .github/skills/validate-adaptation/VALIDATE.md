# VALIDATE — validate-adaptation

Reference for the checks in `validate.py`, their output, and exit codes. The
validator is read-only and architecture-aware for the Stingray portal
(Django 5.2 backend, server-rendered Tailwind templates).

## Invocation

```bash
# All checks (from repo root)
python .github/skills/validate-adaptation/validate.py

# One or more specific checks
python .github/skills/validate-adaptation/validate.py --check ui_contract --check seed_contract

# Validator helper self-tests (no app files read)
python .github/skills/validate-adaptation/validate.py --self-test
```

## Output streams

- **stdout**: `[PASS|FAIL|SKIP] <check>: <details>` plus, for failures, a
  `remediation:` line, and a final `Summary: N failed`.
- **stderr**: one JSON object per check —
  `{"name","status","passed","skipped","details","remediation"}` — for machine
  parsing.

## Exit codes

- `0` — no non-skipped check failed (skips count as pass).
- `1` — at least one check failed.

## Baseline behavior

On the committed healthcare baseline the adaptation-dependent checks
(`domain_manifest`, `ui_contract`, `seed_contract`) report `SKIP`, and the
contract checks (`environment`, `backend_compile`, `schema_integrity`,
`api_contract`, `visit_type_enum`, `calculators`) report `PASS`. Expected
result: `Summary: 0 failed`, exit `0`.

## Check reference

- **environment** — Python ≥ 3.10; baseline files present (`apps/core/models.py`,
  `views.py`, `urls.py`, `StingrayHealthPortal/settings.py`,
  `management/commands/seed_dummy_data.py`, `templates/portal_base.html`,
  `templates/base.html`, `manage.py`, `package.json`).
- **backend_compile** — `ast.parse` of every module under `apps/` and
  `StingrayHealthPortal/`.
- **schema_integrity** — each of the six Django models still declares its
  required fields (superset allowed; drop/rename fails). Note: `User` is the
  built-in `django.contrib.auth` model and is not redeclared here.
- **api_contract** — `apps/core/views.py:patient_dashboard` still builds all
  seven dashboard context keys the templates bind to (`total_labs`,
  `pending_labs`, `abnormal_labs`, `total_visits`, `recent_labs`,
  `recent_visits`, `upcoming_followups`).
- **visit_type_enum** — `DoctorVisit.VISIT_TYPE_CHOICES` codes (first tuple
  element) stay exactly `{checkup, follow_up, urgent, specialist, preventive}`.
  Labels (second element) may be re-skinned.
- **domain_manifest** — if present: `apps/core/domain.py` defines `DOMAIN`; any
  nav `url_name` resolves to a real portal URL name; `context_processors.py`
  returns a `domain` key and is registered in `settings.py`.
- **ui_contract** — if a manifest exists: wired templates read `domain.*` and
  drop the hardcoded baseline strings. (See SKILL.md for the rationale.)
- **seed_contract** — generated `seed_*.py` commands (excluding
  `seed_dummy_data.py`) set only existing model fields (FK `*_id` aliases and
  `defaults=` are allowed).
- **calculators** — every `views.<name>` referenced in `urls.py` is defined, and
  any `calculate_*` helper a view calls exists in
  `apps/core/services/finance.py` or `views.py`.
- **tests** — informational skip; reports the static gate commands.

## When a check fails

Read the `remediation:` line. The guiding rule: **re-skin display copy and swap
data values; keep model fields, dashboard context keys, URL names, and
`visit_type` codes stable.** If a vertical genuinely requires a structural
change, update every consumer together (model → migration → view → template →
seed) and update the frozen contract constants at the top of `validate.py` so
the validator tracks the new baseline.
