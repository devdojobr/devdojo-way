# NOTIFY-01 — Find work awaiting my review

- **Epic:** Review awareness
- **Scope:** Essential MVP candidate
- **Status:** High-level story; stale-alert behavior unresolved

## Story
As a mentor, I want in-app submission alerts and a list of pending reviews, so that learners’ work does not go unnoticed.

## Relevant confirmed context
- A learner’s submission to IN REVIEW notifies the active mentor in-app.
- Mentors have a pending-review list covering their assigned enrollments.
- Evidence and an active mentor are prerequisites for submission.
- Withdrawal, decisions, or relationship ending can make a submission no longer pending.
- Former mentors lose access immediately when the relationship ends.

## Boundaries
Email, push, reminders, escalation deadlines, assignment routing, and priority scoring are not confirmed. Do not let an old notification retain unauthorized access.

## Open questions
How are withdrawn, resubmitted, decided, or ended reviews represented in old notifications? Read/unread behavior and queue ordering need refinement, not assumed feature commitments.

## Dependencies
- [REVIEW-01](REVIEW-01.md), [REVIEW-02](REVIEW-02.md), [REVIEW-04](REVIEW-04.md): actionable work.
- [MENTOR-05](MENTOR-05.md): lost access.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Focus on finding actionable reviews without adding scheduling or external channels.
