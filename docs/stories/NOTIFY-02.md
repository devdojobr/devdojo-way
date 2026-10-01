# NOTIFY-02 — Learn about outcomes and replies

- **Epic:** Review awareness
- **Scope:** Essential MVP candidate
- **Status:** High-level story; notification lifecycle unresolved

## Story
As a review participant, I want in-app alerts for relevant decisions and replies, so that I know when to respond or continue working.

## Relevant confirmed context
- Review decisions notify the learner in-app.
- Replies notify the other review participant in-app.
- Approval means DONE; rejection includes feedback and means IN PROGRESS.
- Comments alone do not change status.
- Notifications must respect the relationship’s current access boundaries.

## Boundaries
Email notifications are deferred. No push alerts, reminders, standalone chat, notification preferences, or relationship-event alerts have been committed.

## Open questions
How should alerts behave after withdrawal, resubmission, archiving, or relationship termination? Are read/unread states needed? Avoid assuming every lifecycle event needs a notification.

## Dependencies
- [REVIEW-03](REVIEW-03.md), [REVIEW-04](REVIEW-04.md): triggering events.
- [MENTOR-05](MENTOR-05.md): ending access.

## Refinement handoff
Read [PRODUCT-CONTEXT.md](PRODUCT-CONTEXT.md). Preserve confirmed event coverage and separate additional notification proposals.
