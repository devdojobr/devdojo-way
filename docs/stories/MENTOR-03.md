# MENTOR-03 — Confirm mentoring access

- **Epic:** Mentoring relationships
- **Scope:** Essential MVP candidate
- **Status:** High-level story; access-conflict behavior unresolved

## Story
As a learner, I want to see the mentor and Track before accepting an invitation, so that I understand whose access I am authorizing.

## Relevant confirmed context
- Learners enter externally shared UUID invitation codes.
- A valid code is Track-specific, single-use, revocable, and valid for seven days.
- Learners see the mentor and Track before confirming.
- Access begins only after confirmation and covers that enrollment’s progress, evidence, and reviews.
- Each enrollment permits at most one active mentor; other Tracks remain outside the relationship’s access.

## Boundaries
No automatic access on code entry and no person-wide access. Mentor replacement must respect relationship termination rules.

## Open questions
**Before launch:** self-redemption, already-mentored enrollments, and acceptance before enrollment. When is a code considered used if a learner previews but does not confirm?

## Dependencies
- [MENTOR-02](MENTOR-02.md): invitation limits.
- [MENTOR-05](MENTOR-05.md): ending/replacing access.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve explicit consent and enrollment-scoped visibility.
