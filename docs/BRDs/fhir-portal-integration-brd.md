---
title: FHIR Portal Integration BRD
description: Business requirements document for the FHIR-backed patient portal integration and delivered feature set
author: HVE Tech Katas Team
ms.date: 2026-02-17
ms.topic: overview
keywords:
  - fhir
  - patient portal
  - django
  - vitals
  - requirements
estimated_reading_time: 8
---

## Document purpose

This document back-fills the business requirements for the FHIR integration work that is now implemented in the patient portal. It captures what business outcomes the solution must provide, what features are in scope, and how success is measured.

## Business context

The portal previously depended on ORM-seeded records that were not aligned with external health data exchange standards. The business goal is to source patient-facing records from FHIR resources while preserving a stable user experience in Dashboard, Lab Tests, and Doctor Visits.

## Objectives

* Source portal records from FHIR dataset files with deterministic patient mapping
* Preserve existing portal page contracts and user workflows
* Ensure History and Physical notes are represented as doctor visits, not lab results
* Display latest patient vitals on dashboard with norm-based color and trend direction
* Populate visit vitals from encounter-time observations when available

## Stakeholders

* Product owner for patient portal
* Clinical operations and care teams
* Engineering team maintaining Django portal
* QA team validating patient experience and correctness

## Scope

### In scope

* File-backed FHIR ingestion using `Patient`, `Encounter`, `DiagnosticReport`, `Observation`, and `DocumentReference`
* Repository abstraction for portal record retrieval with source switching
* Deterministic username mapping for `patient1` through `patient20` against finite datasets
* Dashboard summary metrics from FHIR-backed records
* Latest vitals card with status and directional trend from prior reading
* Doctor visit vitals sourced from encounter-linked or same-day observations
* Regression tests for parser, repository behavior, and view context contracts

### Out of scope

* Full FHIR REST production integration beyond scaffold
* New billing behaviors beyond existing invoice retrieval patterns
* Clinical decision support or medical-grade interpretation logic
* Historical migration of existing ORM records into FHIR resources

## Functional requirements

### FR-01 FHIR source selection

The system must support source selection via configuration and default to file-backed FHIR sourcing.

* `PORTAL_RECORDS_SOURCE` supports `fhir_file`, `fhir_rest`, and `legacy_orm`
* `FHIR_DATA_PATH` determines local NDJSON source path
* Unsupported source values must fail fast with explicit error

### FR-02 Deterministic patient mapping

The system must map portal users to dataset patients deterministically.

* `patient1` to `patient10` map directly to ordinals
* `patient11` to `patient20` and unknown usernames map consistently through deterministic fallback

### FR-03 Dashboard record retrieval

The dashboard must show FHIR-backed counts and recency summaries.

* Total labs, pending labs, and abnormal labs
* Recent lab list
* Recent doctor visits and upcoming follow-ups

### FR-04 Lab result classification

Lab Tests must show clinical lab reports and exclude History and Physical notes.

* Diagnostic reports labeled History and Physical are not shown in Lab Tests
* Lab categories remain filterable through existing page controls

### FR-05 Doctor visit classification

Doctor Visits must include encounters and History and Physical records.

* Encounter records remain visible with preserved visit fields
* History and Physical records from reports and documents are represented with visit type `history_physical`
* Duplicate visit rows across encounter, report, and document sources must be prevented

### FR-06 Encounter-time vitals

For visit records, vitals should reflect the time of visit when observations exist.

* Primary match by encounter reference
* Fallback match by same calendar date when encounter-level links are unavailable
* If no relevant vitals exist, vitals remain empty and render as `N/A`

### FR-07 Latest vitals card with trend and norms

Dashboard must show latest patient vitals and indicate directionality from the prior reading.

* Blood pressure, heart rate, temperature, and weight values
* Trend arrows: up, down, or flat based on previous reading
* Norm color state: `normal`, `high`, `low`, or `unknown`

### FR-08 Norm status thresholds

The current implementation classifies status as follows.

* Blood pressure: low if below 90/60, high if above 120/80
* Heart rate: low below 60 bpm, high above 100 bpm
* Temperature: low below 97.0 °F, high above 99.5 °F
* Weight: low below 100 lbs, high above 250 lbs

## Non-functional requirements

* Maintain compatibility with existing template context contracts
* Keep data parsing resilient to missing or malformed FHIR lines
* Keep feature behavior deterministic for repeat testability
* Preserve current page performance characteristics for local dataset size

## UX requirements

* Dashboard latest vitals card must use existing theme tokens and component style
* Latest vitals values must be color-coded by norm state
* Trend direction must be visible using arrow indicators against the previous reading
* Doctor Visits vitals must show `N/A` where data is not available

## Validation and acceptance criteria

A release meets acceptance when all criteria pass.

* Dashboard, Lab Tests, and Doctor Visits pages render without context regressions
* History and Physical notes appear in Doctor Visits and not in Lab Tests
* Dashboard latest vitals values render with status color and trend arrow
* Visit rows show encounter-time vitals where available
* Test suites covering parser, file repository, and portal views pass
* Django system checks pass without new issues

## Dependencies

* Python dependency: `fhir.resources`
* Configuration in `StingrayHealthPortal/settings.py`
* Local NDJSON files in `data/sample-bulk-fhir-datasets-10-patients`

## Risks and mitigations

* Risk: Dataset variability can break assumptions in coding systems
  * Mitigation: Keep parser validation and defensive fallbacks in repository mapping
* Risk: Norm thresholds may not match final clinical policy
  * Mitigation: Keep thresholds centralized in repository helper logic for easy tuning
* Risk: REST source parity is incomplete
  * Mitigation: Keep repository interface stable and expand REST implementation incrementally
