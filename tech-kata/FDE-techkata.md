# Tech Kata: Stingrays Finance App - FDE Tasks

**Duration:** 60 minutes  
**Difficulty:** Intermediate to Advanced  
**Technologies:** Django, Python, GitHub Copilot

## Overview

You're a Forward Deployed Engineer (FDE) working with Stingrays Finance, a small startup with 3 developers. The customer needs help with two issues: fixing a broken feature and adding payment capabilities to their app.

**Your Role:** Research solutions, plan implementation, and deliver MVP-ready code.

## Setup

```bash
npm install
chmod +x ./start.sh
./start.sh
```

---

## Tasks

### 🔧 TICKET-001: Fix Broken Investment Calculator

**Customer Request:** "Our investment calculator isn't working. Can you fix it?"

**Your Task:**
1. Debug and identify the issue
2. Fix the broken functionality
3. Test that it works

**Hints:**
- Check `templates/core/investment-calculator.html`
- Check `apps/core/views.py`
- Check `apps/core/urls.py`

---

### 💳 TICKET-002: Add Recurring Subscription Payments

**Customer Request:** "We need to be able to accept recurring subscription payments in our app. We want to offer monthly ($29/month) and annual ($290/year) plans for our Pro features. How can we add that functionality?"

**Your Task:**
1. **Research:** What payment solutions work best for Django recurring subscriptions?
2. **Plan:** Design the implementation approach (models, views, flow)
3. **Implement:** Build an MVP-ready payment feature

**Success Criteria:**
- Users can subscribe to monthly or annual plans
- Payments are processed securely
- User's pro status is updated after payment
- Basic error handling for failed payments

**What "MVP-ready" means:**
- Working end-to-end payment flow
- Test mode ready (use test API keys)
- Clean, maintainable code the team can build upon
- Basic security practices followed

---

## Completion

When finished:
1. Ensure both features work end-to-end
2. Test your implementations
3. Document any important setup steps or assumptions
