---
# ============================================================================
# 00 METADATA — MACHINE-READABLE HEADER
# The orchestrator reads ONLY this header. Agents read header + prose.
# The header is authoritative for IDs, obligations, paths, and checks.
# Prose sections elaborate items by ID and MUST NOT introduce new
# obligations that are absent from this header.
# ============================================================================

template_version: 2.0

story:
  id: STORY-0000
  version: 1                         # increment on every re-refinement
  type: change                       # foundation | change
  title: ""
  repository: ""                     # e.g. org/repo
  target_branch: main
  refined_against_sha: ""            # full SHA of the base the story was refined against
  risk: null                         # optional: low | medium | high (engine uses max(declared, computed))
  depends_on: []                     # [{ story_id: STORY-0001, min_version: 1 }]

# ----------------------------------------------------------------------------
# CRITERIA — the set the pipeline verifies, judges, and gates on.
# Every FR, BR, E, NFR, SEC, OBS, CFG, and MUST-level IG item that the
# pipeline must check appears here exactly once.
#
# kind:        functional | business_rule | error | nfr | security |
#              observability | configuration | constraint
# obligation:  MUST | MUST_NOT | SHOULD | SHOULD_NOT | MAY
#              MUST / MUST_NOT       -> gating (failure blocks merge)
#              SHOULD / SHOULD_NOT   -> advisory (shortfall escalates or is noted, per policy)
#              MAY                   -> not judged
# verified_in: pipeline | post_deploy
#              post_deploy criteria are excluded from merge decisions and
#              recorded as follow-ups.
# links:       related IDs (BR, E, D, CM, FX, GL) used to build each
#              criterion's context slice. Keep links complete and minimal.
# ----------------------------------------------------------------------------
criteria:
  - id: FR-1
    kind: functional
    obligation: MUST
    verified_in: pipeline
    text: ""
    links: [BR-1, E-1, CM-1, FX-1]

# ----------------------------------------------------------------------------
# SCOPE
# ----------------------------------------------------------------------------
scope:
  codebase_map:                      # section 17 in machine form; globs allowed
    create: []                       # files the story expects to be created
    modify: []                       # files the story expects to be modified
    reference: []                    # read-only reference implementations
  prohibited_paths: []               # section 18, enforced by the IntegrityGate (escalates)
  permitted_test_removals: []        # [{ test_id_pattern: "", reason: "" }]

# ----------------------------------------------------------------------------
# COVERAGE MATRIX — section 20 in machine form.
# test_id: exact id or glob as it appears in test reports, e.g.
#          "com.example.OrderMapperTest#rejectsNegativeQuantity".
#          When set, the pipeline checks deterministically that a matching
#          test exists and passes. Leave empty only when the name cannot be
#          prescribed; then adequacy is judged semantically only.
# ----------------------------------------------------------------------------
coverage:
  - id: CM-1
    covers: [FR-1]
    scenario: ""
    level: unit                      # unit | component | integration | contract | e2e
    fixture: FX-1
    test_id: ""

# ----------------------------------------------------------------------------
# DEFINITION OF DONE — section 24 in machine form.
# Commands MUST match the repository's story-check allowlist; anything else
# makes the story contract invalid. Prefer named repository commands
# (e.g. make targets, wrapper scripts) over raw command lines.
# expect: any combination of
#   exit_code, stdout_contains, stdout_not_contains, file_exists
# ----------------------------------------------------------------------------
checks:
  - id: DOD-1
    command: ""
    expect:
      exit_code: 0

# ----------------------------------------------------------------------------
# ENVIRONMENT — section 22. Build/test/run commands come from the repository
# (AGENTS.md, CI). List ONLY story-specific additions here.
# ----------------------------------------------------------------------------
environment:
  commands_ref: AGENTS.md
  extra: []                          # [{ purpose: "", command: "" }] allowlisted only
---

# STORY-0000 — <Title>

> **How to use this template**
>
> - Every section heading stays. If a section does not apply, write `N/A — <one-line reason>`. An empty section is treated as missing information; `N/A` is treated as a deliberate decision.
> - Give every item an ID (`FR-1`, `BR-1`, `E-1`, `GL-1`, `D-1`, `FX-1`, `ET-1`, …). Prose refers to items by ID only, so the pipeline can slice context per criterion.
> - Any item the pipeline must check is listed in the header `criteria`. If it is in the prose but not in the header, it is guidance, not an obligation.
> - **Precedence when sections conflict:** `18 Prohibited` > `04/05/10 FR/BR/E` > `11–14 NFR/SEC/OBS/CFG` > `06 Decisions` > `16 Implementation guidance` > `17 Codebase map`. A conflict the agent cannot resolve with this order is an escalation trigger (`ET-0`).
> - **Size guard:** if this story exceeds the repository's limits on MUST criteria or codebase-map files, split it during refinement. Oversized stories are rejected at intake.

---

## 01 Context

Why this exists, the business background, and who or what consumes the result (users, services, teams, downstream systems).

## 02 Problem statement

One paragraph. What is wrong or missing today, observably, and for whom.

## 03 Glossary

| ID | Domain term | Precise meaning | Name in code |
|---|---|---|---|
| GL-1 | | | |

## 04 Functional requirements

Each FR has one obligation keyword and appears in the header `criteria`.

| ID | Obligation | Requirement |
|---|---|---|
| FR-1 | MUST | |

## 05 Business rules

| ID | Condition | Outcome | Source |
|---|---|---|---|
| BR-1 | | | |

## 06 Decisions

| ID | Decision | Rationale | Rejected alternatives |
|---|---|---|---|
| D-1 | | | |

Decisions are settled. Agents MUST NOT reopen them; a decision that proves unworkable is an escalation trigger.

## 07 Data specification

Input and output schemas, field constraints (type, nullability, ranges, formats), and concrete example payloads. Reference payloads as fixtures (`FX-n`) defined in section 21.

## 08 Contracts

| ID | Contract | Type (API / event / external system) | Version | Direction | How to stub |
|---|---|---|---|---|---|
| CT-1 | | | | | |

## 09 State & side effects

What is persisted or emitted, transaction boundaries, idempotency keys, and ordering guarantees.

## 10 Error handling

| ID | Trigger | Detection | Response / code | Logging | Retry / rollback |
|---|---|---|---|---|---|
| E-1 | | | | | |

## 11 Non-functional requirements

Every NFR has a number and a measurement method. Mark where it can be verified: `pipeline` (measurable in CI or the local harness) or `post_deploy` (needs production-like load or data). Post-deploy NFRs do not block merge.

| ID | Obligation | Requirement (with number) | Measured by | Verified in |
|---|---|---|---|---|
| NFR-1 | MUST | | | pipeline |

## 12 Security

Authentication, authorization, PII handling, secrets. Checkable items get `SEC-n` IDs and appear in the header.

| ID | Obligation | Requirement |
|---|---|---|
| SEC-1 | MUST | |

## 13 Observability

Required logs, metrics, and traces. Checkable items get `OBS-n` IDs and appear in the header.

| ID | Obligation | Signal | Name / format | When emitted |
|---|---|---|---|---|
| OBS-1 | MUST | | | |

## 14 Configuration

| ID | Obligation | Property / flag | Type | Default per environment |
|---|---|---|---|---|
| CFG-1 | MUST | | | |

## 15 Out of scope

Explicit list of what this story does NOT do. The verifier and the scope judgment use this list directly.

- OOS-1:

## 16 Implementation guidance

**MUST (constraints)** — become `kind: constraint` criteria in the header.

| ID | Constraint |
|---|---|
| IG-1 | |

**SHOULD (suggestions)** — guidance only; not verified.

- IGS-1:

## 17 Codebase map

Human-readable explanation of the header `scope.codebase_map`: why each file is created or modified, and which reference implementation to copy for which purpose.

| Path | Action (create / modify / reference) | Purpose |
|---|---|---|
| | | |

Changes outside this map are allowed, but they are reported and, depending on repository configuration, raise the run's risk class or stop it for review.

## 18 Prohibited

**Enforced (paths)** — listed in header `scope.prohibited_paths`. Touching them stops the run for human review.

- `path/or/glob/**`

**Guidance (non-path)** — things not to add or change that cannot be expressed as paths (e.g. "do not introduce a new dependency on X"). Prefer turning these into repository rules over time.

- PR-1:

## 19 Compatibility

`change` stories only (`N/A` for `foundation`): backward compatibility, data or schema migrations, and rollout notes. Rollout happens after merge and is outside the pipeline; describe it here for the humans who own deployment.

Any intentional removal of existing behavior MUST be paired with a `permitted_test_removals` entry in the header.

## 20 Coverage matrix

Human-readable view of header `coverage`. Every pipeline-verified MUST/MUST_NOT criterion is covered by at least one row.

| ID | Covers | Scenario | Level | Fixture | Test ID |
|---|---|---|---|---|---|
| CM-1 | FR-1 | | unit | FX-1 | |

## 21 Fixtures & test data

| ID | Description | Location or inline payload |
|---|---|---|
| FX-1 | | |

## 22 Environment

Build, test, and run commands come from the repository (`AGENTS.md`, CI). List only story-specific additions (e.g. a test tag or profile) and mirror them in header `environment.extra`.

## 23 Escalation triggers

Situations where the agent must stop and report instead of deciding. The DeliveryAgent reports the triggered ID.

| ID | Trigger |
|---|---|
| ET-0 | Sections conflict in a way the precedence rule does not resolve |
| ET-1 | |

## 24 Definition of done

Human-readable view of header `checks`. Every item is machine-checkable: command → expected result.

| ID | Command | Expected result |
|---|---|---|
| DOD-1 | | exit code 0 |

## 25 Refinement log

| # | Question | Answer | Source | Date |
|---|---|---|---|---|
| 1 | | | | |
