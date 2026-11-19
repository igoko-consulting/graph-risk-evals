# Claude Code prompt — session 1

Paste this as the first message in Claude Code, with the repository already created and the first commit in place.

---

You are building `graph-risk-evals`, a pre-registered lab testing when graph methods earn their cost in fraud and AML detection.

**Read these first, in this order:**

1. `CLAUDE.md` — working rules and red lines. These bind every session.
2. `prds/prd-v2.md` — the working specification. Implement from this.
3. `01-the-bet/pre-registration.md` — the committed hypotheses.

**Do not implement from `prds/prd-v1.md`.** It is historical and contains three errors corrected in v2. If the two disagree, v2 is right.

---

## This session builds the thin end-to-end slice, and nothing else

The goal is a pipeline that runs from a clean clone, loads data, computes one metric, renders one chart, with every version pinned. Resist building arms, features or the site. Library and version problems should surface now, not on day three.

**Deliverables for this session, in order:**

1. **Repository skeleton** matching the structure in the README, with empty module directories and a `NOTES.md` in each.
2. **`.gitignore`** excluding `data/` and the usual Python artefacts. Datasets are never committed.
3. **`requirements.txt`** with exact pinned versions. No ranges, no bare names. Choose versions at least two weeks old.
4. **`Makefile`** with `make all` as the single entry point, plus `make data`, `make test` and `make clean`.
5. **`loaders/`** with a schema contract and a fetch script for the primary dataset. The interface must be designed so a second dataset plugs in without a rebuild: see the Phase 5 section of the PRD.
6. **Day-one data checks**, reported as output and written to `04-the-data/NOTES.md`:
   - Confirm node, edge, feature and time-step counts against the PRD.
   - Confirm the local and aggregate feature split, and which column indices belong to each.
   - **Answer the open question: do any edges cross time steps?** This is load-bearing for the whole leakage analysis. If they do, stop and say so before continuing.
   - Report the label distribution by class and by time step.
   - Compute k as specified: mean illicit labels per time step across steps 1 to 29 and the validation window, in code, before any test step is read. Write it to `results/`.
7. **Graph store loaded.** Per-time-step graphs in the embedded store. One traversal query committed to `graph/queries/` that computes in-degree, to prove the path works.
8. **Pre-registration gate.** The hash check described in the PRD: hash `01-the-bet/pre-registration.md`, compare against the `prereg-v1` tag, refuse to write to `results/` on mismatch. Roughly twenty lines. Test that it fails when it should.
9. **One metric, one chart.** Simplest possible: class balance by time step, computed from code, written to `results/`, rendered as a static chart. This proves the whole path from data to output.

---

## Constraints for this session

- **Static.** No server, no keys, no network at view time.
- **Laptop CPU.** No GPU anywhere in the stack.
- **Under 30 minutes** for the full run on a clean clone.
- **Every number from code.** Nothing hand-entered, nothing written by a model.
- **Plain commit messages.** No attribution or co-authorship lines.

---

## Stop and ask if

- Edges cross time steps. The leakage design changes and I need to decide before you continue.
- The feature split does not match the PRD. Arm A's isolation depends on it.
- The dataset licence restricts what the PRD assumes.
- Any pinned version has no release old enough to be safe.
- A red line in `CLAUDE.md` blocks the work.

Say what you found, what it blocks, and what the options are. Do not proceed on an assumption that would change a result.

---

## The gate for this session

The slice runs end to end on a clean clone. If it does not by the end of the session, the kill criterion in the pre-registration fires and the repository ships as a method write-up instead. Tell me plainly if we reach that point.

Start by reading the three documents and telling me your plan for this session before you write code.
