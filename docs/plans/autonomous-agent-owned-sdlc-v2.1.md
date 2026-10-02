# Autonomous Agent-Owned SDLC — Implementation Specification (v2.1)

> **Audience:** autonomous coding agents (Codex, Claude Code, OpenCode agents, or equivalent) implementing this runtime.
>
> **Purpose:** implement the smallest reliable SDLC that can take a fully refined, self-contained user story (in the format of the companion **User Story Template v2**) and deliver it autonomously through PR creation and merge to the target branch, with autonomy that is **earned from measured evidence**, not assumed.
>
> **Primary optimization order:**
>
> 1. Correctness / reliability
> 2. Lowest cost / fewest model calls
> 3. Delivery speed
>
> **Core architectural principle:**
>
> - Use **agents** for open-ended work.
> - Use **deterministic tools** for facts.
> - Use **JEV** (via `SemanticJudge`) for bounded semantic judgment.
> - Use **policy** for authority.
> - Use the **orchestrator only for state transitions**.
> - Grant **autonomy** only where measured evidence supports it.

---

# 0. How to Read This Document

## 0.1 Normative keywords

MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are used as defined in RFC 2119.

Each rule appears **once**, in Part I. Other sections refer to rules by section or invariant ID (`I-1` … `I-10`) instead of restating them.

## 0.2 Structure

```text
Part I     Normative specification        (implement this)
Part II    Implementation guidance        (order, DoD, config, interfaces)
Appendix A Rationale                      (non-normative; explains why)
Appendix B Changes from v1                (non-normative)
Appendix C Changes from v2                (non-normative)
```

If Appendix A appears to conflict with Part I, Part I wins.

## 0.3 Fail-closed configuration

Configuration values shown as `null` have no universal correct value. The implementer MUST expose them as configuration and MUST NOT invent defaults.

The engine MUST fail closed when they are missing:

- a missing value required for a state → the engine refuses to start;
- a missing value required only for autonomous merge → the affected scope is limited to `SHADOW` mode (§5).

## 0.4 Criteria terminology

The story header (§7.1) defines a **criterion set**. Each criterion has an `obligation` and a `verified_in` value.

```text
gating criteria    G = { c | c.obligation in {MUST, MUST_NOT}     and c.verified_in = pipeline }
advisory criteria  A = { c | c.obligation in {SHOULD, SHOULD_NOT} and c.verified_in = pipeline }
follow-ups         F = { c | c.verified_in = post_deploy }
not judged           = { c | c.obligation = MAY }
```

Throughout this specification, **acceptance criterion (AC)** means a member of `G ∪ A`. Every rule stated "per AC" applies to each member of `G ∪ A`. Only members of `G` can cause `FAIL`. Follow-ups never influence merge; they are recorded (§7.6, §18.3).

The pipeline MUST NOT infer obligations from prose. An item that appears only in the story's prose sections is guidance for agents, not a criterion.

---

# PART I — NORMATIVE SPECIFICATION

# 1. Mission

Build an autonomous SDLC runtime that receives a story already refined elsewhere, as a story artifact: a machine-readable header plus ID-anchored prose sections (User Story Template v2).

The input story MUST be treated as:

- self-contained;
- ready for implementation;
- sufficiently small for one delivery cycle;
- inclusive of its acceptance criteria;
- authoritative for scope and intent.

The SDLC MUST NOT perform story refinement. Story changes come only from the upstream refinement system (§17.3).

Delivery boundary:

```text
refined story
  -> implementation
  -> deterministic validation + integrity gate
  -> PR + CI
  -> independent verification
  -> evidence validation
  -> semantic judgment
  -> policy decision
  -> autonomy gate (or human approval)
  -> base sync
  -> merge to target branch
```

The system MUST support escalation when confidence, policy, integrity, budget, or repeated failure requires human intervention, and MUST support **resuming** a run after the human acts (§17).

---

# 2. Non-Goals

Do NOT introduce any of the following unless evaluation data (§24) proves they are necessary:

- manager, planner, architect, repair, documentation, or merge agents;
- dedicated unit-test or integration-test agents;
- dynamic agent graphs, LLM-driven routing, LLM-driven workflow planning;
- agent-generated workflow topology or autonomous role spawning;
- deployment, release, rollback, or production observation (see §18.4 for the precondition this creates).

There are exactly two cognitive roles:

1. `DeliveryAgent`
2. `VerifierAgent`

JEV, the orchestrator, the policy engine, the integrity gate, the evidence validator, and the autonomy gate are NOT agents.

---

# 3. Architectural Invariants

These MUST remain true unless the system owner explicitly changes them.

**I-1 Deterministic orchestration.**
The orchestrator tracks state, invokes components, enforces budgets, manages PRs, and merges when authorized. It MUST NOT interpret the story, write code, reason about implementation, choose agents by judgment, invent steps, skip mandatory gates, or make semantic judgments.

**I-2 Two agent roles.**
Only `DeliveryAgent` and `VerifierAgent` exist. Roles MAY be instantiated many times. Each instantiation SHOULD receive a fresh context unless a contract explicitly requires continuation. A role is persistent; a session is disposable.

**I-3 Authority separation.**
No probabilistic component may authorize anything.

```text
Agent        != authority
Verifier     != authority
JEV          != authority
LLM output   != authority
```

- Only the **PolicyEngine** may produce `PASS`.
- `PASS` permits merge only when the **AutonomyGate** also permits it, or an authorized human approves (§17).
- Any deterministic component (contract validator, gate, budget check, stall detector, evidence validator) MAY produce `ESCALATE`.
- Only deterministic components MAY route to `REPAIR`.

**I-4 Verification independence.**
The `VerifierAgent` MUST NOT receive the DeliveryAgent's reasoning, conversation history, plans, self-reports, or explanations not present in repository state. It receives factual state only. Its model MUST be independently configurable from the DeliveryAgent's (§10.2).

**I-5 Repository as memory.**
The repository is the canonical durable knowledge store. Do NOT create opaque global agent memory as the authoritative source for project knowledge.

**I-6 Agents cannot change the rules that judge them.**
No agent output may modify, weaken, or bypass the checks, thresholds, configuration, or instructions used to evaluate that same run without human approval. This is enforced deterministically by the IntegrityGate (§9), never by prompt compliance alone.

**I-7 Gate tooling is trusted, the branch is not.**
Integrity checks, evidence validation, policy evaluation, and the orchestrator MUST execute from the trusted base revision or a pinned external location, never from the agent-modified working tree.

**I-8 Evidence must be verifiable.**
Agent-reported evidence counts only after deterministic validation against recorded execution data (§12). Unvalidated evidence MUST be treated as absent.

**I-9 Autonomy is earned and scoped.**
Autonomous merge is permitted only for scopes whose measured performance meets configured promotion criteria (§5). Default mode is `SHADOW`.

**I-10 Merge what was validated.**
A merge MUST target exactly the commit SHA that passed all gates, against a base that commit was validated on (§18).

---

# 4. Core Separation (Summary)

```text
Agents own cognition.
Deterministic tools own facts.
The IntegrityGate owns the protection of the rules.
The Verifier owns independent evidence generation.
The EvidenceValidator owns the trust of evidence.
JEV owns bounded semantic judgment.
Policy owns the decision.
The AutonomyGate owns whether the decision may take effect unattended.
The orchestrator owns state.
The repository owns durable project knowledge.
```

Any proposed change that violates this separation requires explicit justification backed by evaluation data.

---

# 5. Autonomy Model

## 5.1 Modes

| Mode | Policy `PASS` leads to | Human role | Purpose |
|---|---|---|---|
| `SHADOW` | `AWAITING_HUMAN` (blind review) | Reviews **without** seeing policy outcome or JEV scores, then decides | Collect unbiased labels for calibration |
| `SUPERVISED` | `AWAITING_HUMAN` (approval) | Sees the full decision package, approves or rejects | Reduce review effort while trust is built |
| `AUTONOMOUS` | `SYNC_WITH_BASE` → `MERGE` | Handles escalations only | Unattended delivery |

`FAIL` → `REPAIR` and `ESCALATE` → human behave the same in every mode.

The default mode for every scope MUST be `SHADOW`.

## 5.2 Autonomy scope

Autonomy is configured per **scope**:

```text
scope = (repository, risk_class)
```

## 5.3 Risk classification

Risk class MUST be computed deterministically from the final diff, never by an LLM.

Inputs (configurable):

- paths touched, matched against configured high-risk path patterns (e.g. security, persistence migrations, public API contracts, configuration);
- dependency manifest changes;
- diff size (files, lines);
- count of gating criteria;
- story `type` (`foundation` stories MAY be mapped to a higher minimum class);
- **unmapped changes**: files changed outside the story's `codebase_map.create ∪ codebase_map.modify`;
- story size relative to the soft limits in §7.1.4;
- optional `risk` field declared on the story.

```text
effective_risk = max(declared_risk, computed_risk)
```

Risk is recomputed whenever the diff changes. A run MUST use the most recent value at `AUTONOMY_GATE`.

## 5.4 Promotion

A scope MAY move `SHADOW → SUPERVISED → AUTONOMOUS` only when configured criteria are met, measured on labelled runs (§24.3):

```yaml
promotion_criteria:
  min_labelled_runs: null
  max_false_accept_rate: null      # upper confidence bound, not point estimate
  max_false_reject_rate: null
  confidence_level: null
  min_observation_window_days: null
```

Promotion MUST be an explicit, recorded action by an authorized human. The system MAY recommend promotion; it MUST NOT promote itself.

## 5.5 Demotion

Demotion MUST be automatic and immediate when any of the following occurs:

- an **escaped defect** is attributed to a run in that scope (§24.4);
- the false-accept upper bound exceeds the configured maximum;
- any **calibration-invalidating change** occurs (§5.6).

```yaml
demotion:
  on_escaped_defect: null          # target mode
  on_threshold_breach: null
  on_calibration_invalidation: null
```

## 5.6 Calibration-invalidating changes

Calibration evidence applies only to the exact configuration that produced it. Each of the following invalidates it for affected scopes:

- DeliveryAgent, VerifierAgent, or SemanticJudge model or version change;
- system prompt or agent instruction template change in the runtime;
- policy version change (§14.5);
- calibration map change (§13.6).

Affected scopes revert to the configured demotion mode until re-qualified.

## 5.7 Kill switch

A global and per-repository kill switch MUST exist.

When active:

- no new runs start;
- in-flight runs move to `PAUSED` at their next transition;
- no merge occurs.

Lifting the switch resumes paused runs from their recorded state.

## 5.8 Deployment precondition

See §18.4. A scope whose target branch auto-deploys to production MUST NOT be `AUTONOMOUS` unless the configured deployment safeguards are explicitly acknowledged.

---

# 6. Workflow State Machine

## 6.1 Overview (happy path and main loops)

```text
STORY_RECEIVED
      |
      v
PREPARE_WORKSPACE
      |
      v
DELIVERY <------------------------------------------+
      |                                             |
      v                                             |
LOCAL_VALIDATION ---- deterministic FAIL --> REPAIR-+
      |                                       ^
      v                                       |
INTEGRITY_GATE ------ violation --------------+
      |                                       |
      v                                       |
CREATE_OR_UPDATE_PR                           |
      |                                       |
      v                                       |
CI_VALIDATION ------- deterministic FAIL -----+
      |                                       |
      v                                       |
VERIFY                                        |
      |                                       |
      v                                       |
EVIDENCE_VALIDATION                           |
      |                                       |
      v                                       |
SEMANTIC_JUDGMENT                             |
      |                                       |
      v                                       |
POLICY_DECISION ----- FAIL -------------------+
      |       \
      | PASS   +----- ESCALATE ---> ESCALATE ---> AWAITING_HUMAN
      v
AUTONOMY_GATE ------- human required -----------> AWAITING_HUMAN
      |
      v
SYNC_WITH_BASE ------ base moved -> LOCAL_VALIDATION (revalidation)
      |
      v
MERGE
      |
      v
DONE

Side paths (any state that touches infrastructure):
  infra / flaky / tool failure --> INFRA_RETRY --> originating state
  retries exhausted            --> ESCALATE

REPAIR: budget exhausted or stalled --> ESCALATE
Kill switch: any state --> PAUSED --> same state on release
```

## 6.2 Transition table (authoritative)

The diagram is illustrative. **This table is normative.** Any situation not covered by the table MUST route to `ESCALATE` with category `UNHANDLED_TRANSITION`.

| From | Condition | To | Failure category |
|---|---|---|---|
| `STORY_RECEIVED` | contract valid | `PREPARE_WORKSPACE` | |
| `STORY_RECEIVED` | contract invalid | `ESCALATE` | `STORY_CONTRACT_INVALID` |
| `STORY_RECEIVED` | hard size limit exceeded | `ESCALATE` | `STORY_TOO_LARGE` |
| `STORY_RECEIVED` | a dependency is not merged | `ESCALATE` | `DEPENDENCY_NOT_MERGED` |
| `STORY_RECEIVED` | stale and `story.stale_action = ESCALATE` | `ESCALATE` | `STORY_STALE` |
| `STORY_RECEIVED` | run with same idempotency key active | reject start | `DUPLICATE_RUN` |
| `PREPARE_WORKSPACE` | ready | `DELIVERY` | |
| `PREPARE_WORKSPACE` | infrastructure error | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` |
| `DELIVERY` | status `completed`, non-empty diff vs base | `LOCAL_VALIDATION` | |
| `DELIVERY` | status `blocked` (with or without a story escalation trigger ID) | `ESCALATE` | `DELIVERY_BLOCKED` |
| `DELIVERY` | empty diff vs base | `ESCALATE` | `NO_CHANGES` |
| `DELIVERY` | reports disputed oracle (§11.4) | `ESCALATE` | `ORACLE_DISPUTED` |
| `DELIVERY` | agent runtime / tool failure | `INFRA_RETRY` | `AGENT_RUNTIME_FAILURE` |
| `LOCAL_VALIDATION` | all required checks pass | `INTEGRITY_GATE` | |
| `LOCAL_VALIDATION` | deterministic failure | `REPAIR` | `LOCAL_VALIDATION_FAILED` |
| `LOCAL_VALIDATION` | story DoD check failed (§7.4.2) | `REPAIR` | `STORY_CHECK_FAILED` |
| `LOCAL_VALIDATION` | coverage-matrix test missing or failing (§7.4.3) | `REPAIR` | `COVERAGE_MATRIX_UNMET` |
| `LOCAL_VALIDATION` | failure classified infra / flaky (§15.2) | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` / `FLAKY_CHECK` |
| `LOCAL_VALIDATION` | same failure reproduces on base (§15.3) | `ESCALATE` | `PRE_EXISTING_FAILURE` |
| `INTEGRITY_GATE` | no violations, or all waived | `CREATE_OR_UPDATE_PR` | |
| `INTEGRITY_GATE` | protected-path violation | `ESCALATE` | `PROTECTED_PATH_MODIFIED` |
| `INTEGRITY_GATE` | test-integrity / coverage / suppression violation | `REPAIR` | `INTEGRITY_VIOLATION` |
| `CREATE_OR_UPDATE_PR` | PR exists at current head | `CI_VALIDATION` | |
| `CREATE_OR_UPDATE_PR` | provider error | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` |
| `CI_VALIDATION` | required CI passes on current head SHA | `VERIFY` (or `SYNC_WITH_BASE` if revalidation skips verification, §18.2) | |
| `CI_VALIDATION` | deterministic failure | `REPAIR` | `CI_FAILED` |
| `CI_VALIDATION` | infra / flaky | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` / `FLAKY_CHECK` |
| `CI_VALIDATION` | same failure reproduces on base | `ESCALATE` | `PRE_EXISTING_FAILURE` |
| `VERIFY` | verifier returns structured output | `EVIDENCE_VALIDATION` | |
| `VERIFY` | runtime / tool failure | `INFRA_RETRY` | `AGENT_RUNTIME_FAILURE` |
| `EVIDENCE_VALIDATION` | evidence valid | `SEMANTIC_JUDGMENT` | |
| `EVIDENCE_VALIDATION` | fabricated evidence, verifier attempts remain | `VERIFY` (fresh session) | `EVIDENCE_FABRICATED` |
| `EVIDENCE_VALIDATION` | fabricated evidence, attempts exhausted | `ESCALATE` | `EVIDENCE_INVALID` |
| `SEMANTIC_JUDGMENT` | all required judgments returned | `POLICY_DECISION` | |
| `SEMANTIC_JUDGMENT` | provider error | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` |
| `POLICY_DECISION` | `PASS` | `AUTONOMY_GATE` | |
| `POLICY_DECISION` | `FAIL` | `REPAIR` | `VERIFICATION_FAILED` / `SEMANTIC_FAILURE` |
| `POLICY_DECISION` | `ESCALATE` | `ESCALATE` | `SEMANTIC_UNCERTAINTY` / `POLICY_ESCALATION` |
| `AUTONOMY_GATE` | scope `AUTONOMOUS` and permitted | `SYNC_WITH_BASE` | |
| `AUTONOMY_GATE` | scope `SHADOW` / `SUPERVISED` | `AWAITING_HUMAN` | `APPROVAL_REQUIRED` |
| `SYNC_WITH_BASE` | head validated against current base | `MERGE` | |
| `SYNC_WITH_BASE` | base advanced, clean update | `LOCAL_VALIDATION` (revalidation) | |
| `SYNC_WITH_BASE` | conflict | `REPAIR` | `MERGE_CONFLICT` |
| `MERGE` | merged at expected SHA | `DONE` (`MERGED`) | |
| `MERGE` | head SHA ≠ validated SHA | `LOCAL_VALIDATION` | `HEAD_CHANGED` |
| `MERGE` | rejected by platform rules | `ESCALATE` | `MERGE_FAILURE` |
| `MERGE` | transient provider error | `INFRA_RETRY` | `INFRASTRUCTURE_FAILURE` |
| `REPAIR` | repair budget remains, no stall | `DELIVERY` (repair mode) | |
| `REPAIR` | repair budget exhausted | `ESCALATE` | `REPAIR_BUDGET_EXHAUSTED` |
| `REPAIR` | stall detected (§16.4) | `ESCALATE` | `REPAIR_STALLED` |
| `INFRA_RETRY` | retries remain | originating state | |
| `INFRA_RETRY` | retries exhausted | `ESCALATE` | `INFRASTRUCTURE_FAILURE` |
| `ESCALATE` | package emitted | `AWAITING_HUMAN` | |
| `AWAITING_HUMAN` | human resolution (§17.3) | per resolution | |
| `AWAITING_HUMAN` | escalation timeout | `DONE` (`EXPIRED`) | |
| any | run cost or wall-clock budget exceeded | `ESCALATE` | `RUN_BUDGET_EXHAUSTED` |
| any | kill switch active | `PAUSED` | |
| `PAUSED` | kill switch released | recorded state | |

Terminal outcomes: `MERGED`, `ABANDONED`, `EXPIRED`.

`ESCALATE` is NOT terminal.

---

# 7. State Definitions

## 7.1 `STORY_RECEIVED`

Intake runs entirely deterministically and before any model call, in this order: contract (§7.1.2), size (§7.1.4), dependencies (§7.1.5), staleness (§7.1.6). The first failing check decides.

### 7.1.1 Story artifact

The input is a story artifact in the format of User Story Template v2:

- a **machine-readable header** (YAML front matter), which is authoritative for IDs, obligations, paths, coverage, and checks;
- **ID-anchored prose sections** `01`–`25`, which give agents context and elaborate header items by ID.

The orchestrator reads only the header. Agents read both.

Normative header shape:

```yaml
template_version:                       # engine MUST reject unknown major versions
story:
  id:
  version:
  type: foundation | change
  title:
  repository:
  target_branch:
  refined_against_sha:
  risk:                                 # optional
  depends_on: [{ story_id, min_version }]
criteria:
  - { id, kind, obligation, verified_in, text, links: [] }
scope:
  codebase_map: { create: [], modify: [], reference: [] }
  prohibited_paths: []
  permitted_test_removals: [{ test_id_pattern, reason }]
coverage:
  - { id, covers: [], scenario, level, fixture, test_id }
checks:
  - { id, command, expect: { exit_code, stdout_contains, stdout_not_contains, file_exists } }
environment:
  commands_ref:
  extra: [{ purpose, command }]
```

### 7.1.2 Contract validation

All of the following MUST hold; otherwise → `ESCALATE` (`STORY_CONTRACT_INVALID`) with the list of violated rules.

1. Required header fields are present. `refined_against_sha` is a full SHA that exists in the repository.
2. All IDs are unique across the artifact.
3. Every `links`, `covers`, and `fixture` reference resolves to an ID defined in the header or in the prose.
4. Every criterion ID appears in the prose body. (The reverse direction — every prose item with a MUST/MUST NOT keyword appears in the header — SHOULD be checked and reported as a warning, because prose parsing is less reliable.)
5. Every gating criterion is covered by at least one `coverage` row.
6. Every `checks[].command` and `environment.extra[].command` matches the repository's story-check allowlist (§21).
7. Every section heading `01`–`25` is present and non-empty. `N/A — <reason>` is valid; an empty section is not.
8. `scope.prohibited_paths` does not overlap `scope.codebase_map.create ∪ scope.codebase_map.modify`.
9. Every `permitted_test_removals` entry has a non-empty `reason`.

The pipeline MUST NOT repair, complete, or reinterpret an invalid story. Corrections come from the refinement system as a new story version.

### 7.1.3 Idempotency

Idempotency key: `(repository, story.id, story.version)`. A second run with an active key MUST be rejected.

### 7.1.4 Size limits

```yaml
story:
  limits:
    gating_criteria:      { soft: null, hard: null }
    codebase_map_files:   { soft: null, hard: null }   # |create ∪ modify|
```

- Above a **hard** limit → `ESCALATE` (`STORY_TOO_LARGE`). The story must be split during refinement.
- Above a **soft** limit → proceed, and the risk classifier raises the run's risk class (§5.3).

### 7.1.5 Dependencies

For each `depends_on` entry, a run for that story with `version ≥ min_version` MUST have terminal outcome `MERGED`, and its merge commit MUST be an ancestor of the current base revision. Otherwise → `ESCALATE` (`DEPENDENCY_NOT_MERGED`).

### 7.1.6 Staleness

A story is **stale** when any of the following holds:

- `refined_against_sha` is not an ancestor of the current base revision;
- any file matching `codebase_map.modify`, `codebase_map.reference`, or `prohibited_paths` changed between `refined_against_sha` and the current base;
- any path in `codebase_map.create` already exists at the current base.

Action is configured by `story.stale_action`:

- `ESCALATE` → `ESCALATE` (`STORY_STALE`). Typical resolutions: `STORY_AMENDED` (re-refined against a newer SHA) or `WAIVE_AND_CONTINUE`.
- `WARN` → proceed; record the stale paths in the run; raise the risk class by one level; include the stale paths in agent context.

## 7.2 `PREPARE_WORKSPACE`

Create isolated working state (branch, worktree, temporary checkout, or sandbox). The mechanism is project-specific; the contract is generic.

The orchestrator MUST:

- record the base revision SHA;
- acquire the per-run branch lock;
- respect `workflow.max_concurrent_runs_per_repository`;
- capture the **base test inventory** (§9.3) for the recorded base revision, or reuse a cached inventory for that SHA.

Output:

```yaml
workspace:
  repository:
  base_revision:
  branch:
  working_path:
  base_test_inventory_ref:
```

## 7.3 `DELIVERY`

Invoke a fresh `DeliveryAgent` session (§8).

In repair mode, the session receives the repair context (§16.2).

The top-level instruction SHOULD remain minimal:

```text
Initial:  Deliver this story completely within the constraints of this repository.
Repair:   Resolve the identified delivery failure while preserving all previously satisfied requirements.
```

Do NOT encode a rigid internal plan in the orchestration layer. The agent owns its internal execution loop.

## 7.4 `LOCAL_VALIDATION`

### 7.4.1 Project checks

Run deterministic project-specific checks, for example: compile, unit tests, integration tests, lint, format, static analysis, type checking, security scanning, architecture tests, schema validation, forbidden-dependency rules, generated-file consistency, and all **repro oracles** collected so far (§11.4).

Commands MUST come from project specialization (§19), not from the generic engine.

Test results MUST be collected in a machine-readable report format so the test inventory can be computed (§9.3).

Failures MUST be classified (§15) before routing.

### 7.4.2 Story checks (Definition of Done)

Every `checks[]` entry in the story header is a required deterministic check for this run.

- It MUST be executed by the trusted harness (I-7), in the workspace, after project checks pass.
- Its command MUST match the story-check allowlist (§21); this was validated at intake and MUST be re-validated before execution.
- Its result is evaluated only against `expect` (`exit_code`, `stdout_contains`, `stdout_not_contains`, `file_exists`). All stated expectations MUST hold.
- A failing story check → `REPAIR` (`STORY_CHECK_FAILED`), with the check ID, command, expectation, and output excerpt as failure context.
- Story checks are part of every `LOCAL_VALIDATION`, including revalidation after repair and after base sync.

Because the story artifact lives outside the repository, agents cannot edit story checks.

### 7.4.3 Coverage-matrix check

For every `coverage[]` row with a non-empty `test_id`, the head test inventory (§9.3) MUST contain at least one matching test, and every matching test MUST have passed.

- Missing or failing → `REPAIR` (`COVERAGE_MATRIX_UNMET`), listing the row IDs and the criteria they cover.
- Rows without `test_id` are not checked deterministically; their adequacy is judged by `tests_adequate` (§13.3).

### 7.4.4 Unmapped changes

The orchestrator MUST compute **unmapped changes**: files in the diff that match neither `codebase_map.create` nor `codebase_map.modify`. Test files and files under paths configured as `scope.always_mapped` (e.g. lockfiles generated by allowed tooling) are excluded.

Unmapped changes do not fail the run. They are:

- an input to the risk classifier (§5.3);
- an input to the `scope_alignment` judgment (§13.4);
- handled per `scope.unmapped_change_action`: `none`, `raise_risk`, or `escalate` (→ `ESCALATE` with `POLICY_ESCALATION`).

## 7.5 `INTEGRITY_GATE`

Run the IntegrityGate (§9) on the diff between base revision and current head.

## 7.6 `CREATE_OR_UPDATE_PR`

PR lifecycle is infrastructure responsibility. Create the PR if absent; update it if present. The PR description SHOULD be generated deterministically from the story header: story ID and version, run ID, gating and advisory criteria, and a **Follow-ups** list of all post-deploy criteria (`F`, §0.4) so that they are visible to the people who own deployment.

Do not merge here.

## 7.7 `CI_VALIDATION`

Run or await configured CI for the **current head SHA**. A CI result for any other SHA MUST be ignored.

CI SHOULD re-run the IntegrityGate from trusted tooling (I-7), so local results are not the only enforcement.

Default order: CI first, verifier second.

## 7.8 `VERIFY`

Invoke a fresh `VerifierAgent` session (§10).

## 7.9 `EVIDENCE_VALIDATION`

Run the EvidenceValidator (§12).

## 7.10 `SEMANTIC_JUDGMENT`

Invoke `SemanticJudge` for each required judgment (§13), using validated evidence only.

## 7.11 `POLICY_DECISION`

Invoke the PolicyEngine (§14). It returns exactly one of `PASS`, `FAIL`, `ESCALATE`.

## 7.12 `AUTONOMY_GATE`

Deterministically determine whether this `PASS` may proceed without a human:

```text
permitted =
      scope_mode(repository, effective_risk) == AUTONOMOUS
  AND kill_switch inactive
  AND deployment precondition satisfied (§18.4)
  AND no waivers granted in this run that require human merge approval
```

## 7.13 `SYNC_WITH_BASE`

See §18.

## 7.14 `MERGE`

See §18.3.

## 7.15 `REPAIR`

See §16.

## 7.16 `INFRA_RETRY`

See §15.4.

## 7.17 `ESCALATE` and `AWAITING_HUMAN`

See §17.

---

# 8. DeliveryAgent Contract

## 8.1 Objective

The `DeliveryAgent` is constructive. Its responsibility:

> Make the story true in the repository.

It SHOULD autonomously perform whatever project-allowed work is required: exploration, inspection, internal planning, implementation, test creation and modification, debugging, builds, static checks, documentation updates, knowledge updates, and commits.

## 8.2 Test ownership

The DeliveryAgent MUST be allowed to write and modify tests, so it can iterate:

```text
inspect -> implement -> test -> observe failure -> repair -> test
```

DeliveryAgent tests are NOT independent proof of correctness, and modifications to existing tests are subject to the IntegrityGate (§9).

## 8.3 Repository autonomy

The DeliveryAgent MAY inspect allowed content, run project commands, use tools, modify production code, tests, docs, skills, and knowledge artifacts, and commit.

Restrictions MUST be defined by project policy: `AGENTS.md` for guidance, and machine-enforced controls (§21, §9) for hard boundaries.

## 8.4 Inputs

```text
full story artifact (header + prose), including the precedence rule
repository, AGENTS.md, documentation, skills
available development tools, project constraints
current branch/workspace
stale paths, if the story was accepted with stale_action = WARN
[repair mode] repair context (§16.2)
```

The DeliveryAgent MUST NOT receive policy thresholds, calibration data, autonomy configuration, or JEV probability values (Appendix A.7).

## 8.5 Output

```yaml
delivery_result:
  status: completed | blocked
  commit:
  changed_files: [ { path } ]
  tests_added: [ { path } ]
  tests_modified: [ { path } ]
  knowledge_updated: [ { path } ]
  unresolved_blockers: [ { description } ]
  escalation_trigger:               # story ET-n ID when status = blocked because of a story trigger
  disputed_oracles:                 # repair mode only, §11.4
    - oracle_id:
      reason:
      evidence_refs: []
```

This metadata is informational and routing-relevant only through the fields named in the transition table (`status`, `disputed_oracles`). `escalation_trigger` is recorded in the escalation package and telemetry.

## 8.6 Story escalation triggers

The DeliveryAgent MUST return `status: blocked` with the trigger ID when any of the story's escalation triggers (section 23, including `ET-0` for unresolvable section conflicts) occurs. It MUST NOT decide those situations itself. It MUST NOT be trusted as proof of correctness. The diff is computed by the orchestrator, not taken from this output.

---

# 9. IntegrityGate

The IntegrityGate enforces I-6 deterministically. It runs from trusted tooling (I-7) at `INTEGRITY_GATE` and again in CI.

## 9.1 Protected paths

```yaml
integrity:
  protected_paths: null   # MUST be non-empty; the engine refuses to start otherwise
```

The protected set MUST cover at least the project's equivalents of:

- CI/CD definitions;
- this runtime's workflow, policy, autonomy, and calibration configuration;
- validator, gate, and evidence-tooling scripts;
- `AGENTS.md` and other agent instruction files;
- code ownership and branch protection files;
- quality-threshold configuration (coverage thresholds, lint rule sets, static-analysis baselines, suppression files);
- dependency lock or allowlist files, if the project treats them as controlled.

For each run, the effective protected set is:

```text
effective_protected = integrity.protected_paths ∪ story.scope.prohibited_paths
```

Any modification (add, change, delete, rename) of an effectively protected path → `ESCALATE` (`PROTECTED_PATH_MODIFIED`). The escalation package states whether the path was repository-protected or story-prohibited.

This is how legitimate knowledge updates to `AGENTS.md` still reach `main`: a human approves them through the waiver path (§17.3).

## 9.2 Test integrity

The gate compares the **base test inventory** with the **head test inventory**. Each inventory is computed from machine-readable test reports and lists each test's identifier and outcome (passed, failed, skipped/disabled).

A violation exists when a test that **passed on base**:

- no longer exists on head; or
- is skipped or disabled on head;

unless its identifier matches a `scope.permitted_test_removals` pattern in the story header.

Renamed tests count as removed unless the project's `TestIdentityResolver` (§19) maps old to new identity deterministically.

## 9.3 Test inventory

```text
TestInventory = { test_id -> outcome } derived from test reports for a given SHA
```

The base inventory MUST come from running the suite at the recorded base revision (cached per SHA). It MUST NOT be reconstructed from agent claims.

## 9.4 Assertion weakening

Assertion removal and weakening are language-specific. The generic engine MUST expose an extension point:

```java
interface TestWeakeningDetector {
    List<IntegrityViolation> detect(Diff diff, Workspace workspace);
}
```

Projects SHOULD provide implementations (e.g. removed assertions, broadened matchers, newly caught-and-ignored exceptions in tests). Findings are integrity violations.

## 9.5 Coverage ratchet

```yaml
integrity:
  coverage:
    changed_lines_min: null
    max_overall_drop: null
```

If coverage measurement is configured:

- changed-line coverage below `changed_lines_min` → violation;
- overall coverage drop greater than `max_overall_drop` → violation.

## 9.6 Suppressions

Projects SHOULD provide a `SuppressionDetector` that counts suppression markers in the diff (lint ignores, warning suppressions, static-analysis exclusions). Net new suppressions above the configured allowance → violation.

## 9.7 Routing

- Protected-path violation → `ESCALATE`.
- All other violations → `REPAIR`, with the violation list as factual failure context.
- A repeated identical violation is caught by stall detection (§16.4).

## 9.8 Waivers

A human MAY waive a specific violation for a specific run (§17.3). Waivers are keyed by violation fingerprint, recorded with identity and reason, and never carried to other runs. A run with any waiver MUST require human merge approval at `AUTONOMY_GATE`.

---

# 10. VerifierAgent Contract

## 10.1 Objective

The `VerifierAgent` is adversarial. Its responsibility:

> Attempt to falsify the claim that the story has been correctly delivered.

It is an independent evidence generator, not a conventional "looks good" reviewer.

## 10.2 Fresh context and model independence

Each verification attempt MUST use a new session.

```yaml
agents:
  delivery:
    model: null
  verifier:
    model: null
    require_different_model_family: null
```

The verifier model MUST be independently configurable. Using a different model family from the DeliveryAgent is RECOMMENDED, because same-model verification shares blind spots. The choice MUST be recorded per run and evaluated (§24).

## 10.3 Inputs

```text
full story artifact (header + prose)
repository at current head SHA
current diff and commits
committed tests
CI results and deterministic gate results
previously collected repro oracles and their current status
AGENTS.md, project documentation, skills
verification tools
```

It MUST NOT receive anything excluded by I-4, nor policy thresholds, calibration data, or prior JEV outputs.

## 10.4 Allowed actions

The VerifierAgent MAY inspect history, code, and tests; run builds, tests, and services; inspect logs; issue HTTP/API requests; probe edge cases; create temporary tests and scripts; run property-based tests and fuzzing; test concurrency, error conditions, persistence, compatibility, and configuration behavior; and compare the implementation to acceptance criteria.

All tool executions MUST go through the `AgentRunner` harness, which records them (§12.1).

## 10.5 Production modification restriction

The VerifierAgent MUST NOT modify committed production code, committed tests, or any repository content on the delivery branch. It MUST NOT repair what it evaluates.

It MAY create ephemeral artifacts in a sandbox outside committed state (e.g. `.tmp/verification/`). The orchestrator MUST verify after `VERIFY` that the branch head is unchanged; if it changed → `ESCALATE` (`VERIFIER_MODIFIED_BRANCH`).

```text
Allowed:  VerifierAgent -> evidence -> policy -> DeliveryAgent repair
Forbidden: VerifierAgent -> fixes production code -> verifies own fix
```

---

# 11. Verification Evidence Contract

## 11.1 Shape

```yaml
verification:
  head_sha:
  acceptance_criteria:
    - id: AC-001
      claim: "..."
      evidence:
        - type: test | command | runtime_observation | code
          execution_id:          # required for test, command, runtime_observation
          reference:             # test id, command, endpoint, or path#Lstart-Lend
          claimed_outcome:       # e.g. passed, failed, exit_code=0, status=200
      counterexample_search:
        - description:
          execution_ids: []
      findings:
        - id:
          severity: none | low | medium | high | critical
          description:
          evidence_refs: []
          repro_oracle:          # required for severity >= configured level
      unresolved_uncertainty:
        - description:
```

## 11.2 Separation of concerns

The verifier MUST distinguish evidence, findings, and uncertainty. It MUST NOT collapse them into a prose verdict. Outputs such as `LGTM`, `7/10`, or `probably correct` are invalid.

## 11.3 Coverage of criteria

Every criterion in `G ∪ A` (§0.4) MUST appear in the output. A missing criterion is treated as having no evidence. Follow-up (`post_deploy`) and `MAY` criteria MUST NOT be required, and evidence for them is ignored by policy.

For `MUST_NOT` and `SHOULD_NOT` criteria, the claim to falsify is that the prohibited behavior does not occur; the verifier SHOULD actively attempt to provoke it.

## 11.4 Repro oracles

When a finding's severity is at or above `verification.repro_required_severity` (configurable), the verifier MUST attach a **repro oracle**: a self-contained test or script that fails on the current head, with an `execution_id` showing the failure.

The orchestrator stores validated oracles in the run's artifact store, outside the branch. From then on:

- every `LOCAL_VALIDATION` in this run MUST execute all stored oracles as required checks;
- an oracle that fails is a deterministic failure (§7.4);
- the repair session receives oracles as executable targets and SHOULD commit an equivalent permanent test;
- if the DeliveryAgent believes an oracle is wrong, it reports it in `disputed_oracles`, which routes to `ESCALATE` (`ORACLE_DISPUTED`). Humans arbitrate oracle validity; agents do not.

A finding at or above the required severity without a valid oracle is downgraded to `unresolved_uncertainty`.

---

# 12. EvidenceValidator

The EvidenceValidator enforces I-8. It is deterministic and runs from trusted tooling (I-7).

## 12.1 Execution records

The `AgentRunner` harness MUST record every tool execution performed by an agent session:

```yaml
execution_record:
  execution_id:
  session_id:
  head_sha:
  command:
  exit_code:
  stdout_ref:
  stderr_ref:
  output_digest:
  started_at:
  duration:
```

Records are written by the harness, never by the agent.

## 12.2 Checks

For each evidence item and oracle:

| Evidence type | Validation |
|---|---|
| `test` | execution record exists in this verifier session at `head_sha`; the test id appears in that execution's report; the reported outcome matches `claimed_outcome` |
| `command` | execution record exists in this session at `head_sha`; exit code matches `claimed_outcome` |
| `runtime_observation` | execution record exists in this session at `head_sha`; the claimed observation is present in the recorded output |
| `code` | path exists at `head_sha`; the line range is within the file |
| repro oracle | execution record shows failure at `head_sha`; the oracle artifact exists and is self-contained |

## 12.3 Outcomes

- **Valid:** item retained.
- **Unverifiable** (e.g. ambiguous observation match): item dropped and counted. If an AC is left with fewer than `evidence.min_validated_per_ac` items, that AC is marked `insufficient_evidence`.
- **Fabricated** (references a nonexistent execution, wrong SHA, or an outcome contradicting the record): the **entire** verifier output is discarded. Route per §6.2 (`EVIDENCE_FABRICATED`).

Fabrication and unverifiable rates MUST be recorded per model (§24).

---

# 13. Semantic Judgment Layer (JEV)

## 13.1 Role

JEV provides bounded semantic judgments after evidence validation. JEV MUST NOT write code, choose workflow steps, authorize anything, act as a manager, plan, or replace deterministic checks.

## 13.2 Usage model

```text
Is the answer deterministic?
  yes -> normal code/tool
  no  -> Is the answer space bounded?
           yes -> SemanticJudge (JEV)
           no  -> Agent
```

## 13.3 Required judgments (first implementation)

Each is evaluated **per acceptance criterion** where noted, never as one global question.

| Judgment | Granularity | Output |
|---|---|---|
| `acceptance_criterion_satisfied` | per AC | boolean probability |
| `tests_adequate` | per AC | boolean probability |
| `scope_alignment` | per run | choice: `within_scope`, `scope_incomplete`, `scope_excessive`, `unclear` |

Optional judgments, enabled by configuration after evaluation justifies them:

| Judgment | Output |
|---|---|
| `maintainability_risk` | bounded score 1–5 (negligible … unacceptable) |
| `failure_classification` | configurable choice taxonomy (see §13.5) |

## 13.4 Inputs

JEV SHOULD receive factual, assembled state only: a **story slice** for the criterion, relevant diff and code, committed tests, CI and deterministic results, **validated** verifier evidence, and project constraints.

A story slice is built deterministically by the `StorySlicer` from the header and ID-anchored prose:

```text
slice(criterion c) =
    c itself (header + its prose row)
  + every item in c.links, followed one level deep
  + every coverage row whose covers include c, with its fixture
  + glossary entries (GL-n) referenced by any of the above
  + decisions (D-n) referenced by any of the above
  + section 15 Out of scope            (scope_alignment only: full section)
  + section 01/02 summary              (bounded to a configured length)
```

Slicing MUST NOT use a model. A criterion whose slice cannot be built (dangling link) is a contract defect that should have been caught at intake; if encountered, → `ESCALATE` (`STORY_CONTRACT_INVALID`).

For `scope_alignment`, the input additionally includes the list of unmapped changes (§7.4.4) and the codebase map.

It MUST NOT receive DeliveryAgent self-assessment, discarded or unverifiable evidence, or other judgments' outputs, unless a judgment definition explicitly requires it.

## 13.5 Failure classification is advisory

`failure_classification` shapes the repair context and the escalation package. It MUST NOT route the workflow. Routing for infrastructure and pre-existing failures comes only from deterministic classification (§15).

## 13.6 Calibration

Raw JEV probabilities MUST be treated as **uncalibrated scores**.

- Policy thresholds apply to calibrated values: `calibrated = calibration_map(judgment, raw)`.
- Before a calibration map exists, the identity map is used and the scope MUST remain in `SHADOW`.
- Calibration maps are fitted from labelled runs (§24.3), versioned, stored as protected configuration, and recorded on every decision.

## 13.7 `SemanticJudge` abstraction

The SDLC core MUST depend on an abstraction, not on JEV's API:

```java
interface SemanticJudge {
    DecisionResult decide(DecisionDefinition definition, DecisionContext context);
}
```

`JevSemanticJudge` is the first implementation. This permits future comparison with other bounded-decision providers, local classifiers, or deterministic rules once a question becomes machine-verifiable.

`DecisionResult` MUST include: result, raw probabilities, provider, provider/model version, and decision definition version.

---

# 14. Policy Engine

## 14.1 Role

The PolicyEngine owns the decision. It is deterministic, versioned, and pure: the same inputs and policy version MUST produce the same output.

## 14.2 Inputs

```text
deterministic validation results
integrity results and waivers
CI results
validated verifier evidence, findings, uncertainty, oracle status
calibrated semantic judgments
repair count and budgets
project policy configuration
```

## 14.3 Evaluation order

Policy MUST evaluate in this order, stopping at the first rule that decides:

```text
1. Hard gates
   any deterministic check, CI, or oracle failing           -> FAIL
   any unwaived integrity violation                          -> FAIL
   (these should not reach policy; if they do, it is a defect -> ESCALATE)

2. Validated findings
   any validated finding with severity >= block_on_severity -> FAIL

3. Evidence sufficiency
   any gating criterion marked insufficient_evidence         -> per config: FAIL | ESCALATE
   any advisory criterion marked insufficient_evidence       -> per advisory_action

4a. Gating criteria (G), calibrated
   for EACH c in G and EACH required per-criterion judgment:
     value <= auto_fail_threshold                            -> FAIL
     value inside escalation_band                            -> ESCALATE
   Scores across criteria MUST NOT be averaged. The weakest criterion decides.

4b. Advisory criteria (A), calibrated
   for EACH c in A and EACH required per-criterion judgment:
     value < auto_pass_threshold                             -> per advisory_action:
                                                                ESCALATE | NOTE
   An advisory criterion MUST NOT produce FAIL.
   NOTE records the shortfall in the PR description and telemetry and continues.

5. Run-level judgments
   scope_alignment in {scope_incomplete}                     -> FAIL
   scope_alignment in {scope_excessive, unclear}             -> ESCALATE (configurable)

6. Unresolved uncertainty
   count or severity above configured limit                  -> ESCALATE

7. Otherwise, all required judgments for G >= auto_pass_threshold
   and all run-level judgments acceptable                    -> PASS
   else                                                      -> ESCALATE

Follow-up (post_deploy) and MAY criteria are not inputs to any rule.
```

## 14.4 Output

```yaml
policy_result:
  outcome: PASS | FAIL | ESCALATE
  deciding_rule:
  policy_version:
  calibration_version:
  reasons: []
```

## 14.5 Versioning

Policy configuration is protected (§9.1). Every decision records `policy_version`, so historical decisions can be replayed exactly (§24.2).

---

# 15. Failure Classification and Infrastructure Handling

## 15.1 Principle

A failure is routed to `REPAIR` only when the failure is deterministically attributable to the change. Infrastructure problems, flaky checks, and pre-existing failures MUST NOT consume repair budget or trigger code changes.

## 15.2 Infrastructure and flaky classification

Classification MUST be deterministic, using:

- provider status (cancelled, runner lost, timeout, quota, network);
- configured log signatures for known infrastructure errors (`infra.known_signatures`);
- **same-commit re-run:** a failed check is re-run on the unchanged SHA up to `infra.flake_reruns` times. If any re-run passes, the check is classified `FLAKY_CHECK`.

Flaky checks MUST be reported in telemetry and the escalation package. Whether a flaky-then-passing check counts as passing is a configured policy (`infra.flaky_counts_as_pass`). It MUST NOT be decided by an agent.

## 15.3 Pre-existing failures

If a check fails deterministically, the orchestrator MUST check whether the same check fails at the base revision (cached per base SHA). If it does → `ESCALATE` (`PRE_EXISTING_FAILURE`). The agent did not cause it and must not be asked to fix unrelated breakage.

## 15.4 `INFRA_RETRY`

- Uses `infra.max_retries`, separate from the repair budget.
- Applies optional backoff (`infra.backoff`).
- Returns to the originating state with identical inputs.
- Exhausted → `ESCALATE` (`INFRASTRUCTURE_FAILURE`).

## 15.5 Failure categories

```text
STORY_CONTRACT_INVALID     DUPLICATE_RUN              DELIVERY_BLOCKED
NO_CHANGES                 ORACLE_DISPUTED            AGENT_RUNTIME_FAILURE
LOCAL_VALIDATION_FAILED    PRE_EXISTING_FAILURE       FLAKY_CHECK
INTEGRITY_VIOLATION        PROTECTED_PATH_MODIFIED    CI_FAILED
VERIFIER_MODIFIED_BRANCH   EVIDENCE_FABRICATED        EVIDENCE_INVALID
VERIFICATION_FAILED        SEMANTIC_FAILURE           SEMANTIC_UNCERTAINTY
POLICY_ESCALATION          APPROVAL_REQUIRED          MERGE_CONFLICT
HEAD_CHANGED               MERGE_FAILURE              REPAIR_BUDGET_EXHAUSTED
REPAIR_STALLED             RUN_BUDGET_EXHAUSTED       INFRASTRUCTURE_FAILURE
UNHANDLED_TRANSITION       STORY_TOO_LARGE            STORY_STALE
DEPENDENCY_NOT_MERGED      STORY_CHECK_FAILED         COVERAGE_MATRIX_UNMET
```

Keep implementation-specific details attached separately from the category.

---

# 16. Repair Model

## 16.1 No repair agent

Repair uses a **fresh** `DeliveryAgent` session. A dedicated `RepairAgent` MUST NOT be introduced without evaluation evidence.

## 16.2 Repair context

Preserve:

```text
original story + acceptance criteria (current story version)
current repository state and branch
failure category and factual failure details
  - failed deterministic checks with output excerpts
  - integrity violations
  - validated verifier findings
  - repro oracles (executable)
  - semantic judgment outcomes and stated reasons (not probabilities)
  - advisory failure classification
regression notes (§16.5)
human guidance, if any (§17.3)
repair attempt number
```

Discard: conversation history, self-justification, earlier hidden reasoning.

MUST NOT include: thresholds, calibration data, raw JEV probabilities, autonomy configuration.

## 16.3 Re-entry

After repair, the run re-enters at `LOCAL_VALIDATION`. No mandatory gate may be skipped after repair.

## 16.4 Stall detection

Each failure produces a deterministic **failure fingerprint**:

```text
fingerprint = hash(
  failure_category,
  sorted(failing check ids),
  sorted(failing test ids),
  sorted(failing oracle ids),
  sorted(failed AC ids),
  sorted(integrity violation fingerprints),
  sorted(normalized finding ids)
)
```

If the current fingerprint matches any fingerprint within the last `repair.stall_window` cycles → `ESCALATE` (`REPAIR_STALLED`). This covers both "no progress" and oscillation.

Human guidance (§17.3) resets the stall window.

## 16.5 Regression tracking

If an AC judged satisfied in an earlier cycle is not satisfied in a later cycle, the orchestrator records a regression and includes it in the next repair context. Regressions do not route by themselves.

## 16.6 Budgets

- `repair.max_cycles` bounds repair cycles. Exhausted → `ESCALATE`.
- The orchestrator MUST NOT make subjective retry decisions. "One more try feels useful" is not a rule.

---

# 17. Escalation and Resume

## 17.1 Principle

Escalation is a successful outcome when autonomy has reached its configured boundary. It MUST be diagnosable, and the run MUST be resumable.

## 17.2 Escalation package

```yaml
escalation:
  run_id:
  story: { id, version, type }
  escalation_trigger:           # story ET-n ID, if the DeliveryAgent raised one
  stale_paths:                  # if the story was accepted with stale_action = WARN
  unmapped_changes:
  follow_ups:                   # post_deploy criteria
  branch:
  pr:
  head_sha:
  base_sha:
  mode: SHADOW | SUPERVISED | AUTONOMOUS
  effective_risk:
  category:
  reason:
  deterministic_failures:
  integrity_violations:
  verifier_findings:            # validated only
  repro_oracles:
  semantic_judgments:           # omitted in SHADOW blind review
  policy_result:                # omitted in SHADOW blind review
  repair_attempts:
  failure_fingerprints:
  flaky_checks:
  cost_so_far:
  recommended_human_focus:      # derived deterministically from category and failing items
  allowed_resolutions: []
```

Failed autonomous attempts MUST NOT be hidden.

## 17.3 Resolutions

A human resolves an escalation with exactly one structured resolution. Each resolution is recorded with identity, timestamp, and free-text reason, and becomes a label for evaluation (§24.3).

| Resolution | Effect | Constraints |
|---|---|---|
| `APPROVE_MERGE` | → `SYNC_WITH_BASE` | All deterministic checks and CI MUST be green on the head SHA. Human approval MAY override semantic and policy outcomes; it MUST NOT override failing deterministic checks or CI. |
| `REJECT` | records the decision; then the human picks `PROVIDE_GUIDANCE` or `ABANDON` | Used in `SHADOW`/`SUPERVISED` review |
| `WAIVE_AND_CONTINUE` | waives listed violation fingerprints (§9.8) and resumes at the state after the escalating gate | Waivers force human merge approval for this run |
| `PROVIDE_GUIDANCE` | adds guidance to repair context; grants `escalation.guidance_repair_grant` extra cycles; resets stall window; → `REPAIR` | Guidance is input to the agent, not authority |
| `HUMAN_COMMITTED` | human pushed commits → `LOCAL_VALIDATION` | Full loop; human commits are also subject to integrity checks, which the human may waive |
| `STORY_AMENDED` | a new story version from the refinement system is attached → `REPAIR` with the new version | The SDLC MUST NOT edit the story itself |
| `ABANDON` | close PR → `DONE` (`ABANDONED`) | |

## 17.4 Shadow-mode blind review

In `SHADOW`, approval requests MUST hide the policy outcome and semantic judgments until the human has recorded `APPROVE_MERGE` or `REJECT`. The system then reveals them and records agreement or disagreement. This prevents anchoring and keeps calibration labels independent.

## 17.5 Timeout

If no resolution arrives within `escalation.timeout` → `DONE` (`EXPIRED`), with the PR left open and labelled.

---

# 18. Merge Safety

## 18.1 `SYNC_WITH_BASE`

Before merge, the orchestrator MUST determine whether the target branch has advanced since the validated head was produced.

- Base unchanged → `MERGE`.
- Base advanced → update the branch with the configured `merge.sync_strategy` (rebase or merge commit), deterministically.
  - Clean → `LOCAL_VALIDATION` (revalidation).
  - Conflict → `REPAIR` (`MERGE_CONFLICT`). Conflict resolution is delivery work and counts against the repair budget.

Where the platform provides a merge queue, it SHOULD be used (`merge.use_merge_queue`), since it provides the same guarantee with less custom logic.

## 18.2 Revalidation scope

After a clean sync:

- deterministic validation, IntegrityGate, and CI MUST always re-run;
- verification, evidence validation, semantic judgment, and policy re-run according to `merge.reverify_on_base_change`:

```text
always       -> full loop
if_overlap   -> full loop if files changed on base intersect files changed by this run
                (or their configured dependency closure); else skip to SYNC_WITH_BASE
never        -> skip to SYNC_WITH_BASE after CI
```

This value has no default (§0.3).

## 18.3 `MERGE`

- Merge MUST be performed with an expected head SHA (compare-and-swap). If the PR head differs from the validated SHA → `LOCAL_VALIDATION` (`HEAD_CHANGED`).
- Merge MUST respect platform branch protections; the runtime MUST NOT disable or bypass them.
- Merge MUST be idempotent: on resume, the orchestrator first checks whether the PR is already merged at the expected SHA.

Merge requires all of:

```text
deterministic validation passed on head SHA
AND IntegrityGate passed or violations waived on head SHA
AND CI passed on head SHA
AND (policy == PASS AND AutonomyGate permitted)  OR  human APPROVE_MERGE
AND head validated against current base (§18.1)
```

JEV alone, the VerifierAgent alone, and the DeliveryAgent alone MUST NOT cause merge.

## 18.4 Deployment precondition

This specification ends at merge. Many projects deploy the target branch automatically.

```yaml
deployment:
  target_branch_auto_deploys: null        # true | false, required
  safeguards_acknowledged: null           # true | false
```

If `target_branch_auto_deploys` is `true` and `safeguards_acknowledged` is not `true`, the maximum mode for every scope in that repository is `SUPERVISED`.

Acknowledging safeguards means the system owner confirms that independent mechanisms exist downstream (for example progressive rollout, automated rollback, or production monitoring with revert). This runtime does not provide them.

## 18.5 Concurrency

- At most one active run per idempotency key (§7.1).
- At most `workflow.max_concurrent_runs_per_repository` active runs per repository.
- Each run owns its branch exclusively. Concurrent runs that conflict are resolved through `SYNC_WITH_BASE`, never by one run editing another's branch.

---

# 19. Project Specialization

## 19.1 Technology agnosticism

The generic SDLC MUST NOT know intrinsically about any language, framework, platform, or cloud (Java, Spring, Python, Go, Rust, React, Kafka, Kubernetes, Terraform, AWS, Azure, etc.).

Project knowledge comes from the repository and from project-specific plugins.

## 19.2 Specialization sources

```text
AGENTS.md, docs/, skills/
build scripts, repository config, CI definitions, tool configuration
project-specific policies
```

## 19.3 Project extension points

| Extension point | Purpose |
|---|---|
| `DeterministicValidator` | project checks for `LOCAL_VALIDATION` |
| `TestReportParser` | builds `TestInventory` from report formats |
| `TestIdentityResolver` | maps renamed tests deterministically (optional) |
| `TestWeakeningDetector` | language-specific assertion weakening (optional) |
| `SuppressionDetector` | counts suppression markers (optional) |
| `CoverageProvider` | changed-line and overall coverage (optional) |
| `InfraFailureSignatures` | known infrastructure error patterns |
| `RiskClassifier` rules | high-risk paths and size thresholds |

## 19.4 `AGENTS.md`

`AGENTS.md` SHOULD act as constitution, navigation map, and execution constraints. It SHOULD NOT become a knowledge dump.

Recommended content: allowed and forbidden modifications, how to build, how to test, where architecture rules, domain docs, and skills live, the repository definition of done, security and external-system restrictions.

Prefer references (`Architecture rules -> docs/architecture/`) over duplicated content.

`AGENTS.md` is a protected path (§9.1). It describes restrictions; machine controls (§21) enforce them.

---

# 20. Durable Knowledge and Memory Hygiene

## 20.1 Knowledge updates

Agents MAY update non-protected durable knowledge (docs, skills, ADRs, conventions) when implementation changes the truth of the system. These are normal PR changes and are verified like production code.

Changes to protected knowledge (e.g. `AGENTS.md`) require human approval via the waiver path.

## 20.2 Hygiene

Do NOT convert every agent failure into permanent project knowledge.

```text
failure -> telemetry -> repeated/systemic evidence -> durable improvement
```

Prefer executable mechanisms over prose:

```text
lesson -> test | static rule | architecture test | schema | linter | deterministic validator
```

over:

```text
lesson -> more prompt text
```

Use prose only when executable enforcement is impractical.

---

# 21. Security and Permissions

Project-specific restrictions MUST be externalized and machine-enforced wherever possible. Hard security boundaries MUST NOT rely solely on prompt compliance.

The runtime SHOULD support configurable controls per agent role:

```text
filesystem boundaries          network access / egress allowlist
secret access                  allowed / forbidden commands
allowed git operations         package installation
deployment permissions         production access
external API access            branch protections
```

Additional requirements:

- Agents MUST NOT hold credentials that can merge, change branch protections, or modify protected configuration. Those credentials belong to the orchestrator only.
- The VerifierAgent's credentials MUST NOT permit pushing to the delivery branch.
- Secrets MUST NOT appear in prompts, telemetry, or escalation packages.

## 21.1 Story-check allowlist

Commands in story `checks` and `environment.extra` come from outside the repository, so the orchestrator executes them as untrusted input.

```yaml
story_checks:
  allowed_commands: null          # list of exact commands or anchored patterns; MUST be non-empty
  timeout: null
  network: null                   # allowed | denied
```

- A command that does not match the allowlist MUST NOT be executed (intake rejects it; execution re-checks it).
- Commands MUST run with the DeliveryAgent's sandbox restrictions or stricter, never with orchestrator credentials.
- Repositories SHOULD expose named wrapper commands (make targets, scripts) for stories to reference, rather than allowing free-form command lines.

---

# 22. Budgets and Timeouts

All budgets are mandatory configuration (§0.3).

```yaml
budgets:
  repair_max_cycles: null
  verifier_max_attempts: null
  infra_max_retries: null
  run_max_cost: null              # currency or tokens, all model calls in the run
  run_max_wall_clock: null
  state_timeouts:
    DELIVERY: null
    VERIFY: null
    CI_VALIDATION: null
    SEMANTIC_JUDGMENT: null
```

- Exceeding a run-level budget → `ESCALATE` (`RUN_BUDGET_EXHAUSTED`).
- A state timeout of an agent session is an `AGENT_RUNTIME_FAILURE` (→ `INFRA_RETRY`) on first occurrence and counts toward `infra_max_retries`.
- Cost MUST be measured, not estimated by agents.

---

# 23. Persistence and Resume

## 23.1 Persisted state

The system MUST be restartable without relying on agent chat history.

Minimum persisted data:

```text
run ID, idempotency key, story + version
current state, mode, effective risk
base SHA, branch, head SHA, validated SHA
PR identifier
repair count, infra retry count, verifier attempt count
failure fingerprints history
latest deterministic, integrity, and CI results (with SHA)
base test inventory reference
latest validated verifier evidence
repro oracle store reference
latest semantic decisions (raw + calibrated) and versions
latest policy result and version
waivers, human resolutions
cost so far, timestamps
```

## 23.2 Idempotent side effects

Every external side effect (branch creation, PR creation or update, CI trigger, merge, PR close) MUST be idempotent or guarded by reconciliation.

## 23.3 Reconciliation on resume

On resume, before re-executing the current state, the orchestrator MUST reconcile with external reality: branch existence and head SHA, PR state, CI status for the head SHA, and whether the PR is already merged or closed. External reality wins over persisted assumptions.

---

# 24. Observability and Evaluation

## 24.1 Structured events

```yaml
event:
  run_id:
  state:
  action:
  result:
  failure_category:
  duration:
  agent_session_id:
  agent_role:
  model:
  model_version:
  token_usage:
  cost:
  head_sha:
  policy_version:
  calibration_version:
  timestamp:
```

## 24.2 Replay

The system SHOULD support replaying historical runs against different DeliveryAgent and VerifierAgent models, prompts, tools, JEV thresholds, calibration maps, and policy versions.

Policy and calibration replay MUST be exact, since both are deterministic and versioned. Agent replay is statistical and requires repeated trials.

## 24.3 Labels

Labelled runs are the ground truth for calibration and promotion. Label sources:

- human resolutions in `SHADOW` blind review (strongest);
- human resolutions in `SUPERVISED` and escalations;
- escaped-defect attribution (§24.4);
- asynchronous blind review of sampled `FAIL` decisions.

Policy `FAIL` routes straight to repair, so without sampling the system would never learn its false-reject rate. In `SHADOW` and `SUPERVISED`, a configured fraction (`evaluation.fail_review_sample_rate`) of `FAIL` decisions MUST be queued for blind human review. This review is asynchronous and MUST NOT block the repair.

```yaml
label:
  run_id:
  source: shadow_review | supervised_review | escalation | escaped_defect
  human_decision: approve | reject
  reject_reasons: []
  system_outcome: PASS | FAIL | ESCALATE
  agreement: true | false
```

## 24.4 Escaped defects

A merged run is labelled an **escaped defect** (false accept) when, within `evaluation.escape_window`:

- its merge commit is reverted; or
- a defect is linked to its story or merge commit through the configured issue tracker integration.

Escaped defects trigger demotion (§5.5) and MUST appear in reports.

## 24.5 Questions telemetry must answer

```text
Where do stories fail most often, by category and state?
What are the false-accept and false-reject rates per scope (with confidence bounds)?
How often does JEV disagree with human labels? With deterministic evidence?
Which verifier findings correspond to real defects?
What are the evidence fabrication and unverifiable rates per model?
How often do integrity violations occur, and of which kind?
What is the flake rate per check?
How many repair cycles are typical? How often do runs stall?
What does a merged story cost, and where is time spent?
Which project rules create repeated friction?
Which story sections and criterion kinds most often lead to escalation or repair?
How often are stories rejected at intake, stale, or blocked on an escalation trigger?
```

## 24.6 Growth rule

Do NOT assume more agents improve performance. Add roles only after evaluation identifies a repeated failure mode that cannot be solved by better tools, deterministic validation, project knowledge, verifier behavior, semantic judgment, or policy.

## 24.7 Refinement feedback

The pipeline is downstream of refinement, and most story defects are cheaper to fix upstream. The runtime MUST emit a `refinement_feedback` event for every run that ends in, or passes through, any of:

```text
STORY_CONTRACT_INVALID   STORY_TOO_LARGE   STORY_STALE   DEPENDENCY_NOT_MERGED
DELIVERY_BLOCKED (with escalation_trigger)   ORACLE_DISPUTED
SEMANTIC_UNCERTAINTY on a specific criterion   human REJECT with a story-related reason
```

```yaml
refinement_feedback:
  story: { id, version }
  category:
  criterion_ids: []
  section_ids: []          # e.g. ["04", "20"]
  detail:
```

These events are data for the refinement system. The SDLC MUST NOT act on them itself (§1).

---

# 25. Parallelism

The top-level workflow is sequential. The orchestrator MUST NOT use an LLM to decide parallelization, and no intelligent parallelism scheduler is built initially.

Allowed parallelism:

- independent CI jobs;
- independent deterministic checks;
- base-revision inventory and pre-existing-failure checks, run concurrently with delivery;
- internal tool calls chosen by an agent;
- independent runs on different stories, within §18.5 limits.

---

# 26. Anti-Patterns

The implementing agent MUST avoid all of the following.

| # | Anti-pattern | Why it fails |
|---|---|---|
| 26.1 | **Manager LLM** ("What should happen next?") | Transitions belong to deterministic code (I-1) |
| 26.2 | **Reviewer self-repair** (verifier fixes, then approves) | Destroys independence (§10.5) |
| 26.3 | **Self-approval** (DeliveryAgent tests or claims as final evidence) | §8.2 |
| 26.4 | **Giant semantic question** ("Is this PR good?") | Judgments must be decomposed per AC (§13.3) |
| 26.5 | **JEV for deterministic facts** (did build/tests/lint/CI pass, does file exist) | §13.2 |
| 26.6 | **Unbounded loops** | §16.6, §22 |
| 26.7 | **Workflow hidden in prompts** ("implement, then review yourself, then merge…") | Control belongs to runtime code |
| 26.8 | **Org-chart simulation** (roles because humans have those job titles) | Roles follow cognitive independence, not titles |
| 26.9 | **Agents editing their own judges** (tests, thresholds, CI, AGENTS.md) | I-6, §9 |
| 26.10 | **Running gate tooling from the agent's branch** | I-7 |
| 26.11 | **Trusting reported evidence** without execution records | I-8, §12 |
| 26.12 | **Repairing infrastructure failures with code changes** | §15 |
| 26.13 | **Averaging scores across acceptance criteria** | The weakest AC decides (§14.3) |
| 26.14 | **Merging a SHA other than the one validated**, or against a stale base | I-10, §18 |
| 26.15 | **Autonomy without calibration**, or carrying calibration across model/prompt/policy changes | I-9, §5.6 |
| 26.16 | **Leaking thresholds or judge scores to agents** | Invites optimizing against the judge (Appendix A.7) |
| 26.17 | **Treating escalation as terminal** | §17 |
| 26.18 | **Inventing threshold values in code** | §0.3 |

---

# PART II — IMPLEMENTATION GUIDANCE

# 27. Core Domain Model

Keep the implementation small. Suggested entities:

```text
StoryArtifact, StoryHeader, StoryVersion
Criterion (kind, obligation, verified_in), CoverageRow, StoryCheck, StorySlice
Workspace, WorkflowRun, WorkflowState, Mode, RiskClass
DeliveryResult, ValidationResult, CIResult
TestInventory, IntegrityResult, IntegrityViolation, Waiver
ExecutionRecord, VerificationEvidence, VerificationFinding, ReproOracle
EvidenceValidationResult
DecisionDefinition, DecisionResult, CalibrationMap
PolicyResult, AutonomyDecision
FailureContext, FailureFingerprint
EscalationPackage, HumanResolution, Label
```

Avoid generic abstraction layers before they are needed.

---

# 28. Interfaces

Minimal initial boundaries:

```text
AgentRunner            (records ExecutionRecords for every agent tool call)
DeliveryAgent          VerifierAgent
DeterministicValidator IntegrityGate          EvidenceValidator
PullRequestProvider    CIProvider             MergeProvider
SemanticJudge          CalibrationStore
PolicyEngine           AutonomyGate           RiskClassifier
WorkspaceManager       WorkflowStore          ArtifactStore
EscalationChannel      TelemetrySink
StoryParser            StoryContractValidator StorySlicer
StoryCheckRunner       StalenessChecker
```

Conceptual definitions:

```java
interface DeliveryAgent {
    DeliveryResult deliver(DeliveryContext context);
}

interface VerifierAgent {
    VerificationEvidence verify(VerificationContext context);
}

interface DeterministicValidator {
    ValidationResult validate(Workspace workspace);
}

interface IntegrityGate {
    IntegrityResult check(Diff diff, TestInventory base, TestInventory head,
                          Story story, List<Waiver> waivers);
}

interface EvidenceValidator {
    EvidenceValidationResult validate(VerificationEvidence evidence,
                                      List<ExecutionRecord> records,
                                      String headSha);
}

interface SemanticJudge {
    DecisionResult decide(DecisionDefinition definition, DecisionContext context);
}

interface PolicyEngine {
    PolicyResult evaluate(PolicyContext context);
}

interface StoryContractValidator {
    ContractResult validate(StoryArtifact story, RepositoryState base);   // §7.1.2–7.1.6
}

interface StorySlicer {
    StorySlice slice(StoryArtifact story, String criterionId);           // deterministic, §13.4
}

interface StoryCheckRunner {
    List<CheckResult> run(List<StoryCheck> checks, Workspace workspace); // allowlisted, §7.4.2
}

interface AutonomyGate {
    AutonomyDecision evaluate(Scope scope, WorkflowRun run);
}
```

Do not over-generalize these before the first implementation works.

---

# 29. Orchestrator Reference Behavior

The orchestrator SHOULD be implemented as an explicit transition table (§6.2) plus one handler per state. Handlers perform work and return an **event**; only the table maps `(state, event)` to the next state.

```python
def run(run_id):
    run = store.load(run_id)
    reconcile_with_external_reality(run)                      # §23.3

    while run.state not in TERMINAL:
        if kill_switch_active(run.repository):
            run.paused_from = run.state
            transition(run, PAUSED); return

        if run_budget_exceeded(run):                          # §22
            escalate(run, "RUN_BUDGET_EXHAUSTED"); continue

        event = HANDLERS[run.state](run)                      # does work, returns event
        next_state = TRANSITIONS.get((run.state, event.kind))

        if next_state is None:
            escalate(run, "UNHANDLED_TRANSITION"); continue

        if next_state == INFRA_RETRY:
            run.retry_origin = run.state

        if next_state == REPAIR:
            run.failure_context = event.failure_context
            run.fingerprints.append(fingerprint(event))       # §16.4

        transition(run, next_state)                           # persists before continuing


# Selected handlers

def handle_repair(run):
    if run.repair_count >= cfg.budgets.repair_max_cycles:
        return Event("budget_exhausted")
    if stalled(run.fingerprints, cfg.repair.stall_window):
        return Event("stalled")
    run.repair_count += 1
    run.delivery_mode = "repair"
    return Event("retry")                                     # -> DELIVERY

def handle_infra_retry(run):
    if run.infra_retries >= cfg.budgets.infra_max_retries:
        return Event("exhausted")
    run.infra_retries += 1
    backoff(run)
    return Event("retry", target=run.retry_origin)

def handle_policy(run):
    result = policy_engine.evaluate(build_policy_context(run))
    run.policy_result = result
    return Event(result.outcome)                              # PASS | FAIL | ESCALATE

def handle_autonomy_gate(run):
    decision = autonomy_gate.evaluate(scope_of(run), run)
    return Event("permitted" if decision.permitted else "human_required")

def handle_merge(run):
    if pr_already_merged_at(run.pr, run.validated_sha):
        return Event("merged")
    result = merge_provider.merge(run.pr, expected_sha=run.validated_sha)
    return Event(result.kind)                                 # merged | head_changed | rejected | transient

def handle_escalate(run):
    escalation_channel.emit(build_escalation_package(run))    # blind in SHADOW
    return Event("emitted")                                   # -> AWAITING_HUMAN
```

This pseudocode is normative in behavior, not in language.

---

# 30. Required Configuration

Do NOT hardcode these values. `null` means the implementer must expose configuration rather than invent a value. Behavior when unset follows §0.3.

```yaml
workflow:
  target_branch: main
  max_concurrent_runs_per_repository: null

story:
  supported_template_major: 2
  stale_action: null                      # ESCALATE | WARN
  limits:
    gating_criteria:      { soft: null, hard: null }
    codebase_map_files:   { soft: null, hard: null }
  foundation_min_risk: null               # optional minimum risk class for foundation stories

story_checks:
  allowed_commands: null                  # MUST be non-empty
  timeout: null
  network: null

scope:
  always_mapped: []                       # paths never counted as unmapped changes
  unmapped_change_action: null            # none | raise_risk | escalate

agents:
  delivery:  { model: null }
  verifier:  { model: null, require_different_model_family: null }

autonomy:
  default_mode: SHADOW            # fixed safe default
  kill_switch: false
  scopes: []                      # [{ repository, risk_class, mode }]
  promotion_criteria:
    min_labelled_runs: null
    max_false_accept_rate: null
    max_false_reject_rate: null
    confidence_level: null
    min_observation_window_days: null
  demotion:
    on_escaped_defect: null
    on_threshold_breach: null
    on_calibration_invalidation: null

risk:
  high_risk_paths: null
  dependency_manifests: null
  size_thresholds: null           # files / lines per class

integrity:
  protected_paths: null           # MUST be non-empty
  coverage:
    changed_lines_min: null
    max_overall_drop: null
  suppressions:
    max_net_new: null

verification:
  required_judgments:
    - acceptance_criterion_satisfied
    - tests_adequate
    - scope_alignment
  repro_required_severity: null

evidence:
  min_validated_per_ac: null

semantic:
  provider: jev
  auto_pass_threshold: null
  auto_fail_threshold: null
  escalation_band: null
  calibration_ref: null

policy:
  version: null
  block_on_severity: null
  insufficient_evidence_action: null      # FAIL | ESCALATE
  scope_excessive_action: null            # FAIL | ESCALATE
  max_unresolved_uncertainty: null
  advisory_action: null                   # ESCALATE | NOTE

repair:
  stall_window: null

infra:
  flake_reruns: null
  flaky_counts_as_pass: null
  known_signatures: []
  backoff: null

merge:
  sync_strategy: null                     # rebase | merge
  use_merge_queue: null
  reverify_on_base_change: null           # always | if_overlap | never

deployment:
  target_branch_auto_deploys: null
  safeguards_acknowledged: null

budgets:
  repair_max_cycles: null
  verifier_max_attempts: null
  infra_max_retries: null
  run_max_cost: null
  run_max_wall_clock: null
  state_timeouts: {}

escalation:
  guidance_repair_grant: null
  timeout: null

evaluation:
  escape_window: null
  fail_review_sample_rate: null

project:
  agent_instructions: AGENTS.md
```

---

# 31. Implementation Order

Implement incrementally. Each phase MUST pass its proof before the next begins. **The system runs in `SHADOW` from the first real run.** Autonomous merge is a configuration outcome of Phase 10, not a coding milestone.

## Phase 1 — Workflow skeleton

Story artifact parser, contract validation, size, dependency, and staleness checks (§7.1), `WorkflowRun` persistence, transition table, handlers with mock agents, workspace/branch management, reconciliation, kill switch.

Prove: every row of §6.2 is reachable with mocks, and resume after a crash at every state reconciles correctly.

## Phase 2 — DeliveryAgent

Integrate one coding agent through `AgentRunner` with execution recording.

Prove: inspect, modify, run commands, write tests, commit. No verifier yet.

## Phase 3 — Deterministic validation and failure classification

Validators, `TestReportParser`, test inventory, pre-existing failure check, flake re-runs, `INFRA_RETRY`.

Also story checks (§7.4.2), the coverage-matrix check (§7.4.3), and unmapped-change detection (§7.4.4).

Prove: `Delivery -> Validation -> Repair`; infrastructure failures never consume repair budget; a story check whose command is not allowlisted is never executed.

## Phase 4 — IntegrityGate

Protected paths, test integrity, optional coverage/suppression/weakening detectors, waivers. Tooling runs from the trusted base.

Prove with adversarial fixtures: deleted test, disabled test, edited CI file, edited `AGENTS.md`, lowered coverage threshold. Each one is caught.

## Phase 5 — PR, CI, and merge safety

Provider abstractions, head-SHA pinning, `SYNC_WITH_BASE`, compare-and-swap merge. Merge only via human approval at this phase.

Prove: a stale base triggers revalidation; a changed head blocks merge.

## Phase 6 — VerifierAgent and EvidenceValidator

Fresh-context verifier, structured evidence, repro oracles, branch-unchanged check, evidence validation.

Prove with fixtures: fabricated execution IDs are rejected; oracles are enforced in the next validation.

## Phase 7 — SemanticJudge

`SemanticJudge`, `JevSemanticJudge`, `StorySlicer`, the three required judgments per criterion in `G ∪ A`, identity calibration map.

Prove: slices are deterministic (same story and criterion produce byte-identical slices) and contain every linked item.

## Phase 8 — Policy, AutonomyGate, escalation and resume

Ordered policy, risk classifier, autonomy gate (all scopes `SHADOW`), escalation packages, blind review, every resolution in §17.3, stall detection.

Prove: `PASS -> AWAITING_HUMAN (blind)`, `FAIL -> REPAIR`, `ESCALATE -> AWAITING_HUMAN`, and each resolution resumes correctly.

## Phase 9 — Observability, labels, replay, calibration

Telemetry, label capture, escaped-defect attribution, exact policy replay, calibration fitting.

## Phase 10 — Earned autonomy

Operate in `SHADOW` until promotion criteria are met for a scope. Promote low-risk scopes first, by explicit human action. Only after this phase should architecture expansion be considered.

---

# 32. First-Version Definition of Done

The first usable version is complete when it can:

1. accept a valid story artifact; reject invalid, oversized, duplicate, dependency-blocked, or (per configuration) stale stories before any model call;
2. create isolated repository work and capture the base test inventory;
3. launch a DeliveryAgent with recorded executions;
4. let it implement and test autonomously;
5. run project-specific deterministic validation, story DoD checks, and the coverage-matrix check;
6. classify infrastructure, flaky, and pre-existing failures without consuming repair budget;
7. enforce the IntegrityGate from trusted tooling;
8. create/update a PR and obtain CI for the exact head SHA;
9. launch an independent, fresh VerifierAgent on an independently configured model;
10. validate its evidence against execution records and enforce repro oracles;
11. invoke `SemanticJudge` per acceptance criterion;
12. apply ordered, versioned, deterministic policy;
13. repair with fresh DeliveryAgent sessions, with stall detection;
14. escalate with a diagnosable package and resume after any human resolution;
15. run blind `SHADOW` review and record labels;
16. sync with base, revalidate, and merge at the validated SHA only;
17. enforce autonomy scopes, demotion, kill switch, and the deployment precondition;
18. persist and reconcile state to resume after interruption;
19. emit telemetry sufficient to answer §24.5 and replay policy exactly.

---

# 33. Future Extensions — Do Not Build Yet

```text
parallel independent verifiers
specialized security and performance verification
release/deployment stages, production observation, automatic rollback
alternative SemanticJudge adapters (e.g. OpenAI Decisions API)
multi-judge voting
historical risk models (learned risk classification)
project-specific verifier skills
automated knowledge promotion
verifier output caching across repair cycles
```

Do not implement them until evaluation justifies them.

---

# 34. Design Test

Before adding any component, ask in order:

```text
1. Can normal code do this reliably?            yes -> normal code
2. Is this a bounded judgment?                  yes -> SemanticJudge / JEV
3. Does this need open-ended reasoning/creation? yes -> an agent
4. Does it need authority?                      yes -> deterministic policy
5. Could an agent change what judges it?        yes -> protect it (I-6)
6. Can the evidence for it be fabricated?       yes -> validate it (I-8)
7. Does it widen what runs unattended?          yes -> it must be earned (I-9)
```

---

# 35. Final Architecture

```text
                   +----------------------+
                   |  REFINED STORY + ACs |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |   DELIVERY AGENT     |  constructive, autonomous
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   | DETERMINISTIC        |  + failure classification
                   | VALIDATION + ORACLES |    (infra / flaky / pre-existing)
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |   INTEGRITY GATE     |  trusted tooling, protected paths,
                   |                      |  test inventory, ratchets
                   +----------+-----------+
                              |
                              v
                           PR / CI   (exact head SHA)
                              |
                              v
                   +----------------------+
                   |   VERIFIER AGENT     |  independent model, adversarial,
                   |                      |  evidence + repro oracles
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   | EVIDENCE VALIDATOR   |  execution records, fail closed
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   | SEMANTIC JUDGE (JEV) |  per-AC, calibrated
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |   POLICY ENGINE      |  ordered, versioned, deterministic
                   +----------+-----------+
                              |
             +----------------+-----------------+
             |                |                 |
             v                v                 v
          REPAIR       AUTONOMY GATE        ESCALATE
             |          |          |            |
             |      permitted   human           v
             |          |       required   AWAITING_HUMAN
             |          v          |       (blind in SHADOW)
             |    SYNC_WITH_BASE <-+------------+
             |          |                       |
             |          v                       | guidance / commits /
             |        MERGE  (CAS on SHA)       | waiver / amended story
             |          |                       |
             v          v                       |
        fresh       DONE                        |
     DeliveryAgent <----------------------------+
```

---

# 36. Instruction to the Implementing Agent

Implement this system incrementally, in the order of §31.

- Do not reinterpret the architecture into a more complex multi-agent hierarchy.
- Do not add roles preemptively.
- Do not substitute an LLM router for the transition table.
- Do not collapse Delivery and Verification into one context or one credential set.
- Do not let JEV, the verifier, or the delivery agent authorize merge.
- Do not let any agent modify what judges it.
- Do not trust evidence you have not validated.
- Do not infer obligations from story prose. The story header is authoritative; prose is context.
- Do not edit, complete, or reinterpret a story. Report story problems; refinement fixes them.
- Do not hardcode unknown thresholds, budgets, or modes. Fail closed.
- Do not enable autonomous merge in code. It is a configuration outcome earned from labelled data.

When an implementation detail is project-specific, create an extension point instead of guessing a universal answer.

Prefer the smallest implementation that preserves every invariant in this specification.

The first objective is not to build an impressive agent framework.

The first objective is to build a delivery loop that can be **measured, trusted, and improved**, and that becomes autonomous only where it has proven it deserves to be.

---

# APPENDIX A — Rationale (Non-Normative)

**A.1 Why only two agents.** Additional roles add cost, latency, and coordination failure modes without adding independence. The one separation that matters cognitively is between the agent that builds and the agent that tries to break it. Everything else is either a deterministic fact or a bounded judgment.

**A.2 Why the DeliveryAgent writes its own tests.** Tests are part of the build-feedback loop. Splitting test writing into a separate agent slows iteration and doesn't create independence, because the verifier provides that. The cost of this choice is a gaming incentive, which the IntegrityGate addresses.

**A.3 Why fresh sessions for repair.** A continued conversation anchors on the original interpretation and its self-justifications. A fresh session with objective failure context re-reads the problem.

**A.4 Why CI before verification.** Verification is the most expensive step. Running it on code that doesn't build or pass tests wastes model calls.

**A.5 Why agents can't touch protected paths.** A repair session sees a failing check and is instructed to make it pass. Without enforcement, the cheapest path is often to weaken the check. Natural-language instructions do not reliably prevent this; deterministic diff checks do.

**A.6 Why evidence is validated against execution records.** The verifier's output is consumed by JEV, another probabilistic component. Two probabilistic layers in series compound errors, and a fabricated "test passed" would pass straight through. Tying every claim to a harness-recorded execution makes fabrication detectable rather than merely discouraged.

**A.7 Why agents never see thresholds or scores.** An agent that knows what the judge rewards can optimize for the judge instead of the story. Giving agents factual failures, not scores, keeps them working on the defect.

**A.8 Why repro oracles.** The most valuable verifier output is a concrete counterexample. Discarding it forces the repair agent to rediscover the defect, and lets it "fix" something adjacent. An executable oracle makes the next validation prove the fix.

**A.9 Why infrastructure failures are separated.** Flaky tests and broken runners are not code defects. Routing them to repair burns budget and invites agents to change correct code until a flake happens to pass.

**A.10 Why the weakest AC decides.** Averaging hides a failing criterion behind strong ones. A story with one unmet AC is not delivered.

**A.11 Why `SHADOW` with blind review.** Thresholds without data are guesses, and JEV probabilities are not calibrated by default. Blind review produces labels that are not anchored on the system's opinion, so they can be used to calibrate it. Autonomy is then a measured property of each scope, not a belief.

**A.12 Why calibration resets on model or prompt changes.** Measured error rates describe one configuration. A new model can be better on average and worse on exactly the cases that matter.

**A.13 Why compare-and-swap merge and base sync.** CI on a branch proves the branch, not the result of merging it into a target branch that has moved. Validating one SHA and merging another silently removes every guarantee upstream.

**A.14 Why escalation is resumable.** Many escalations need one human answer, not a restart. Resumption preserves the work, the evidence, and the budget accounting, and the human's resolution becomes training signal.

**A.15 Why the deployment precondition.** If merge equals production deployment, the absence of rollback in this runtime becomes a production risk. The precondition makes that dependency explicit instead of implicit.

**A.16 Why a machine-readable story header.** The orchestrator must make routing decisions without a model (I-1). It can only do that from structured data. Prose stays because agents need context, but obligations live in one parseable place, so the pipeline never has to guess what is required.

**A.17 Why obligation levels split gating and advisory criteria.** Treating every requirement as mandatory makes a missed SHOULD block merge; treating them uniformly in an average lets a missed MUST pass. Separating the sets keeps the weakest-criterion rule meaningful.

**A.18 Why post-deploy criteria are excluded from merge.** A requirement that cannot be measured in the pipeline can never have pipeline evidence. Including it would make every run escalate. Recording it as a visible follow-up keeps it honest without blocking delivery.

**A.19 Why staleness and dependency checks run first.** A story refined against code that has since changed describes a codebase that no longer exists. Detecting this deterministically at intake costs nothing; discovering it after delivery and verification costs the most expensive steps in the pipeline.

**A.20 Why story checks are allowlisted.** The DoD is the most direct statement of "done" and makes an excellent gate. But commands written in a story are executed by the runtime; without an allowlist the story format becomes a command-execution channel.

---

# APPENDIX B — Changes from v1 (Non-Normative)

| Area | v1 | v2 |
|---|---|---|
| Path to trust | Thresholds `null`, no bootstrap | Autonomy modes, blind `SHADOW` review, labelled runs, calibration, scoped promotion and demotion, kill switch (§5) |
| Test/rule tampering | `AGENTS.md` guidance only | IntegrityGate: protected paths, test inventory diff, coverage and suppression ratchets, weakening detectors, waivers; trusted tooling (I-6, I-7, §9) |
| Evidence trust | Verifier output consumed directly | Execution records, EvidenceValidator, fail-closed on fabrication (I-8, §12) |
| Verifier findings | Ephemeral artifacts discarded | Repro oracles enforced in later validation; agent disputes go to humans (§11.4) |
| Delivery outcomes | `DELIVERY → LOCAL_VALIDATION` unconditional | `blocked`, no-change, disputed oracle, and runtime failure routed (§6.2) |
| Infrastructure | Category defined, not routed | Deterministic infra/flaky/pre-existing classification, `INFRA_RETRY` with separate budget (§15) |
| Repair loops | `max_cycles` only | Failure fingerprints, stall/oscillation detection, regression tracking (§16) |
| Merge | Merge when policy passes | Base sync, revalidation scope, merge queue, SHA compare-and-swap, concurrency limits (I-10, §18) |
| Deployment | Out of scope, unstated | Explicit precondition capping autonomy (§18.4) |
| Escalation | Terminal | `AWAITING_HUMAN` with structured, resumable resolutions (§17) |
| Model diversity | Mentioned in eval hooks | Independent verifier model configuration, recorded and evaluated (§10.2) |
| Policy | Thresholds only | Ordered evaluation, per-AC minimum (no averaging), versioned, exactly replayable (§14) |
| Budgets | Repair only | Cost, wall clock, per-state timeouts, verifier and infra budgets (§22) |
| Resume | State persisted | Idempotent side effects and reconciliation with external reality (§23) |
| Terminology | `UNCERTAIN` vs `ESCALATE`; policy-only escalation contradicted | Single outcome vocabulary; authority rules stated precisely (I-3) |
| Document | Rules restated across sections | Normative Part I, guidance Part II, rationale appendix; one rule, one place |

---

# APPENDIX C — Changes from v2 (Non-Normative)

| Area | v2 | v2.1 |
|---|---|---|
| Story input | Minimal `acceptance_criteria` list | Story artifact (User Story Template v2): authoritative machine-readable header + ID-anchored prose (§7.1.1) |
| Criteria | All ACs mandatory | `obligation` and `verified_in`; gating, advisory, follow-up, and not-judged sets (§0.4) |
| Intake | Structure check only | Contract validation rules, size limits, dependency check, staleness check against `refined_against_sha` (§7.1) |
| Definition of done | Not represented | Story DoD checks run as allowlisted deterministic gates (§7.4.2, §21.1) |
| Coverage matrix | Not represented | Deterministic check that prescribed tests exist and pass (§7.4.3) |
| Scope | Judged semantically | Unmapped changes computed against the codebase map; feed risk, scope judgment, and configurable action (§7.4.4) |
| Protected paths | Repository-level only | Plus story `prohibited_paths` per run (§9.1) |
| Escalation triggers | Generic `blocked` | DeliveryAgent reports story trigger IDs, including `ET-0` for unresolvable section conflicts (§8.6) |
| Semantic judgment input | "The story" | Deterministic per-criterion story slices (§13.4) |
| Policy | One per-AC rule | Gating criteria can FAIL; advisory criteria can only ESCALATE or NOTE (§14.3) |
| Follow-ups | — | Post-deploy criteria listed in the PR and escalation package, excluded from merge (§7.6) |
| Feedback loop | — | `refinement_feedback` events to improve upstream refinement (§24.7) |

