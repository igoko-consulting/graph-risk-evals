# Team charter

[in review]

Who builds this lab, who decides what, and what the author has signed off. The form follows the team charter in the Product Leadership course (`igoko-consulting/product-leadership`, 03-team-charter). Here the team is one author and the Claude Code sessions that build under the author's rules. Written on 2026-11-22 from the record.

**Why it sits in `docs/`.** It governs every phase rather than one module, and it sits beside the build prompts it refers to. `00-build/` holds the pipeline and its running notes, so a charter there would read as part of the code.

## 1. What we own

- **We own:** the experiment as the PRD specifies it, its code, its results and the write-up, on one public dataset (`prds/prd-v2.md`).
- **Out of scope:** a detection product, any claim about payments data, and anything in the PRD's non-goals. Phase 5 items are deferred, not owned yet.
- **Joint calls:** none. There is one decision-maker. Reviewers raise findings; the author decides what is acted on.

## 2. Roles

| Role | Who | Decides | Does not decide |
|---|---|---|---|
| Author | The repository owner | Scope; sign-off at each phase gate; interpretation; removing `[in review]`; the production-experience content (governance note, decision log); the evidence-chain scores | |
| Build sessions | Claude Code sessions working under [`CLAUDE.md`](../CLAUDE.md). Session 0 set up the repository from [`claude-code-prompt-session0.md`](claude-code-prompt-session0.md); session 1 built the thin slice from [`claude-code-prompt.md`](claude-code-prompt.md). No prompt is committed for later phases | How to implement the PRD within the red lines | Anything that would change a result, a red line or the pre-registration: they stop and ask |
| Reviewers | Two models reviewing PRD v1 ([`prd-review.md`](prd-review.md)); an independent read-only audit; a cold-reader review; personal reviewers, family and colleagues (owner input, 2026-11-22) | Nothing: they raise findings | Whether a finding is acted on |
| Second scorer | A language model scoring the evidence-chain sample blind | Nothing: its scores are reported beside the author's | |

## 3. How we decide

- **The written record wins over memory.** PRD v2 over v1; the red lines in `CLAUDE.md` over any instruction; `results/` over prose.
- **A red line stops the work.** The session reports what it found, what it blocks and the options (`CLAUDE.md`, When to stop and ask).
- **The author's decision is recorded** as a dated entry in `change_log.md`, or in `docs/prd-review.md` for review findings.

## 4. Sign-offs on record

Decisions the record attributes to the author. Each was made before the result it could affect, unless the entry says otherwise.

| Date | Decision | Record |
|---|---|---|
| 2026-11-19 | Arm A uses the local features left once the time step is excluded; confirmed before the data was loaded | `change_log.md`, session 1 |
| 2026-11-19 | scikit-learn's histogram gradient boosting chosen, before any arm was built | `change_log.md`, session 1 |
| 2026-11-19 | The tuning protocol applies to every arm, A, B and D | `change_log.md`, session 1, errata |
| 2026-11-19 | The integer rule for k, chosen after the mean was known and before any arm was built | `change_log.md`, session 1 |
| 2026-11-19 | The tuning contract, metrics and kill-criterion metric, agreed before any model was trained | `change_log.md`, protocol entry |
| 2026-11-20 | No bootstrap bands on the queue-size chart; both periods shown | `change_log.md`, queue-size chart and the write-up |
| 2026-11-20 | README restructured for a cold reader (PRD v2.5, requirement 21) | `change_log.md`, queue-size chart and the write-up |
| 2026-11-20 | Gate 2 tightened to the PRD's rule | `change_log.md`, Gate 2 entry |
| 2026-11-22 | Objective, project kill criterion, readers in order and reviewers, for the course-structure pages | `change_log.md`, course-structure entry |

**Not yet signed off:** the Phase 4 gate ([ship-hold-memo](../05-evals-and-guardrails/ship-hold-memo.md)); every item marked `[in review]`; the evidence-chain scores; and two questions the audit left open, whether PRD v2.5 moves to its own file and the tone flagged in the PRD.

## 5. Stakeholders and updates

There are no stakeholders in the commercial sense: no sponsor, no budget holder, no team. Reviews were personal, by family and colleagues, named here by role (owner input, 2026-11-22). No stakeholder updates were written, so the course's stakeholder message has no counterpart here, and none is invented.
