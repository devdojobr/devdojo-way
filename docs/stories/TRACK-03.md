# TRACK-03 — Retire a Track

- **Epic:** Track administration
- **Scope:** Essential MVP candidate
- **Status:** High-level story; ready for product refinement

## Story
As an administrator, I want to stop new enrollment in a retired Track while allowing existing learners to continue, so that outdated Tracks can be phased out fairly.

## Relevant confirmed context
- Retirement stops new enrollment.
- Existing learners may continue with their original requirements.
- Existing progress, approvals, and review history are retained.

## Boundaries
Retirement is not deletion. Do not end existing mentoring, cancel reviews, or migrate learners merely because a Track is retired. Reactivation and permanent deletion are not confirmed.

## Open questions
Can an archived enrollment be resumed after retirement? How should learners distinguish retired Tracks from available ones?

## Dependencies
- [TRACK-02](TRACK-02.md): original requirements remain intact.
- [LEARN-01](LEARN-01.md): enrollment availability.
- [LEARN-04](LEARN-04.md): pause/resume edge case.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Keep retirement separate from destructive removal and ask about resume behavior.
