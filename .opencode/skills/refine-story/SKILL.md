---
name: refine-story
description: Interactively refine one repository product story, or PLATFORM-01 foundation, into an approved User Story Template v2 artifact with dependency-merge gates, source provenance, and mechanical contract validation.
---

# Refine one story into the autonomous SDLC input contract

This is upstream refinement, outside the pipeline's two cognitive roles. Never
implement a story or operate the SDLC runtime. Other agents may reuse this skill,
but must obey the same write/command boundaries; the skill grants no permissions.

Paths below are repository-root-relative, except `scripts/validate_story.py`,
which is relative to this skill directory. Work from the repository root without
changing branches. The primary agent owns persona and machine permissions; this
skill owns the entire procedure. Do not change the template or spec to make a
story pass.

## 1. Sources, authority, and non-negotiable rules

Read these sources fully (continue truncated reads) before interpreting the
selected story:

1. `docs/plans/user-story-template-v2.md`: exact header shape, heading names,
   tables, and sections 01–25. Copy its structure, not its placeholder content.
2. `docs/plans/autonomous-agent-owned-sdlc-v2.1.md`: consumer contract. Pay special
   attention to §0.4, §1, §5.3, §7.1.2–7.1.6, §7.4.2–7.4.4, §9.1–9.2, §11.3,
   §13.4, §21.1, and §24.7. Runtime limits, staleness policy, risk rules, and
   story-check allowlists are runtime configuration, not new story header fields.
3. `docs/stories/active/2026-10-02/README.md` and `PRODUCT-CONTEXT.md`.
4. The selected product story and every product story in its Dependencies list;
   also read the refined versions of approved delivery dependencies if present.
5. `docs/plans/idea.md` (always read-only).
6. `docs/stories/refined/TECH-CONTEXT.md` if present. Its absence is not approval
   to invent conventions.

Read `pom.xml`, all `src/**`, wrappers/build definitions, and any current
`AGENTS.md`/CI/conventions for technical proposals in Phase B. Early read-only
inspection to establish foundation/dependency readiness is permitted, but do not
start technical refinement before the merge gate. Facts at the recorded base,
not uncommitted additions or the future implementation, ground Phase B.

- The invocation requests technical design and detailed acceptance criteria as
  required by the product pack; all other guardrails remain in force.
- Preserve stable product IDs, actors, benefits, scope classification, and
  confirmed outcomes. Recommended refinement order is context, not authority to
  start other stories. No implicit MVP expansion.
- Product sources, dependencies, idea, and TECH-CONTEXT conflicts are questions
  for the user. Do not silently select a winner or apply the story's internal
  precedence rule to conflicting input sources.
- No consequential gap may be filled by inference. Assumptions awaiting
  confirmation require confirmation **in this session**, then become `BR-n` or
  `D-n` with the user and original assumption as sources.
- No invented numbers, names, codes, defaults, policies, security obligations,
  telemetry names, NFR measurements, schema constraints, or command conventions.
  Repository/source facts may be cited directly; new choices require user
  confirmation. Explicitly label suggested values and rejected alternatives.
- A contract-ready artifact contains no unresolved questions, `TBD`, or
  unconfirmed assumptions. Relevant unanswered before-launch questions block it.
  Do not require decisions on unrelated stories merely because they share a
  launch checklist; ask which questions affect this story and record exclusions.
- Header obligations are authoritative. Every checkable FR, BR, E, NFR, SEC,
  OBS, CFG, and MUST-level IG item has exactly one `criteria` entry. Its prose
  elaboration uses the same ID and adds no unregistered obligations. SHOULD
  implementation suggestions (`IGS-n`) remain guidance, not criteria.
- Logical item IDs are unique across the artifact, not across token occurrences:
  required header/prose mirrors and references are valid; two different logical
  items may never share an ID. `CM-n`, `DOD-n`, `FX-n`, `GL-n`, `D-n`, `CT-n`,
  `ET-n`, `OOS-n`, `PR-n`, and other item namespaces also obey this rule. Do not
  restart numbering within a section. TD IDs are external source citations, not
  local definitions; copy relevant decisions into local D IDs.
- Preserve this exact precedence rule in the story's introductory template
  guidance: `18 Prohibited > 04/05/10 FR/BR/E > 11–14 NFR/SEC/OBS/CFG >
  06 Decisions > 16 Implementation guidance > 17 Codebase map`.
  Keep `ET-0`: `Sections conflict in a way the precedence rule does not resolve`.
  Other ET items identify observable, concrete stop situations, never "if unsure".

## 2. Session setup and provenance

1. Require exactly one story ID. Locate it by exact ID; never choose a story for
   the user. `PLATFORM-01` has no product-source file. Split-child IDs refer to
   their original parent source and approved allocation.
   New foundation work always uses `PLATFORM-`; the first is `PLATFORM-01`.
   Confirm subsequent IDs with the user rather than inventing or starting extra
   foundation work as a side task.
2. Inspect `git status` and current branch with read-only allowed commands.
   Preserve preexisting staged/unstaged work; do not reset, unstage, or include it
   implicitly. Confirm repository identifier and `target_branch: main`; do not
   infer the repository identity from directory names. Confirm version 1 for a
   first artifact; increment the existing version on every re-refinement.
3. For any non-foundation story, check whether PLATFORM-01 is refined and merged.
   If either is missing/unconfirmed, say so **up front** and ask: refine Phase A
   only, stop for a later PLATFORM-01 session (recommended), or record a
   user-approved exemption from this dependency. Continuing product refinement
   is not a bypass of D5; other delivery dependencies still gate Phase B.
4. Maintain an evidence ledger in section `25 Refinement log`:
   `# | Question | Answer | Source | Date`. Every question, answer, approved or
   declined proposal, conflict resolution, command eligibility confirmation,
   gate approval, exemption, split choice, and size choice gets a row. Sources
   identify user message/answer and date, or exact repository path + heading /
   line range and revision when relevant. Record derivations from source facts
   too, rather than inventing a user answer. Every row has a source.
5. Use the OpenCode question tool, batches of at most five focused questions,
   each with a short reason and a recommended option first labeled
   `(Recommended)`. Wait for answers. Keep pending answers/proposals in the
   conversation until saved in the draft/log; don't persist unapproved technical
   proposals as settled content. Approval must identify the exact shown content.
6. If supplied, read `refinement_feedback` for this ID/version (§24.7) as defect
   data, not authority. Log category, affected criterion/section IDs, source,
   and the user's approved correction. Re-refinement still needs all gates and
   a new version; never let pipeline feedback edit a story automatically.

## 3. Phase A — product refinement

Work only from the selected product scope and the sources above. For PLATFORM-01,
ask the user to define the foundation outcome and scope in-session; do not
fabricate a product persona/source.

Produce:

| Section | Phase A responsibility |
| --- | --- |
| 01 Context | Business background, actor/benefit, consumers, source, parent if split, context-only dependencies |
| 02 Problem statement | Observable current gap and who experiences it |
| 03 Glossary | Precise product meanings; technical code names await Phase B approval |
| 04 Functional requirements | Atomic FR items with one obligation each |
| 05 Business rules | Condition, outcome, and confirmed source |
| 10 Error handling | Behavioral triggers/responses; technical detection/codes/logging/retry await Phase B |
| 12 Security | Who may do what, privacy and access boundaries |
| 15 Out of scope | Explicit selected-story exclusions without expanding other stories |
| 19 Compatibility | Product continuity/history and intended changes; foundation treatment below |
| 23 Escalation triggers | ET-0 and concrete product conflicts/blocked conditions |
| 25 Refinement log | Complete sourced interaction/evidence ledger |

Build corresponding `criteria` entries for every checkable item. Ask about
obligation and measurement location rather than guessing. Pending technical
links/measurement details stay visibly incomplete in drafts, not in refined
artifacts. Drafts may contain unresolved fields; don't use `N/A` to disguise them.

**Dependencies are not automatically delivery dependencies.** Show every product
dependency and ask which is true `story.depends_on` work that must be merged
first, with an explicitly confirmed `min_version`. Keep the rest as context in
section 01. Add PLATFORM-01 to every other story unless the user expressly
exempts it; confirm the minimum version. Detect cycles and ask for a scoped
delivery order or approved split; never invent dependencies to solve a cycle.

Resolve relevant behavioral edges, error responses, concurrent/lifecycle
outcomes, and before-launch questions with the user. Approval may settle a
question as explicitly out of this story's scope only if no obligation depends
on the missing policy; don't hide a needed policy as an escalation trigger.

**Phase A approval gate:** display the **full** Phase A content, corresponding
criteria, proposed delivery/context dependency classification, and refinement
log, not just a summary. Ask for explicit approval. Rejected portions return to
questions. Save only approved Phase A content plus sourced blockers in the draft.
If consequential product questions remain unanswered, save the draft and stop.

## 4. Just-in-time gate and Phase B base

Phase B is allowed only when **every** approved `depends_on` dependency has been
merged into `main`. For each dependency:

1. Confirm `docs/stories/refined/<dependency-ID>.md` exists, is not a draft, and
   its header version meets `min_version`. This checks the refined artifact's
   presence, not the implementation's merge; do not infer a merge from it or
   require the artifact itself to have been merged as an extra prerequisite.
2. From that refined file's authoritative `scope.codebase_map.create`, check
   that **every** concrete path exists at `main` HEAD using `git show main:<path>`.
   If globbed, enumerate and confirm matches from the committed tree via
   read-only `git show main:<directory>` tree inspection. No matches fails;
   an empty create list has no path tests and is explicitly reported as vacuous.
   Existence is evidence, not proof of a MERGED runtime outcome.
3. Ask the user to confirm the dependency/version is merged into main and that
   the local main ref is current, supplying merge evidence when available.
   No fetch/network is permitted. Missing/stale local main, a missing refined
   file/path, insufficient version, or unconfirmed merge blocks Phase B.

Report all three results per dependency. Runtime §7.1.5 additionally requires a
MERGED run at sufficient version and merge-commit ancestry; user confirmation
and file existence do not waive that downstream check.

If any check fails, save the approved Phase A draft with an explicit Blocking
list naming the dependency/check and required human action, then end. Do not
technically refine against planned but unmerged dependency files.

At the **start of Phase B**, inspect `git status --porcelain` including staged,
unstaged, untracked files and both sides of renames. If **any** uncommitted change
is outside `docs/stories/`, stop and ask the user to resolve it; never commit or
discard it yourself. Resume only after the condition is cleared.

Record `git rev-parse HEAD` as the full 40-hex `story.refined_against_sha` **before
any refinement commit**; do not substitute a later commit SHA. Read relevant
technical evidence at this SHA with `git show <SHA>:<path>`. Report the main ref
and current branch. Ensure that SHA is in main's ancestry by inspecting
`git log main --format=%H`; if not, stop and ask for a human-established base.
Never switch branches or run disallowed `git merge-base`/`git diff` commands.

Inspect staleness against local main before emission: base ancestry; changes to
modify/reference/prohibited paths since the recorded SHA (read-only `git log`
with path selection, inspecting `git show` as needed); and create paths already
present on main. Also reject create paths already existing at the recorded SHA.
Uncommitted files intended as creates also require user resolution; don't
misclassify user work. A moved HEAD/base or changed relevant evidence requires
the user to restart the Phase B base/reapprove affected proposals; never silently
replace `refined_against_sha`. Downstream staleness validation still runs at intake.

## 5. Phase B — approved technical proposal groups

Read the current repository, but propose choices rather than silently selecting
them. Show each group's full content, header changes, sources, suggestions, and
cross-story effects. Ask for approval and write **only after** approval. A later
group changing an earlier approved item requires reapproval of that item. If
technical findings change product behavior, reopen Phase A approval explicitly.

Suggested groupings (not an obligation to use all five questions at once):

1. **Decisions and contracts:** 06, 07, 08, 09; approve glossary code names in
   03, type/risk, and the relevant TECH-CONTEXT decisions.
2. **Failure and quality controls:** complete 10 detection/codes/logging/retry;
   11 NFR numbers and measurement methods; approved technical additions to 12
   authentication/authorization/PII/secrets **preserving Phase A permissions**;
   13 signal names/formats; 14 configuration names/types/defaults per environment.
3. **Implementation boundaries:** 16 MUST constraints vs SHOULD guidance, 17
   exact create/modify/reference scope with purposes, 18 enforced prohibited
   paths vs non-path guidance; update 19/23 only after approval.
4. **Verification design:** 20 coverage, 21 fixtures, 22 environment, 24 DoD;
   mirror these exactly in `coverage`, `environment`, and `checks`.

Complete the original header, with no invented fields: `template_version`, every
`story` field (including ID/version/title/repository/main/base/type/risk/depends_on),
`criteria`, `scope`, `coverage`, `checks`, and `environment`. `risk: null` is a
valid explicitly approved unspecified declaration; a declared risk is only a
proposal, never the runtime's deterministic final classification (§5.3).

### Verification semantics

- `G`: MUST/MUST_NOT + `pipeline`; failures gate merge.
- `A`: SHOULD/SHOULD_NOT + `pipeline`; shortfalls are advisory, not FAIL.
- `F`: every `post_deploy` criterion; follow-ups never gate merge.
- MAY is not judged. Report its count separately; §0.4 set counts may overlap
  for MAY + post_deploy, so do not misstate them as a disjoint partition.
- Ask where/how each item can be measured. Anything unmeasurable in CI/local
  harness is `post_deploy`, not a fabricated pipeline test. Never downgrade a
  requirement simply to make it emit-ready.
- Coverage rows use approved scenarios, one of unit/component/integration/
  contract/e2e, resolvable fixtures, and the approved test_id convention. A
  non-empty `test_id` means every matched reported test must exist and pass.
  Leave it empty only if the name cannot be prescribed, with user-confirmed
  reason; then test adequacy is semantic. Design falsification/provocation cases
  for MUST_NOT/SHOULD_NOT and verification for every G and A item (§11.3).
- Every gating criterion needs at least one coverage row; advisory coverage is
  also proposed, not assumed proven by the gating-coverage mechanical test.
- Every checks command is a required trusted-harness gate, evaluated only by the
  template's `expect` keys. Prefer existing named wrappers. Build/test/run
  commands are sourced from AGENTS.md/CI; `environment.extra` contains only
  story-specific additions. Ask the user to confirm **each exact command** in
  checks and environment.extra as runtime allowlist-eligible; record evidence in
  section 25. Do not execute any of them or claim actual runtime registration.
- Preserve passed tests. Intentional removals/renames/disabling need an explicit
  `permitted_test_removals` pattern and non-empty approved reason, paired with
  the behavior change in 19 (§9.2). Never imply this waives assertion weakening.
- Explain map purposes and unmapped-change risks without promising that mapped
  or generated changes are automatically allowed by repository/runtime policy.

### TECH-CONTEXT

Cross-cutting choices belong in `docs/stories/refined/TECH-CONTEXT.md`, created
only when a session first needs an approved decision. Use unique `TD-n` entries
with **decision, rationale, rejected alternatives, date, approved-by**. Obtain
the approver identity from the user; don't invent a name. Show the exact new or
changed entries and wait for approval before writing. Preserve existing entries;
changing a settled one requires explicit user approval and an affected-story list.

Examples to ask about, not defaults: API-only vs UI, authentication mechanism,
package layout, test naming/test_id identity, error response shape, migration
conventions, wrapper command names. The skeleton's dependencies don't decide
these. Copy every relevant approved TD entry completely into story section 06
as a local `D-n`, with `Source: TECH-CONTEXT.md#TD-n` in the decision/rationale
cell and provenance in 25. Copy rationale and rejected alternatives, not merely a
pointer, so judges/delivery need no external context. Unworkable settled decisions
are concrete escalation triggers, not agent discretion to reopen them.

### PLATFORM-01 foundation

- ID `PLATFORM-01`, `type: foundation`, no product-story source and no automatic
  dependency on itself. Define all its requirements with the user in-session.
- Its purpose is to deliver the approved pipeline prerequisites: AGENTS.md,
  named story-check wrappers, and recorded conventions. This refiner writes only
  the **story**; implementation of those paths belongs to the delivery pipeline.
- Its own checks can name **only commands already existing at its recorded SHA**
  (for example, the Maven wrapper if present). Confirm exact arguments,
  expectations, and allowlist eligibility for each. Newly proposed wrappers
  cannot bootstrap their own checks. Do not run Maven to discover a result.
- Keep `environment.commands_ref: AGENTS.md` as the template's intended command
  reference, explaining that this foundation delivers it; do not pretend it
  already exists or is a source of existing commands. Source bootstrap commands
  from the actual wrapper/build evidence instead.
- Section 19 starts `N/A — foundation has no backward-compatibility requirement`,
  then adds the approved delivery note: AGENTS.md is protected under §9.1; its
  creation triggers `PROTECTED_PATH_MODIFIED` and requires a human, run-specific
  waiver. Record a concrete matching trigger in 23. Do **not** put AGENTS.md in
  the story's prohibited paths while also listing it as create (overlap invalid).
- Runtime `story_checks.allowed_commands` is **not a repository file**. This
  story may deliver wrappers; record the approved allowlist commands and human
  runtime-configuration follow-up in 19/23/25, not a fictional repository file or
  an extra header key. Allowlist eligibility is not actual runtime configuration.
  If a follow-up is expressed as a criterion, register it as `post_deploy`.
- Any waived protected-path violation still forces human merge approval (§9.8).

## 6. Shared product edits and cross-story effects

When a decision changes PRODUCT-CONTEXT or another product story, list **every
affected file and story ID**, display the exact proposed diff, and ask for explicit
approval before editing. Apply only that approved diff under `docs/stories/`.
`docs/plans/idea.md` is never edited even when it conflicts. Show source conflicts
in the ledger and explain whether shared updates were applied or left pending.
Reading dependencies does not authorize refining them. A necessary shared
correction withheld by the user blocks refined emission if it leaves the chosen
story inconsistent; optional unrelated follow-ups don't expand selected scope.

## 7. Size guard and splits

Before finishing Phase B, report:

1. Distinct FR count (all obligations and measurement locations).
2. Gating count `|G|`.
3. `|scope.codebase_map.create ∪ scope.codebase_map.modify|`, deduplicating paths.
   For globs, report both the pattern-entry count and committed/concrete file
   expansion where knowable; proposed creates need an approved concrete list
   before claiming a file count. Unknown counts require a question, not guessing.
4. Your reasoned assessment of size and whether to split.

**User-approved update to D13:** more than **10 distinct FR items** requires
splitting. This is the only fixed refiner threshold. For stories with ≤10 FR,
still ask whether to split based on gating/file counts and complexity. Do not
invent other limits. Runtime hard/soft limits remain authoritative downstream;
the user's refiner size choice cannot waive configured intake hard limits.

The agent devises a split **from this one selected parent story**, shows the
complete child scope/criterion allocation and delivery order, then waits for
approval. Child IDs are `<parent-ID>.1`, `.2`, …; each names its parent in 01 and
uses confirmed `depends_on` with `min_version` between parts where order matters.
Preserve all original outcomes and exclusions, without duplicate/conflicting
responsibility. Each child has its own unique local IDs, self-contained decisions,
coverage, fixtures, sourced log, approvals, size review, and self-check.

The same parent session may write its approved split children, never unrelated
stories. **Apply D5 separately to each child before its Phase B.** A sibling that
will be implemented later is not merged: ordered later children remain Phase A
drafts with explicit blockers. Independently ready children may receive approved
Phase B and refined emission. Reapprove any technical allocation after the split;
the parent's approval is not automatic child approval. Save a parent split-plan
draft, not a redundant deliverable contract containing the same work.

## 8. Contract self-check, per-criterion slices, and emission

Assemble the fully approved candidate **in a draft**, not in the refined path,
before validation. Show final content (or exact changes since full approved
groups) to the user. The candidate header/prose follows the original template;
the draft wrapper is not part of that candidate.

### Deterministic helper

Use `scripts/validate_story.py` with Python 3 and **preinstalled PyYAML**:

```text
python3 -B .opencode/skills/refine-story/scripts/validate_story.py docs/stories/refined/drafts/<ID>.md
```

Ask for execution permission. It is a read-only supporting tool, not a build,
test runner, runtime validator, or story-check runner. It reads exactly one file,
rejects path escapes/symlink inputs, parses YAML safely with duplicate-key
rejection, and prints JSON pass/fail results. It never installs dependencies,
executes header commands, reads network resources, or writes files. Nonzero exit
means no refined emission. Missing runtime/parser is a blocker; ask the human to
provide it, never install it as this refiner.

The helper understands template table/list item definitions and header mirrors.
For intersecting glob patterns it conservatively rejects cases whose disjointness
it cannot prove; refine them into concrete approved paths rather than waive a
possible overlap. The downstream runtime remains the authority for its own glob
semantics. Helper success is only mechanical evidence, never final contract PASS.

Maintainers can regression-test the helper with the synthetic in-memory fixtures
in `scripts/test_validate_story.py` using its documented unittest command. That
maintenance command is deliberately not permitted to the story-refiner agent;
it is not part of any story's checks or refinement session.

### Report each rule independently as PASS/FAIL with evidence

| Check | Required verification |
| --- | --- |
| §7.1.2 rule 1 | All required fields/types/enums present and meaningful; full 40-hex SHA; independently run `git cat-file -e <SHA>` and confirm success. No placeholder values. |
| Rule 2 | One logical item per ID across header/prose, required mirrors agree; no collisions or duplicate definitions. |
| Rule 3 | Every links/covers/fixture reference resolves; covers are criterion IDs; fixtures are defined FX items; no external TD citation masquerades as a link. |
| Rule 4 | Every criterion appears in prose and has matching meaning/obligation; every checkable prose requirement is registered exactly once (stricter than runtime warning). |
| Rule 5 | Every G criterion has ≥1 coverage row. |
| Rule 6 | User explicitly confirmed each exact checks/extra command as allowlist-eligible in 25; actual runtime matching remains an intake/execution requirement. Helper cannot certify this. |
| Rule 7 | Exact sections 01–25 each once, substantive/non-empty; `N/A — <reason>` is valid, empty tables and headings alone aren't content. |
| Rule 8 | No prohibited path/pattern intersects creates/modifies; use concrete expansions/conservative pattern checks, not mere string-set intersection. |
| Rule 9 | Every permitted-test-removal entry has non-empty reason and approved intended behavior change. |
| Staleness §7.1.6 | No create exists at recorded SHA; report SHA/main ancestry, relevant intervening changes, and creates already at main. HEAD/base stability rechecked. |
| Content settled | No unresolved questions, TBD, unconfirmed assumptions, invented decisions, or unresolved source conflicts. Log history of resolved questions is valid; unanswered history is not. |
| Header/prose mirrors | Scope, coverage, checks, environment agree exactly; all required item IDs/provenance and precedence/ET-0 present. |
| Dependency gate | All D5 checks still hold for every dependency/minimum version. |
| Size/approval | Count/assessment/choice recorded; >10 FR split; final content approved. |

Any FAIL, uncertain mandatory result, denied validator execution, or missing
confirmation blocks emission. Correct with user approval or save a blocked draft.
Don't claim shell permissions or user command confirmation certify runtime
configuration, merge outcomes, or future CI results.

### Slice completeness — check **every** criterion explicitly

Build an audit row per criterion ID with PASS/FAIL and missing context. Simulate
the deterministic §13.4 slice: criterion header + its prose; links **one level
deep only**; its coverage rows and fixtures; GL and D entries referenced by these;
bounded 01/02 summary; 15 and codebase map additionally for scope alignment.

Check whether that slice alone gives a judge the precise actors, conditions,
outcomes, data/examples, errors, exclusions relevant to that item, security
boundaries, and measurement method. Add minimal complete links (including related
CT/data/state anchored items where needed) instead of "see the rest of the
story". Put essential context in ID-anchored content, not unlinked narrative.
Do not rely on a transitive chain deeper than one link expansion or on reading
TECH-CONTEXT externally. Coverage presence alone does not prove slice adequacy.
For post_deploy/MAY items also verify coherent slices without pretending the
runtime judges them. Get approval for repairs to links or criterion meaning.

## 9. Output formats and final approval

- Ready: `docs/stories/refined/<ID>.md`. Exact template YAML header first, story
  title, original precedence guidance, and sections 01–25 in order with their
  original headings/tables. Remove instructional/sample placeholder content;
  retain applicable precedence and ET-0. All sections are substantive or
  `N/A — <specific reason>`. Do not add a Blocking wrapper to a ready artifact.
- Draft: `docs/stories/refined/drafts/<ID>.md`. Put `# Blocking` at the very top
  with explicit blocking questions/dependencies/actions, then the marker
  `<!-- refined-story-candidate -->` and the candidate beginning with its YAML
  `---` header if one is ready for mechanical checking. For Phase A-only drafts
  the header may be partial and technical sections visibly pending. They are
  **not** pipeline input; don't claim all self-checks pass. Log unanswered
  questions as `Unanswered — blocks emission` with the question's source.
- Shared decisions: `docs/stories/refined/TECH-CONTEXT.md`, approved TD entries
  only. Shared product inputs change only via section 6's exact-diff approval.

Ask explicit final artifact approval before writing the ready file. Run/report
all self-checks on the approved candidate **before** writing it there. A final
approval cannot waive contract failures. If an earlier refined version already
exists, preserve it when a new candidate is blocked; clearly warn that it remains
the old version/base and is not the blocked revision. No deletions/overwrites of
unrelated work. A validated draft may stay as the audit checkpoint; make its top
Blocking section say `None — emitted as <path>, version <n>` only after emission.

## 10. Commit gate and end-of-session report

After final artifact approval, propose the exact file list and commit message.
Ask for **separate explicit approval** before any git add/commit. Include only
session-approved docs/stories changes, not preexisting user changes even if
already staged. Compare reads to `git show HEAD:<path>` and show exact diffs when
needed; `git diff` is not an allowed shell command. If the same file contains
unrelated user work, stop for the human to separate it rather than stage it whole.
Record final/commit approval answers in 25 before staging. Revalidate any candidate
or ready file whose log changed; commit approval never authorizes changing its
obligations. Report the eventual commit SHA in the session report, not by making
an extra unapproved post-commit edit to the artifact.

Use `git add -- <exact-files>` then
`git commit --only -m '<approved-message>' -- <same-exact-files>` on the current
branch. Path-limited commit avoids accidentally committing unrelated staged
files; never use plain git commit with the whole index. Inspect status afterwards
and report the commit SHA. Never push, amend, bypass hooks, change Git config, or
perform Git cleanup. Hooks/signing may execute code or use the network outside
permission matching; ask about their safety before committing. If unavailable or
unsafe, leave files uncommitted for the human. Declined commit permission leaves
the approved artifacts written and reports that no commit occurred.

Draft-only sessions may propose a separately approved docs-only checkpoint
commit, but never call a draft a final artifact. The Phase B base SHA always stays
the pre-refinement-commit HEAD recorded in section 4.

End every session with:

1. Files written, ready vs draft/version, or no writes; draft's full Blocking list.
2. Each contract self-check's PASS/FAIL/not-run and the per-criterion slice audit.
3. Gating, advisory, follow-up, not-judged counts (unavailable if still undecided),
   FR/file counts, size/split decision.
4. Every cross-story effect, affected file/ID, and exact shared edit status
   (proposed/applied/declined/blocked).
5. Foundation/dependency readiness, runtime allowlist follow-ups, remaining human
   actions, and commit status/SHA if separately approved. No claims of build/test
   execution, pipeline readiness, or merge authority beyond the evidence.

Repository storage of refined stories is the upstream source of truth. The
pipeline consumes an immutable supplied artifact outside its delivery workspace
(§7.4.2); do not prescribe pipeline edits to these files or confuse their
repository location with permission for a DeliveryAgent to change its contract.
