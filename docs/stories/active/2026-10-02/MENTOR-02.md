# MENTOR-02 — Invite a learner to Track mentoring

- **Epic:** Mentoring relationships
- **Scope:** Essential MVP candidate
- **Status:** High-level story; redemption eligibility unresolved

## Story
As an approved mentor, I want to share a temporary, Track-specific invitation code, so that I can establish a mentoring relationship with a learner.

## Relevant confirmed context
- Invitations use temporary UUID codes shared externally.
- Codes are scoped to one Track, single-use, revocable, and expire after seven days.
- Codes are not recipient-bound; the first eligible redeemer may use one.
- Each enrollment has at most one active mentor.
- Creating or sharing a code does not itself grant learner-data access; learner confirmation is required.

## Boundaries
No in-system invitation delivery, email notifications, group codes, or mentor matching is committed. Do not select a technical UUID implementation.

## Open questions
**Before launch:** eligible redemption, self-redemption, existing-mentor conflicts, and learners not yet enrolled. Also refine expired, invalid, used, and revoked-code behavior.

## Dependencies
- [MENTOR-01](MENTOR-01.md): approved mentors.
- [MENTOR-03](MENTOR-03.md): confirmation and access.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Address forwarded-code risk without silently changing to recipient-bound invitations.
