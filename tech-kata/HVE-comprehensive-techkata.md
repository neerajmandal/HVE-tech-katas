# Tech Kata: StingraysFinance Pro - Subscription Billing Modernization

**Duration:** 60-90 minutes
**Difficulty:** Advanced
**Technologies:** Django, Python, Stripe API, PostgreSQL, Mermaid/PlantUML

## Overview

StingraysFinance has grown from a simple free tools platform into a business ready to monetize with a "Pro" subscription tier. However, the codebase has grown organically without proper architecture, and there's a critical bug affecting existing Pro users.

Your mission: modernize the architecture, fix the critical bug, and implement Stripe subscription billing—all while properly documenting your decisions and designs.

**Business Context:** StingraysFinance is a small startup with 3 developers. The CEO has secured funding contingent on launching paid subscriptions within the quarter. The engineering team needs to move fast but also establish good practices for the growing codebase.

## HVE Techniques Covered

| Technique | Ticket |
|-----------|--------|
| Building architecture assets (diagrams) | TICKET-000 |
| Building design from requirements (database) | TICKET-001 |
| Writing ADRs | TICKET-002 |
| Explain code using Copilot | TICKET-003 |
| Diagnose bug root cause | TICKET-004 |
| Fix a bug | TICKET-005 |
| RPI for large refactor | TICKET-006 |
| RPI for net-new feature (payment integration) | TICKET-007 |

---

## Prerequisites

- Basic knowledge of Django framework
- Understanding of REST APIs and webhooks
- Familiarity with database design concepts
- Git workflow knowledge
- Stripe account (test mode) - [Sign up free](https://dashboard.stripe.com/register)

## Setup Instructions

**1. Initial Setup**

```bash
npm install
pip install -r requirements.txt
```

**2. Environment Configuration**

```bash
cp .env.example .env
# Add your Stripe test keys to .env
```

**3. Start Application**

```bash
./start.sh
```

**4. Verify Setup**
- Navigate to `http://localhost:8000`
- Log in with test credentials: `pro_user@test.com` / `testpass123`
- Verify you can access the Pro dashboard (may intermittently fail - that's the bug!)

---

## Tasks

### TICKET-000: Architecture Documentation

**Type:** Documentation
**Priority:** High
**HVE Technique:** Building architecture assets using Copilot

**Description:**

Before making changes, we need to document our current architecture. Create C4 diagrams (Context and Container level) showing the current system architecture and the proposed architecture with Stripe integration.

**User Story:**

As a new developer joining the team, I want clear architecture diagrams so that I can understand how the system components interact and where changes need to be made.

**Acceptance Criteria:**

- [ ] C4 Context Diagram created showing:
  - StingraysFinance system boundary
  - User types (Free users, Pro users, Admins)
  - External systems (future: Stripe, Email service)
- [ ] C4 Container Diagram created showing:
  - Django web application
  - PostgreSQL database
  - Static file serving
  - Future: Stripe webhook handler
- [ ] Diagrams created using Mermaid or PlantUML (text-based, version-controllable)
- [ ] Diagrams saved to `/docs/architecture/` directory
- [ ] Brief README explaining each diagram

**Deliverables:**

```
/docs/architecture/
├── README.md
├── c4-context.md (or .puml)
└── c4-container.md (or .puml)
```

**Tips for using Copilot:**
- Describe your system components and ask Copilot to generate Mermaid C4 diagram syntax
- Provide context about Django apps and ask for container-level breakdown
- Request PlantUML or Mermaid format specifically

---

### TICKET-001: Subscription Database Schema Design

**Type:** Design
**Priority:** High
**HVE Technique:** Building design from requirements

**Description:**

Design the database schema to support subscription billing. The schema must handle subscription plans, customer subscriptions, payment history, and integration with Stripe's data model.

**Business Requirements:**

1. Support multiple subscription tiers (Basic Pro, Premium Pro, Enterprise)
2. Track subscription status (active, canceled, past_due, trialing)
3. Store payment history for invoicing and support
4. Handle subscription upgrades/downgrades
5. Support annual and monthly billing cycles
6. Allow for promotional/discount codes
7. Track Stripe customer and subscription IDs for sync

**Acceptance Criteria:**

- [ ] ERD (Entity Relationship Diagram) created showing all tables and relationships
- [ ] Schema includes tables for:
  - `SubscriptionPlan` (available plans and pricing)
  - `CustomerSubscription` (user's active subscription)
  - `PaymentHistory` (transaction records)
  - `PromoCode` (discount codes)
- [ ] All foreign key relationships defined
- [ ] Appropriate indexes identified for common queries
- [ ] Schema handles edge cases (user changes plan mid-cycle, refunds)
- [ ] Design document saved to `/docs/design/subscription-schema.md`

**Deliverables:**

```
/docs/design/
└── subscription-schema.md
    - ERD diagram (Mermaid)
    - Table definitions with column types
    - Index recommendations
    - Migration strategy notes
```

**Sample Requirements to Design From:**

```
- Users can subscribe to: Basic ($9.99/mo), Premium ($19.99/mo), Enterprise ($49.99/mo)
- Annual billing gets 2 months free
- Subscriptions auto-renew unless canceled
- Users can upgrade immediately (prorated) or downgrade at period end
- We need to show users their payment history
- Support team needs to look up payments by email or transaction ID
- Promo codes can be: percentage off, fixed amount off, or free trial extension
```

---

### TICKET-002: Payment Provider ADR

**Type:** Documentation
**Priority:** High
**HVE Technique:** Writing ADRs with Copilot

**Description:**

Write an Architecture Decision Record (ADR) documenting the decision to use Stripe as the payment provider over alternatives like PayPal and Square.

**Context:**

The team evaluated three payment providers for subscription billing. This ADR should capture the evaluation criteria, analysis, and final decision rationale.

**Acceptance Criteria:**

- [ ] ADR follows standard template (Title, Status, Context, Decision, Consequences)
- [ ] Document evaluates at least 3 options (Stripe, PayPal, Square)
- [ ] Evaluation criteria include:
  - Developer experience / API quality
  - Subscription/recurring billing support
  - Pricing and fees
  - Webhook reliability
  - PCI compliance handling
  - International support
  - Documentation quality
- [ ] Decision clearly stated with rationale
- [ ] Consequences section covers both positive and negative implications
- [ ] ADR saved to `/docs/adr/001-payment-provider-selection.md`

**Deliverables:**

```
/docs/adr/
└── 001-payment-provider-selection.md
```

**ADR Template:**

```markdown
# ADR-001: Payment Provider Selection

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision Drivers
[What criteria are most important for this decision?]

## Considered Options
1. Stripe
2. PayPal
3. Square

## Decision
[What is the decision and why?]

## Consequences
### Positive
[What are the benefits?]

### Negative
[What are the drawbacks?]

### Neutral
[What are the side effects?]
```

---

### TICKET-003: Code Explanation - Authentication & Pro Access Flow

**Type:** Analysis
**Priority:** Medium
**HVE Technique:** Explain code using Copilot

**Description:**

Before fixing the Pro access bug, we need to understand the current authentication and Pro access verification flow. Use Copilot to explain the existing code and document how the system currently determines if a user has Pro access.

**Context:**

The codebase has grown without documentation. New team members struggle to understand how Pro access is verified throughout the application. Some views check `user.is_pro`, others check session data, and some check a `ProSubscription` model directly.

**Acceptance Criteria:**

- [ ] Document the current authentication flow from login to session creation
- [ ] Identify ALL locations where Pro access is checked (list file:line references)
- [ ] Create a sequence diagram showing the Pro access verification flow
- [ ] Document inconsistencies found in how Pro access is checked
- [ ] Identify the session handling code and explain how Pro status is cached
- [ ] Analysis document saved to `/docs/analysis/pro-access-flow.md`

**Files to Analyze:**

- `apps/core/views.py` - Main view handlers
- `apps/pro/views.py` - Pro-specific views
- `apps/core/middleware.py` - Session and auth middleware
- `apps/pro/models.py` - Pro subscription model
- `apps/core/decorators.py` - Access control decorators

**Deliverables:**

```
/docs/analysis/
└── pro-access-flow.md
    - Authentication flow description
    - Pro access check locations (with file:line)
    - Sequence diagram (Mermaid)
    - Identified inconsistencies
    - Session handling explanation
```

**Tips for using Copilot:**
- Select code blocks and ask "Explain this code"
- Ask "What does this middleware do?"
- Ask "How does this decorator verify Pro access?"
- Ask "What are the possible race conditions in this session handling?"

---

### TICKET-004: Diagnose Pro Access Bug

**Type:** Bug Investigation
**Priority:** Critical
**HVE Technique:** Using Copilot to diagnose root cause

**Description:**

Pro users are intermittently losing access to Pro features. They report being randomly redirected to the upgrade page even though their subscription is active. The issue seems to happen more frequently during peak hours.

**Bug Report:**

```
Title: Pro users intermittently lose access
Reported by: Customer Success Team
Frequency: ~15% of Pro user sessions affected
Pattern: More common during peak hours (9am-11am, 2pm-4pm EST)

User reports:
- "I was using the Pro dashboard and suddenly got kicked to the upgrade page"
- "Refreshing the page sometimes fixes it, sometimes doesn't"
- "My subscription shows active in account settings"

Technical observations:
- No errors in application logs during incidents
- Database shows subscription as active
- Issue does not correlate with deployment times
```

**Acceptance Criteria:**

- [ ] Root cause identified and documented
- [ ] Reproduction steps documented (how to trigger the bug reliably)
- [ ] Explain WHY the bug occurs (not just what happens)
- [ ] Document which code paths are affected
- [ ] Propose fix approach (to be implemented in TICKET-005)
- [ ] Bug analysis saved to `/docs/bugs/pro-access-race-condition.md`

**Investigation Hints:**

Look for:
- Race conditions in session updates
- Cache invalidation issues
- Concurrent request handling
- Session vs database state inconsistency
- Middleware execution order

**Deliverables:**

```
/docs/bugs/
└── pro-access-race-condition.md
    - Root cause explanation
    - Affected code paths
    - Reproduction steps
    - Proposed fix approach
```

---

### TICKET-005: Fix Pro Access Race Condition

**Type:** Bug Fix
**Priority:** Critical
**HVE Technique:** Using Copilot to fix a bug

**Description:**

Implement the fix for the Pro access race condition identified in TICKET-004.

**Acceptance Criteria:**

- [ ] Race condition eliminated
- [ ] Pro users no longer experience intermittent access loss
- [ ] Fix handles concurrent requests properly
- [ ] Session state stays consistent with database state
- [ ] No performance regression introduced
- [ ] Unit tests added covering the race condition scenario
- [ ] Integration test added that simulates concurrent requests
- [ ] Fix documented in code comments explaining the race condition

**Technical Requirements:**

- Use appropriate locking mechanisms if needed
- Consider database transaction isolation levels
- Ensure fix works in multi-process deployment (gunicorn workers)
- Add logging for debugging future session issues

**Testing Approach:**

```python
# Suggested test scenario
def test_concurrent_pro_access_check():
    """
    Simulate multiple concurrent requests checking Pro access
    while subscription status is being updated.
    All requests should see consistent state.
    """
    pass
```

---

### TICKET-006: Refactor Views into Service Layer

**Type:** Refactor
**Priority:** High
**HVE Technique:** RPI for large refactor

**Description:**

The `apps/core/views.py` file has grown to 500+ lines with business logic mixed into view handlers. Before adding payment integration, refactor to introduce a proper service layer.

**Current State:**

```
apps/core/views.py (500+ lines)
├── Authentication logic mixed with views
├── Pro access checks duplicated
├── Business calculations in view functions
├── Direct database queries scattered throughout
└── No separation of concerns
```

**Target State:**

```
apps/core/
├── views.py (thin, HTTP handling only)
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── subscription_service.py
│   ├── calculator_service.py
│   └── user_service.py
└── repositories/
    ├── __init__.py
    └── subscription_repository.py
```

**Acceptance Criteria:**

- [ ] Create `services/` directory with appropriate service modules
- [ ] Extract business logic from views into services
- [ ] Views become thin controllers (HTTP handling, request validation, response formatting)
- [ ] Services handle business logic and orchestration
- [ ] All existing functionality preserved (no behavior changes)
- [ ] All existing tests pass
- [ ] New unit tests for service layer
- [ ] Code follows single responsibility principle
- [ ] Dependency injection pattern used for testability

**Refactoring Guidelines:**

1. **DO NOT** change any external behavior
2. Refactor incrementally (one view at a time)
3. Run tests after each extraction
4. Keep commits small and focused
5. Update imports as needed

**Services to Create:**

| Service | Responsibility |
|---------|---------------|
| `AuthService` | Login, logout, session management |
| `SubscriptionService` | Pro status checks, subscription operations |
| `CalculatorService` | Investment calculations, financial tools |
| `UserService` | User profile operations |

---

### TICKET-007: Implement Stripe Subscription Integration

**Type:** Feature
**Priority:** High
**HVE Technique:** RPI for net-new features (Payment processing external integration)

**Description:**

Implement Stripe subscription billing to allow users to subscribe to Pro plans. This includes checkout flow, webhook handling, and subscription management.

**User Stories:**

1. As a free user, I want to subscribe to a Pro plan so that I can access premium features
2. As a Pro user, I want to manage my subscription (upgrade/downgrade/cancel) so that I can control my spending
3. As a Pro user, I want to view my payment history so that I can track my expenses
4. As the system, I need to handle Stripe webhooks so that subscription status stays synchronized

**Acceptance Criteria:**

**Checkout Flow:**
- [ ] User can view available subscription plans with pricing
- [ ] User can select a plan and proceed to Stripe Checkout
- [ ] Successful payment redirects to Pro dashboard with success message
- [ ] Failed payment shows appropriate error message
- [ ] Support for promo codes at checkout

**Webhook Handling:**
- [ ] Endpoint `/webhooks/stripe/` receives Stripe events
- [ ] Handle `checkout.session.completed` - activate subscription
- [ ] Handle `invoice.paid` - record payment, extend subscription
- [ ] Handle `invoice.payment_failed` - notify user, grace period
- [ ] Handle `customer.subscription.deleted` - deactivate Pro access
- [ ] Webhook signature verification implemented
- [ ] Idempotency handling (duplicate webhook protection)

**Subscription Management:**
- [ ] User can view current subscription status
- [ ] User can upgrade to higher tier (immediate, prorated)
- [ ] User can downgrade to lower tier (end of period)
- [ ] User can cancel subscription (access until period end)
- [ ] User can view payment history

**Technical Requirements:**
- [ ] Use Stripe Python SDK
- [ ] Store Stripe customer ID and subscription ID in database
- [ ] Use Stripe test mode for development
- [ ] Environment variables for Stripe keys (never commit keys)
- [ ] Proper error handling for Stripe API failures
- [ ] Logging for all payment events

**API Endpoints to Create:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscribe/` | Show available plans |
| POST | `/subscribe/checkout/` | Create Stripe Checkout session |
| GET | `/subscribe/success/` | Handle successful checkout redirect |
| GET | `/subscribe/cancel/` | Handle canceled checkout redirect |
| POST | `/webhooks/stripe/` | Receive Stripe webhook events |
| GET | `/account/subscription/` | View current subscription |
| POST | `/account/subscription/cancel/` | Cancel subscription |
| GET | `/account/payments/` | View payment history |

**Stripe Integration Checklist:**

```python
# Required Stripe operations
stripe.Customer.create()           # Create customer on first purchase
stripe.checkout.Session.create()   # Create checkout session
stripe.Subscription.modify()       # Upgrade/downgrade
stripe.Subscription.delete()       # Cancel (or set cancel_at_period_end)
stripe.Webhook.construct_event()   # Verify webhook signature
```

**Testing Requirements:**

- [ ] Unit tests for subscription service methods
- [ ] Integration tests using Stripe test mode
- [ ] Webhook handler tests with mock Stripe events
- [ ] End-to-end test of checkout flow (can be manual with Stripe test cards)

**Stripe Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Requires auth: `4000 0025 0000 3155`

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Stripe Python SDK](https://stripe.com/docs/api?lang=python)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Stripe Test Cards](https://stripe.com/docs/testing)
- [C4 Model](https://c4model.com/)
- [ADR GitHub Template](https://github.com/joelparkerhenderson/architecture-decision-record)

---

## Submission Guidelines

1. Complete tickets in order (dependencies exist between tickets)
2. Commit after each ticket with message format: `[TICKET-XXX] Brief description`
3. Ensure all acceptance criteria are met before moving to next ticket
4. Documentation tickets (000-004) set foundation for implementation tickets (005-007)
5. Test thoroughly - the payment integration must be reliable

**Recommended Time Allocation:**

| Tickets | Focus | Suggested Time |
|---------|-------|----------------|
| 000-002 | Architecture & Design | 15-20 min |
| 003-004 | Analysis & Diagnosis | 10-15 min |
| 005 | Bug Fix | 10-15 min |
| 006 | Refactoring | 15-20 min |
| 007 | Payment Integration | 20-25 min |

---

**Good luck! This kata challenges you to demonstrate the full range of AI-assisted development—from architecture and design through debugging to implementing complex integrations.**
