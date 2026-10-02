# Session prompt — build the opencode Story Refiner (agent + skill)

> Paste everything below the line into a new opencode session started at the repository root
> (`/Users/williamsuane/IdeaProjects/devdojo-way`).

---

## Your task

Build an opencode **primary agent** and a **skill** that refine this repository's product-level user stories into story artifacts that conform to **User Story Template v2**. Those artifacts are the input contract of the autonomous SDLC pipeline.

You are building the refiner. You are **not** refining any story in this session.

Deliverables:

1. `.opencode/agents/story-refiner.md`: the agent (persona, permissions, how it uses the skill).
2. `.opencode/skills/refine-story/SKILL.md`: the procedure, rules, and checklists. Add supporting files inside the skill folder only if the procedure needs them.

Opencode here is **v2.0.21**. Before you write either file, check the current opencode documentation for the agent frontmatter (`description`, `mode`, `permission`, …) and the skill format/location (`name`, `description` frontmatter; `.opencode/skills/<name>/SKILL.md`). Don't rely on memory. If the docs disagree with the paths above, stop and tell me.

Do not commit anything in this session. I will review the files first.

## Read these first (all of them, fully)

| File | Role |
|---|---|
| `docs/plans/user-story-template-v2.md` | **The output contract.** Every refined story has exactly this shape. |
| `docs/plans/autonomous-agent-owned-sdlc-v2.1.md` | The consumer of the output. The sections that matter most for the refiner are §0.4, §1, §5.3, §7.1 (especially §7.1.2 contract validation, §7.1.4 size, §7.1.5 dependencies, §7.1.6 staleness), §7.4.2–7.4.4, §9.1–9.2, §11.3, §13.4 (StorySlicer), §21.1, §24.7. |
| `docs/stories/active/2026-10-02/README.md` | Index of the 25 product stories and the recommended refinement order. |
| `docs/stories/active/2026-10-02/PRODUCT-CONTEXT.md` | Confirmed product decisions, assumptions, open questions, guardrails. |
| `docs/stories/active/2026-10-02/*.md` | The 25 product stories (input). Read at least 3 to understand their shape. |
| `docs/plans/idea.md` | Original source idea. **Read-only, always.** |
| `pom.xml`, `src/**` | Current codebase: Spring Boot 4.1.1, Java 25, Maven wrapper, JPA, Flyway, MySQL, Security, springdoc, Testcontainers. It is essentially an empty skeleton, base package `academy.devdojo`. There is no `AGENTS.md`. |

## Decisions already made (do not reopen, do not reinterpret)

The agent and skill you write must encode all of these.

**D1 — Artifacts.** Primary agent + skill. The agent owns persona and permissions. The skill owns the procedure, so other agents can reuse it later.

**D2 — Permissions.** The agent may write **only** under `docs/stories/`. It must never edit `src/**`, `pom.xml`, build files, `docs/plans/**`, or `.opencode/**`. Express this through opencode `permission` settings wherever the opencode version supports path-scoped rules, not just through prompt text. If path-scoping isn't supported, say so in your final report. Bash is limited to read-only inspection (`git status`, `git log`, `git rev-parse`, `git show`, `git ls-files`, `ls`, `cat`, `grep`, `find`) plus `git add` / `git commit` (see D11). No build/test execution, no network, no `git push`.

**D3 — One story per session, interactive.** The user starts the agent with one story ID. The agent works only on that story. It asks focused questions in small batches (no more than about 5 per batch, each with a short reason and, where useful, options), waits for answers, and never fills a gap by inference. Every question and answer goes into section `25 Refinement log` with its source.

**D4 — Two phases with approval gates.**
- **Phase A — Product refinement.** Inputs: the product story, PRODUCT-CONTEXT, the product stories it depends on, `idea.md`, TECH-CONTEXT. Produces sections 01, 02, 03, 04, 05, 10 (behavioral triggers/responses), 12 (who may do what), 15, 19, 23, plus the matching `criteria` entries. Ends with the full Phase A content shown to the user and an explicit approval.
- **Phase B — Technical refinement.** The agent reads the repository and **proposes** sections 06, 07, 08, 09, 10 (detection/codes/logging/retry), 11, 13, 14, 16, 17, 18, 20, 21, 22, 24 and the header `scope`, `coverage`, `checks`, `environment`, `story.type`, `story.risk`, `refined_against_sha`. Each proposal group is shown to the user and written only after approval. NFR numbers, security obligations, observability names, configuration defaults and similar values come from the user. The agent may suggest values but must label them as suggestions until confirmed.
- The user's invocation of this agent counts as the explicit request for technical design and detailed acceptance criteria that PRODUCT-CONTEXT and the README otherwise forbid. **All other PRODUCT-CONTEXT guardrails still apply:** do not expand scope, keep stable IDs and outcomes, do not turn assumptions or open questions into rules, flag cross-story effects.

**D5 — Just-in-time technical refinement.** Phase B is allowed **only if every `depends_on` story has been merged into `main`**. The agent checks this by (a) confirming that the dependency's refined file exists in `docs/stories/refined/`, (b) checking that the dependency's `codebase_map.create` paths exist at `main` HEAD, and (c) asking the user to confirm the merge. If any check fails, Phase A output is saved as a draft (D7) and the session ends with a clear statement of what is blocking.

**D6 — Unresolved questions block emission.** A refined story must contain no open questions, no "TBD", no unconfirmed assumptions. If a consequential question can't be answered in the session (especially the "before launch" questions in PRODUCT-CONTEXT), the agent does **not** write the v2 story. It saves a draft listing the blocking questions and stops. The PRODUCT-CONTEXT "Assumptions awaiting confirmation" may be used only after the user confirms them in-session. Once confirmed, they become BR-n or D-n with the user as the source.

**D7 — Output locations.**
- Refined, contract-ready stories: `docs/stories/refined/<ID>.md`
- Drafts (Phase A only, or blocked): `docs/stories/refined/drafts/<ID>.md`, with a "Blocking" list at the top.
- Shared technical decisions: `docs/stories/refined/TECH-CONTEXT.md` (D9).
- The product stories in `docs/stories/active/2026-10-02/` stay as input. Edit them only under D10.

**D8 — IDs.**
- `story.id` keeps the product ID (e.g. `REVIEW-01`).
- If a story must be split, the parts become `REVIEW-01.1`, `REVIEW-01.2`, …. Each one names its parent in section 01 and declares `depends_on` between parts where delivery order matters.
- New foundation work uses the `PLATFORM-` prefix. The first is **`PLATFORM-01`** (D12).
- Item IDs (`FR-n`, `BR-n`, `E-n`, `GL-n`, `D-n`, `FX-n`, `CM-n`, `ET-n`, `IG-n`, `OOS-n`, `PR-n`, …) must be unique across the whole artifact, as §7.1.2 rule 2 requires.

**D9 — TECH-CONTEXT.** Cross-cutting technical decisions (for example: API-only vs UI, authentication mechanism, package layout, test naming / `test_id` convention, error-response format, migration conventions, wrapper command names) are kept in `docs/stories/refined/TECH-CONTEXT.md` as ID'd entries (`TD-n`: decision, rationale, rejected alternatives, date, approved-by). An entry is added only after user approval. Each story copies the relevant TD entries into its own section `06 Decisions` as `D-n` (citing `TD-n` as the source), so the story stays self-contained. TECH-CONTEXT does not exist yet. The first session that needs a cross-cutting decision creates it.

**D10 — Shared product edits.** If a decision changes PRODUCT-CONTEXT or another product story, the agent lists every affected file and story ID, shows the exact proposed diff, and edits **only after explicit approval**. `docs/plans/idea.md` is never edited.

**D11 — Git.** The agent commits after the user approves the final artifact. It proposes the file list and commit message and waits for approval before committing. It commits on the current branch and never pushes. `refined_against_sha` is the full SHA of `HEAD` taken at the start of Phase B, recorded before any refinement commit. If the working tree has uncommitted changes outside `docs/stories/` at that moment, the agent stops and asks.

**D12 — PLATFORM-01 (foundation).** The repository lacks the prerequisites the pipeline needs: no `AGENTS.md`, no named wrapper commands for story checks, no recorded conventions. These are delivered by a `type: foundation` story `PLATFORM-01`. It has no product-story source. The user and the agent define its content in-session. Every other story's `depends_on` includes `PLATFORM-01` unless the user says otherwise. When a session starts for any other story and `PLATFORM-01` is not yet refined or merged, the agent says so up front and lets the user decide how to proceed. Constraints the skill must state for PLATFORM-01:
- Its own `checks` may use only commands that already exist at its `refined_against_sha` (e.g. the Maven wrapper). The user must confirm each one as allowlist-eligible.
- `AGENTS.md` is a protected path in the pipeline (§9.1). Delivering it will escalate (`PROTECTED_PATH_MODIFIED`) and needs a human waiver. Record this in its sections 19/23.
- The pipeline's story-check allowlist is runtime configuration (§21.1), not a repository file. PLATFORM-01 can create the wrapper commands, and the allowlist entries are recorded as a follow-up for the human who configures the runtime.

**D13 — Size guard: ask per story.** There are no fixed limits. Before finishing Phase B, the agent reports the count of gating criteria (MUST/MUST_NOT + `verified_in: pipeline`) and `|codebase_map.create ∪ codebase_map.modify|`, says whether it thinks the story is too large, and asks the user whether to split (D8 naming).

## Rules the skill must encode beyond the decisions above

1. **Header is authoritative; prose elaborates.** Every FR, BR, E, NFR, SEC, OBS, CFG and MUST-level IG item that must be checked appears in `criteria` exactly once. Prose refers to items by ID and adds no obligations that are missing from the header.
2. **Contract self-check before writing** (spec §7.1.2). The agent verifies and reports pass/fail for each rule: required header fields; full 40-char SHA that exists (`git cat-file -e`); unique IDs; every `links`/`covers`/`fixture` reference resolves; every criterion ID appears in the prose; every gating criterion is covered by ≥1 coverage row; every `checks[].command` and `environment.extra[].command` is user-confirmed as allowlist-eligible; sections 01–25 all present and non-empty (`N/A — <reason>` is valid); `prohibited_paths` ∩ (`create` ∪ `modify`) = ∅; each `permitted_test_removals` entry has a reason. It also checks staleness preconditions (§7.1.6): no `codebase_map.create` path already exists at `refined_against_sha`. Any failure means the story is not written as refined.
3. **Slice completeness** (spec §13.4). For each criterion, its `links` must be complete enough that the deterministic slice (criterion + linked items + coverage rows + fixtures + GL + D) lets a judge evaluate it without the rest of the story. The agent checks this explicitly for every criterion.
4. **Product dependencies ≠ delivery dependencies.** The "Dependencies" list in a product story describes related behavior. The agent asks which of them are true `depends_on` (must be merged first, with `min_version`) and records the rest as context only.
5. **Precedence and ET-0.** Keep the template's precedence rule and `ET-0`. Escalation triggers must be concrete situations the DeliveryAgent can recognize, not "if unsure".
6. **`verified_in`.** Anything that can't be measured in CI/local harness is `post_deploy` and does not gate. The agent asks the user rather than guessing.
7. **No invention.** No numbers, names, defaults, codes, or policies that the user, PRODUCT-CONTEXT, `idea.md`, TECH-CONTEXT, or the repository did not provide. Every row in section 25 cites its source.
8. **Conflicts.** If the product story, PRODUCT-CONTEXT, `idea.md`, a dependency story, or TECH-CONTEXT conflict, the agent surfaces the conflict and asks. It never picks silently.
9. **End-of-session report.** The agent ends with: the file(s) written (or the draft plus blocking list), contract self-check results, gating/advisory/follow-up criteria counts, cross-story effects found, and proposed edits to other files (applied or not).

## What I want from you in this session

1. Read every input listed above.
2. **Ask me** about anything ambiguous before writing (opencode capabilities, conflicts between these decisions and the spec/template, anything missing). Do not infer.
3. Propose, and **do not build without my approval**, whether the skill should include a small deterministic validator script for the mechanical contract rules (unique IDs, reference resolution, coverage of gating criteria, section presence, path overlap). If I approve, ask me which language/runtime to use.
4. Write the two files.
5. Report back:
   - file paths and a summary of each;
   - how each decision D1–D13 is encoded (one line each);
   - permission limitations you couldn't enforce mechanically;
   - how to invoke it (e.g. switching to the agent and passing `REVIEW-01`).
