# REVIEW-04 — Decide a review outcome

- **Epic:** Evidence and review
- **Scope:** Essential MVP candidate
- **Status:** High-level story; mistaken-approval policy unresolved

## Story
As a mentor, I want to approve a requirement or reject it with an explanation, so that the learner knows whether it is endorsed or what needs improvement.

## Relevant confirmed context
- Only the enrollment’s active mentor reviews its pending submission.
- Approval moves the requirement to DONE; written approval feedback is optional.
- Rejection requires an explanation and returns the requirement to IN PROGRESS.
- Evidence, feedback, reviewer, decision, and timestamps remain in history.
- Review decisions notify the learner in-app.
- Approved evidence and decisions remain unchanged; administrators cannot override them.

## Boundaries
No multiple-reviewer voting, separate final Track sign-off, automatic assessment, or administrator override. Reopening approved work is deferred.

## Open questions
**Before launch:** handling materially mistaken approvals. Also refine decisions on withdrawn work, relationship termination during review, and correction of accidental rejection without rewriting history.

## Dependencies
- [REVIEW-02](REVIEW-02.md), [MENTOR-05](MENTOR-05.md): review no longer pending.
- [LEARN-05](LEARN-05.md): completion.
- [NOTIFY-02](NOTIFY-02.md): outcome alerts.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve sole active-mentor authority and explicit rejection feedback.
