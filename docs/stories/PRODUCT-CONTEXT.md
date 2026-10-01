# Shared product context

## Provenance and authority

- **Source idea:** `../idea.md` defines Tracks and requirements, multiple enrollments, a four-state Kanban, text/link evidence, temporary UUID mentoring invitations, mentor review notifications, acceptance/rejection, and retained review iterations.
- **Confirmed discovery decisions:** the rules below were selected by the user during the interview. They clarify and extend the source idea.
- **Assumptions and open questions:** explicitly labeled below; they are not requirements.
- **Status:** first high-level story draft. Stories are essential MVP candidates selected during discovery, not implementation specifications.

If the source, a story, and shared context appear inconsistent, surface the conflict. Do not silently choose a new policy.

## Purpose and audience — confirmed

A focused developer-community pilot helps learners demonstrate career growth through evidence, actionable feedback, and repeated improvement. Designated administrators run the program.

A Track is an independent target role or career level, such as Senior Java Developer. Learners can join several Tracks directly without earlier-level prerequisites. Completion means mentor endorsement of every requirement, not guaranteed employment, promotion, or overall role readiness.

Learners without mentors can organize work and prepare evidence, but cannot submit for review or obtain endorsed completion.

## Actors and permissions — confirmed

- Learners manage their own enrollments, work, evidence, submissions, and review participation.
- Mentors require administrator approval. A person may both learn and mentor.
- Each enrollment has at most one active mentor. Different enrollments may have different mentors.
- Active mentors see their assigned enrollment’s progress, evidence, and review history, including earlier mentors’ reviews.
- Administrators define Tracks, approve mentors, inspect enrollment history for support, and may end relationships. Support access/intervention is recorded.
- Administrators cannot change learner evidence, rewrite decisions, or override mentor reviews.
- Progress is private by default; there are no public profiles in the MVP.

## Core journey and review rules — confirmed

Administrator defines Track → learner enrolls → learner works on a requirement → submits evidence to an active mentor → mentor discusses and reviews → history survives revisions → progress advances.

- Requirements start in WAITING; learners begin work in IN PROGRESS.
- Submission requires at least text or a link plus an active mentor; it enters IN REVIEW.
- Without a mentor, work remains IN PROGRESS.
- Submitted evidence is preserved unchanged within each iteration. Withdraw before revising a pending submission.
- Rejection requires an explanation and returns work to IN PROGRESS.
- Approval moves work to DONE; approval feedback is optional.
- Both parties may reply within the review; comments alone do not change status.
- History retains submitted evidence, discussion, reviewer, decision/outcome, and timestamps across iterations.
- Approved evidence and decisions remain unchanged; reopening is deferred.
- The Track completes when every requirement is approved, without a separate final sign-off.
- Preserving a link does not preserve or guarantee the external content behind it.

## Mentoring lifecycle — confirmed

- Approved mentors generate temporary UUID invitations, scoped to a Track.
- Codes are single-use, revocable, and valid for seven days. They are not recipient-bound; the first eligible redeemer may use one.
- Learners see the mentor and Track and confirm before access starts.
- Either party may end mentoring. Former mentors immediately lose access.
- Learners retain history and approvals. Pending submissions are recorded as ended without a decision and return to IN PROGRESS.
- Replacement mentors see retained history and review resubmitted work.

## Track and enrollment lifecycle — confirmed

- Existing enrollments retain their original requirements; updates affect new enrollments.
- Retired Tracks reject new enrollment but existing learners may continue.
- Leaving archives the enrollment and ends mentoring; pending work returns to IN PROGRESS.
- Returning restores the original requirements and progress, but not mentor access automatically.

## Notifications and operating scope — confirmed

- In-app submission alerts for mentors and a pending-review list.
- In-app decision alerts for learners and reply alerts for the other review participant.
- One community; account registration/access/recovery and administrator-assisted support/closure.
- Text/link evidence only; guidance against sharing confidential material. Mentors request accessible, shareable alternatives when links cannot be inspected.

## Deferred capabilities

Reopening approved work; migrating existing enrollments to updated requirements; uploads; email notifications; public profiles; mentor matching; certificates; payments; AI recommendations; standalone chat; gamification; enterprise capabilities.

## Outside the chosen MVP model

Mandatory earlier-level progression; multiple simultaneous mentors for one enrollment; self-approved DONE; separate final Track sign-off; administrator review overrides; multi-organization isolation; guarantees of external evidence accessibility or permanence.

## Open questions — resolve before launch

- Account closure/deletion versus retention of shared evidence and review history.
- Handling materially incorrect approvals while reopening and overrides are excluded.
- Limits, justification, visibility, and recording of administrator support access.
- Invitation eligibility, self-redemption, existing-mentor conflicts, and redemption before enrollment.
- Whether confidentiality guidance and administrator-assisted support suffice for pilot participants.

## Open questions — later refinement

Cross-Track evidence reuse/credit; backward WAITING/IN PROGRESS moves; obsolete notifications; accessibility/mobile expectations; discussion editing/deletion; accidental duplicate submissions; resuming enrollment in a retired Track.

## Assumptions awaiting confirmation

- One continuing enrollment per learner per Track, not parallel duplicate enrollments.
- Withdrawal returns work to IN PROGRESS.
- No promise of formal certification or standardized assessment consistency across mentors.

## Key risks

Forwarded codes may reach unintended people. External evidence may change or become inaccessible. Mentor availability can delay endorsed completion. Immutable approvals limit correction of mistakes.

## Refinement guardrails

Preserve stable story IDs and outcomes. Do not turn recommendations, assumptions, or open questions into confirmed rules. Do not expand scope implicitly. Ask about consequential missing behavior and flag cross-story effects. Do not introduce architecture, technology, schemas, APIs, estimates, sprint plans, or implementation unless separately requested. Detailed acceptance criteria require a subsequent request.
