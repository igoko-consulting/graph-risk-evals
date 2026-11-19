# Claude Code prompt — session 0, repository setup

Run this first, in an empty cloned repository. Download the documents to a local folder before starting, and replace `<SOURCE>` with its path.

---

Set up the repository structure for `graph-risk-evals` and commit it.

The documents already exist at `<SOURCE>`. **Place them verbatim. Do not edit, reformat, summarise or regenerate a single character of any of them.** They are the specification, and one of them is about to be cryptographically hashed, so drift is not a cosmetic problem.

## 1. Create this structure

```
00-build/                 pipeline: loaders, features, arms, evaluation
01-the-bet/               pre-registration, hypotheses, kill criteria
02-the-decision/          the ladder, build-vs-buy, rung selection
03-the-margin/            cost model, assumptions, sensitivity
04-the-data/              dataset notes, labels, leakage tests
05-evals-and-guardrails/  eval stack, red lines, review queue
06-governance/            controls, data protection, sovereignty
07-decision-log/          anonymised production decisions, mapped to rungs
graph/queries/            traversal queries for Arm B features
loaders/                  dataset loaders behind one interface
results/                  JSON output
site/                     static front end
tests/                    leakage and integrity tests
prds/                     versioned PRDs
docs/img/                 diagrams
```

Put a `NOTES.md` in each numbered module directory, with a one-line heading naming what the module is for. Put a `.gitkeep` in the empty directories so they survive the commit.

## 2. Place the documents

| From `<SOURCE>` | To |
|---|---|
| `README.md` | `README.md` |
| `CLAUDE.md` | `CLAUDE.md` |
| `prd-v1.md` | `prds/prd-v1.md` |
| `prd-v2.md` | `prds/prd-v2.md` |
| `prd-review.md` | `docs/prd-review.md` |
| `claude-code-prompt.md` | `docs/claude-code-prompt.md` |
| `pre-registration.md` | `01-the-bet/pre-registration.md` |
| `architecture.png` | `docs/img/architecture.png` |
| `experiment-junctions.png` | `docs/img/experiment-junctions.png` |

## 3. Create `.gitignore`

```
data/
__pycache__/
*.pyc
.venv/
venv/
.env
.DS_Store
*.kuzu
*.db
results/*.tmp
```

## 4. One edit, and only this one

In `01-the-bet/pre-registration.md`, replace `_[fill on commit]_` with today's date in ISO format. Change nothing else in that file.

## 5. Commit in exactly two steps

```
Commit 1: everything except 01-the-bet/pre-registration.md
Message:  Add specification, review disposition, agent rules and diagrams

Commit 2: 01-the-bet/pre-registration.md alone
Message:  Commit pre-registration before any result exists
Tag:      prereg-v1, annotated, message "Pre-registration committed before any result exists"
```

They must stay separate. The tag has to point at a commit that contains the pre-registration and no results, because the git history is the evidence the hypotheses were written before the experiment ran.

**Plain commit messages. No attribution, co-authorship or generated-by lines.**

Push both commits and the tag.

## 6. Verify and report back

- Print the repository tree.
- Confirm `git show prereg-v1 --stat` contains the pre-registration and nothing from `results/`.
- Confirm no document was modified beyond the single date substitution, by diffing each placed file against its source.
- Confirm `data/` is ignored.
- Confirm no commit message contains an attribution line.

Report the tree and the five confirmations. Do not write any code this session. Setup only.
