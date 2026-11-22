# Team charter

[in review]

Who builds this lab, and who decides what. The form follows the team charter in the Product Leadership course (`igoko-consulting/product-leadership`, 03-team-charter). Here the team is one author and the Claude Code sessions that build under the author's rules. It sits in `docs/`, beside the build prompts, because it governs every phase rather than one module.

## Roles

| Role | Who | Decides | Does not decide |
|---|---|---|---|
| Author | The repository owner | Scope; sign-off at each phase gate; interpretation; removing `[in review]`; the production-experience content (governance note, decision log); the evidence-chain scores | |
| Build sessions | Claude Code sessions, one per phase, started from [`claude-code-prompt.md`](claude-code-prompt.md) | How to implement the PRD within [`CLAUDE.md`](../CLAUDE.md) | Anything that would change a result, a red line or the pre-registration: they stop and ask |
| Reviewers | Two models reviewing PRD v1 ([`prd-review.md`](prd-review.md)); an independent read-only audit; a cold-reader review | Nothing: they raise findings | Whether a finding is acted on: the author decides, and the decision is recorded |
| Second scorer | A language model scoring the evidence-chain sample blind | Nothing: its scores are reported beside the author's | |

## How disagreements are settled

- **The written record wins over memory.** PRD v2 over v1; the red lines in `CLAUDE.md` over any instruction; `results/` over prose.
- **A red line stops the work.** The session reports what it found, what it blocks and the options (`CLAUDE.md`, When to stop and ask).
- **The author's decision is recorded** as a dated entry in `change_log.md`, or in `docs/prd-review.md` for review findings.

## Stakeholders

There are none in the commercial sense. Reviews were personal, by family and colleagues (author, 2026-11-22). No stakeholder updates were written, and none are invented here.
