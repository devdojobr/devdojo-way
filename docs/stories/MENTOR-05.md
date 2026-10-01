# MENTOR-05 — End or replace mentoring safely

- **Epic:** Mentoring relationships
- **Scope:** Essential MVP candidate
- **Status:** High-level story; ready for product refinement

## Story
As a learner or mentor, I want to end a mentoring relationship while preserving the learner’s work, so that participation remains voluntary and development can continue with another mentor.

## Relevant confirmed context
- Either party can end the relationship; administrators may also end it for support.
- Former mentors immediately lose access.
- Learners retain history and approvals.
- Pending submissions are recorded as ended without a decision and return to IN PROGRESS.
- A replacement mentor gains access to retained history and reviews resubmitted work.
- At most one mentor is active per enrollment.

## Boundaries
Ending mentoring does not erase past reviewers or decisions, revoke approved achievements, or automatically appoint a replacement. Matching is deferred.

## Open questions
How are participants informed of termination? How do stale notifications behave? Approval revocation and account closure interactions need separate decisions.

## Dependencies
- [MENTOR-03](MENTOR-03.md): new access confirmation.
- [REVIEW-06](REVIEW-06.md): ended iterations.
- [SUPPORT-01](SUPPORT-01.md): administrator intervention.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve voluntary participation, immediate access removal, and historical continuity.
