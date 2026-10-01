# Career Path Mentor System — Story refinement pack

These 25 high-level stories were drafted from `../idea.md` and confirmed product-discovery decisions. Each story is stored separately for individual refinement. No implementation or detailed acceptance criteria have been produced.

## How to refine one story

Give the refining model:
1. `PRODUCT-CONTEXT.md`.
2. The selected story file.
3. Any dependency files listed in that story when the refinement affects their behavior.

Each story repeats the context needed for its own goal. The shared context remains necessary for cross-cutting permissions, exclusions, and unresolved policies.

Suggested handoff prompt:

> Refine the attached story using PRODUCT-CONTEXT.md and its local rules. Preserve its stable ID, actor, benefit, and scope classification. Distinguish confirmed requirements from assumptions and proposals. Do not silently resolve open questions or expand the MVP. Ask focused questions for consequential missing decisions. Flag conflicts with dependencies rather than changing them implicitly. Stay at the product-behavior level unless I explicitly request technical design or implementation. Add detailed acceptance criteria only if I request them.

## Index

| Epic | ID | Story |
| --- | --- | --- |
| Accounts | ACCOUNT-01 | [Access my account](ACCOUNT-01.md) |
| Accounts | ACCOUNT-02 | [Obtain support or close my account](ACCOUNT-02.md) |
| Track administration | TRACK-01 | [Define career targets](TRACK-01.md) |
| Track administration | TRACK-02 | [Update Tracks without disrupting learners](TRACK-02.md) |
| Track administration | TRACK-03 | [Retire a Track](TRACK-03.md) |
| Enrollment and progress | LEARN-01 | [Choose my development goals](LEARN-01.md) |
| Enrollment and progress | LEARN-02 | [Organize my work](LEARN-02.md) |
| Enrollment and progress | LEARN-03 | [Prepare evidence independently](LEARN-03.md) |
| Enrollment and progress | LEARN-04 | [Pause and resume a Track](LEARN-04.md) |
| Enrollment and progress | LEARN-05 | [Recognize endorsed completion](LEARN-05.md) |
| Mentoring | MENTOR-01 | [Approve mentors](MENTOR-01.md) |
| Mentoring | MENTOR-02 | [Invite a learner to Track mentoring](MENTOR-02.md) |
| Mentoring | MENTOR-03 | [Confirm mentoring access](MENTOR-03.md) |
| Mentoring | MENTOR-04 | [Understand an assigned learner’s progress](MENTOR-04.md) |
| Mentoring | MENTOR-05 | [End or replace mentoring safely](MENTOR-05.md) |
| Evidence and review | REVIEW-01 | [Submit demonstrated achievement](REVIEW-01.md) |
| Evidence and review | REVIEW-02 | [Withdraw and revise a submission](REVIEW-02.md) |
| Evidence and review | REVIEW-03 | [Discuss a submission](REVIEW-03.md) |
| Evidence and review | REVIEW-04 | [Decide a review outcome](REVIEW-04.md) |
| Evidence and review | REVIEW-05 | [Improve and resubmit](REVIEW-05.md) |
| Evidence and review | REVIEW-06 | [Understand the achievement history](REVIEW-06.md) |
| Review awareness | NOTIFY-01 | [Find work awaiting my review](NOTIFY-01.md) |
| Review awareness | NOTIFY-02 | [Learn about outcomes and replies](NOTIFY-02.md) |
| Support | SUPPORT-01 | [Resolve mentoring problems responsibly](SUPPORT-01.md) |
| Evidence boundaries | EVIDENCE-01 | [Share appropriate review evidence](EVIDENCE-01.md) |

## Recommended refinement order

1. REVIEW-01 through REVIEW-06: keep submission, withdrawal, feedback, and history coherent.
2. MENTOR-02, MENTOR-03, MENTOR-05: establish access boundaries and mentor replacement behavior.
3. ACCOUNT-02 and SUPPORT-01, alongside approval-correction policy: resolve trust-sensitive launch questions.
4. TRACK-02 and LEARN-04: verify preserved versions, retirement, and resumed progress.

Refinement should not overwrite `../idea.md`. If a new decision changes multiple stories, explicitly identify every affected ID and update shared context as well as the affected files when authorized.
