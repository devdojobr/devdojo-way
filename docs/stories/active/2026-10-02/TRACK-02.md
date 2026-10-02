# TRACK-02 — Update Tracks without disrupting learners

- **Epic:** Track administration
- **Scope:** Essential MVP candidate
- **Status:** High-level story; ready for product refinement

## Story
As an administrator, I want to update requirements for future enrollments while preserving existing learners’ requirements, so that guidance can improve without changing commitments mid-journey.

## Relevant confirmed context
- Existing enrollments retain their original requirements and history.
- Changes affect new enrollments only.
- Learners who pause and return resume their original requirements and progress.
- Completion depends on the requirements belonging to that enrollment.

## Boundaries
Migration to newer requirements is deferred. Do not automatically add, remove, or rewrite requirements in existing enrollments. This is a product version policy, not a prescribed technical versioning design.

## Open questions
How administrators and learners distinguish changed Track definitions needs refinement. Treatment of minor corrections versus substantive changes has not been separately decided.

## Dependencies
- [TRACK-01](TRACK-01.md): initial definition.
- [TRACK-03](TRACK-03.md): retirement.
- [LEARN-04](LEARN-04.md): resumed enrollment.
- [LEARN-05](LEARN-05.md): preserved completion basis.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve existing commitments; flag exceptions as proposals requiring confirmation.
