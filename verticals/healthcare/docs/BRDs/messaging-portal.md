---
title: Messaging Portal BRD
description: Business requirements document for secure provider patient messaging in the Stingray Health Portal
author: HVE Tech Katas Team
ms.date: 2026-02-17
ms.topic: overview
keywords:
  - messaging
  - patient portal
  - brd
  - django
  - healthcare
estimated_reading_time: 8
---

## Business context and background

The Stingray Health Portal currently supports appointments, lab results, and core patient account workflows. Patients do not have an in-portal channel for non-urgent communication with their assigned care team. This causes avoidable phone calls, voicemail backlog, and delays in routine follow-up.

The business initiative is to introduce secure portal messaging that supports patient to provider communication, provider responses, and assignment management by administrators.

## Problem statement and business drivers

Patients currently use manual channels for non-urgent questions, including clinic calls and email. These channels increase administrative overhead and reduce communication traceability.

Primary business drivers:

* Improve patient access to care-team communication
* Reduce avoidable operational load on front-office staff
* Provide a reliable and auditable communication record in the portal
* Support role-based care-team routing and assignment governance

## Business objectives and success metrics

### Objectives

* Enable patients to send secure messages to assigned provider staff
* Enable doctors and care staff to review and respond from portal workflows
* Enable administrators to manage provider, nurse, and patient assignment relationships
* Present message threads in a consistent and predictable order
* Track unread versus read status for participant inbox workflows

## Stakeholders and roles

* Product owner: defines business outcomes and release scope
* Clinical operations lead: validates care-team workflow alignment
* Doctors and nurses: receive and respond to patient messages
* Patients: initiate and review message conversations
* Portal administrators: manage doctor nurse patient assignments
* Engineering and QA teams: implement, test, and validate requirements

## Scope

### In scope

* Secure messaging for patients and assigned care-team members
* Provider inbox and thread response workflows
* Doctor nurse patient assignment management for routing
* Message thread grouping and retrieval
* Read and unread status tracking
* Stable chronological ordering in message lists and threads
* Data model support for future attachment expansion without current file upload delivery

### Out of scope

* Real-time transport protocol decision and implementation beyond current portal request response model
* AI-based urgency classification
* External email or SMS delivery channels
* Production-scale retention policy and legal hold automation

## Current and future business processes

### Current state

1. Patient has a non-urgent question
1. Patient calls clinic or leaves voicemail
1. Staff manually routes request to provider
1. Provider response is delayed or handled outside the portal

### Future state

1. Patient opens portal messaging and creates a message
1. System routes message to assigned provider team based on assignment rules
1. Provider reviews unread inbox items and responds in thread
1. Patient receives thread updates on next portal visit and can continue the conversation
1. Admin updates care-team assignments as staffing or panel ownership changes

## Business requirements

### BR-001 Message creation and storage

* Requirement: The system must store each message with sender, recipient, content, and created timestamp
* Linked objective: Enable patients and providers to exchange secure messages
* Impacted stakeholders: Patients, doctors, nurses, administrators
* Priority: Must have
* Acceptance criteria:
  * A persisted message includes sender, recipient, content, and timestamp fields
  * Message data can be retrieved for inbox and thread views

### BR-002 Assignment-based routing

* Requirement: The system must route patient messages only to assigned provider staff according to admin-managed relationships
* Linked objective: Support role-based care-team routing and assignment governance
* Impacted stakeholders: Patients, doctors, nurses, administrators
* Priority: Must have
* Acceptance criteria:
  * Patient messaging target list is limited to assigned care-team members
  * Admin assignment updates affect subsequent message routing behavior

### BR-003 Threaded conversation grouping

* Requirement: The system must support message threads so related conversation messages are grouped and retrievable as a unit
* Linked objective: Enable readable and continuous patient-provider communication
* Impacted stakeholders: Patients, doctors, nurses
* Priority: Must have
* Acceptance criteria:
  * Messages can be associated to a thread identifier
  * Thread view returns all messages for that conversation context

### BR-004 Read and unread status

* Requirement: The system must track read and unread status per participant message view
* Linked objective: Improve inbox workflow and response handling
* Impacted stakeholders: Patients, doctors, nurses
* Priority: Must have
* Acceptance criteria:
  * Newly delivered messages are marked unread for recipients
  * Opening a message or thread updates status to read for that participant

### BR-005 Consistent message ordering

* Requirement: The system must render messages in a consistent chronological order within inboxes and threads
* Linked objective: Present predictable message history and reduce user confusion
* Impacted stakeholders: Patients, doctors, nurses, QA
* Priority: Must have
* Acceptance criteria:
  * Message lists use the configured sort direction for every query
  * Given identical test data, repeated loads produce stable ordering

### BR-006 Provider response workflow

* Requirement: The system must allow provider staff to respond to patient messages from portal workflows
* Linked objective: Enable two-way communication and close message loops
* Impacted stakeholders: Doctors, nurses, patients
* Priority: Must have
* Acceptance criteria:
  * Provider users can submit replies in an existing thread
  * Patient users can view provider replies in the same conversation thread

### BR-007 Admin assignment management

* Requirement: The system must provide admin capabilities to manage doctor nurse patient assignment relationships
* Linked objective: Keep routing accurate as staffing and care panels change
* Impacted stakeholders: Administrators, doctors, nurses, patients
* Priority: Must have
* Acceptance criteria:
  * Admin users can create, update, and remove assignment relationships
  * Assignment changes are reflected in messaging target eligibility

### BR-008 Attachment extensibility

* Requirement: The solution must preserve a path for future message attachments without requiring schema redesign
* Linked objective: Reduce future delivery effort for attachment use cases
* Impacted stakeholders: Product owner, engineering, clinical operations
* Priority: Could have
* Acceptance criteria:
  * Data model and domain boundaries allow attachment support in a future increment
  * Current release excludes direct attachment upload and retrieval workflows

## Non-functional requirements

* Enforce user-based access so users can only view their own message data
* Keep message retrieval deterministic and repeatable for testing

## Benefits and high-level economics

* Expected benefit: lower manual communication overhead for non-urgent inquiries
* Expected benefit: improved patient satisfaction through accessible asynchronous communication
* Expected benefit: stronger traceability versus phone and shared mailbox processes
* Cost assumptions and quantified ROI: TODO with product and operations stakeholders

## Validation and acceptance criteria

A release is accepted when all criteria are met.

* All must-have requirements BR-001 through BR-007 are implemented and validated
* Inbox and thread ordering behavior is consistent and reproducible
* Read and unread status transitions behave correctly by participant
* Assignment changes update routing eligibility without manual intervention
* Security and access checks prevent unauthorized message visibility

## Risks and mitigations

* Risk: Incorrect assignment data can misroute messages
  * Mitigation: Add assignment validation checks and operational reporting
* Risk: Inconsistent ordering logic across queries can reintroduce display defects
  * Mitigation: Standardize ordering conventions and cover with regression tests
* Risk: Message volume growth can degrade inbox response times
  * Mitigation: Apply targeted indexing and monitor query performance
