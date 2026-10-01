# REVIEW-01 — Submit demonstrated achievement

- **Epic:** Evidence and review
- **Scope:** Essential MVP candidate
- **Status:** High-level story; ready for product refinement

## Story
As a learner with an active mentor, I want to submit evidence for a requirement, so that my mentor can assess what I have demonstrated.

## Relevant confirmed context
- Submission requires at least some text or a link and an active mentor for that enrollment.
- Submission enters IN REVIEW and triggers an in-app mentor notification.
- Submitted text/links are preserved unchanged for that iteration.
- Without a mentor, work remains IN PROGRESS.
- Mentor approval is required for DONE.

## Boundaries
No empty reviews, unassigned review queue, self-approved completion, uploads, or automatic assessment. External link contents are not preserved by recording a link.

## Open questions
Duplicate submissions, accidental submission handling, and submission from states other than IN PROGRESS need refinement. Define evidence sufficiency at the product level, not via invented technical validation.

## Dependencies
- [REVIEW-02](REVIEW-02.md): withdrawal.
- [REVIEW-06](REVIEW-06.md): iteration history.
- [NOTIFY-01](NOTIFY-01.md): mentor awareness.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve evidence and mentor prerequisites; do not infer arbitrary status transitions.
