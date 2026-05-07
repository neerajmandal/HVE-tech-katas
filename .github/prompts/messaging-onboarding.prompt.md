---
description: "Explains the messaging portal BRD in plain English for newcomers to the codebase"
argument-hint: "[questions=...]"
---

# Messaging Onboarding

## Inputs

* ${input:questions}: (Optional) Specific questions you have about the messaging feature or the BRD.

## Requirements

Read the messaging portal BRD at #file:docs/BRDs/messaging-portal.md and produce a friendly, plain-English explanation of what it would take to build this messaging feature. Write for a college sophomore who is new to this codebase and may be new to Django. Avoid jargon where possible and define terms when you introduce them.

### Tone and Style

Write like you are explaining this over coffee to a friend who codes but has never seen this project before. Keep things conversational and approachable. Target around 1,000 to 1,500 words. Do not produce ERDs, sequence diagrams, class diagrams, code snippets, or deep technical implementation details. Use `##` for each chunk heading and `###` for sub-sections within chunks.

### Use Phone and Texting Analogies

Ground every concept in something the reader already knows:

* A thread is a group chat in iMessage, where related messages live together
* A message is a single text bubble inside that group chat
* The inbox is the chat list on your phone, showing all your conversations
* An assignment is the contacts list, except an admin manages who you can message
* Read versus unread works like bold versus non-bold texts on your phone

Weave these analogies naturally into your explanation rather than presenting them as a separate glossary.

### Break the BRD Into Three Digestible Chunks

Organize your explanation into three sections that build on each other:

1. "The Foundation" covers what gets stored in the database: messages, threads, timestamps, ordering, and a placeholder for future attachments. This maps to BR-001, BR-003, BR-005, and BR-008 from the BRD.
2. "Who Can Talk to Whom" covers access control and admin-managed assignments that determine which patients can message which providers. This maps to BR-002 and BR-007.
3. "The Conversation Screens" covers what users actually see and interact with: the inbox, thread view, compose, reply, and read/unread indicators. This maps to BR-004 and BR-006.

### Explain the Five Building Blocks

Describe, in plain language, the five pieces that make up a Django feature like this:

1. Models: the database tables that store your data (think spreadsheet columns)
2. Views: the page logic that decides what to show and what to do when someone clicks a button
3. Templates: the HTML pages that users actually see in the browser
4. URLs: the routes that connect a web address to the right page
5. Access rules: the checks that make sure you can only see your own messages

### Connect to What Already Exists

Weave codebase connections into the building blocks and chunks as you introduce them, then include a short closing section that ties everything together. Point out that this codebase already has lab tests and doctor visits, and messaging follows the exact same pattern. Mention that templates live in `templates/core/`, URLs nest under `/portal/`, and the existing features use the same Django conventions (like `@login_required` and `ForeignKey` to the User model). This helps the reader see that messaging is not a brand-new architecture; it is another feature built on the same foundation.

### Address Any Additional Questions

If the reader provided specific questions through the `questions` input, weave answers into the explanation or address them in a short follow-up section at the end.

---

Read the BRD and produce the plain-English explainer following the requirements above.
