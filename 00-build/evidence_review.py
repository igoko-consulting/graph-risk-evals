"""The author's scores for the evidence-chain review sample, kept in git without the chains.

The chains name transactions, and the dataset's licence rules out publishing per-transaction outputs, so
the sheet the author reads and scores stays in data/store/runs/. Each score is saved to
05-evals-and-guardrails/evidence-chain-scores.csv against a SHA-256 of the chain it judges, so a later run
refills the sheet, and a chain that changes cannot inherit a score given to a different one.
"""
import csv
import hashlib
import re

from paths import REVIEW_SCORES, REVIEW_SHEET, ROOT
from protocol import require
from results_io import write_result

CRITERIA = ("true", "sufficient", "actionable")
ANSWERS = {"y": "y", "yes": "y", "n": "n", "no": "n", "": ""}
SHEET_COLUMNS = ("node_id", "chain", *CRITERIA, "note")
SCORE_COLUMNS = ("chain_sha256", *CRITERIA, "note")
RUBRIC = "Is the reason true, sufficient, and actionable by an investigator. Each answered y or n by the author."


def fingerprint(chain: str) -> str:
    return hashlib.sha256(chain.encode()).hexdigest()


def read_csv(path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def read_saved(scores=REVIEW_SCORES) -> dict[str, dict]:
    return {r["chain_sha256"]: r for r in read_csv(scores)} if scores.is_file() else {}


def scores_from_sheet(sheet=REVIEW_SHEET) -> list[dict]:
    rows = []
    for line, r in enumerate(read_csv(sheet), start=2):
        answers = {}
        for c in CRITERIA:
            raw = r.get(c) or ""
            require(raw.strip().lower() in ANSWERS, f"{sheet.name} line {line}: {c} is {raw!r}; use y, n or leave it blank")
            answers[c] = ANSWERS[raw.strip().lower()]
        require(sum(map(bool, answers.values())) in (0, len(CRITERIA)),
                f"{sheet.name} line {line}: answer all three criteria or none")
        note = (r.get("note") or "").strip()
        require(not re.search(r"\d{5,}", note),
                f"{sheet.name} line {line}: the note holds what looks like a transaction ID, and notes are published")
        rows.append({"chain_sha256": fingerprint(r["chain"]), **answers, "note": note})
    return rows


def scored(row: dict) -> bool:
    return any(row[c] for c in CRITERIA) or bool(row["note"])


def refuse_stale(saved: dict, current: set) -> None:
    stale = [h for h, r in saved.items() if h not in current and scored(r)]
    require(not stale, f"{len(stale)} saved scores in {REVIEW_SCORES.relative_to(ROOT)} judge chains that are no "
                       "longer in the review sample, so they cannot be carried over. Move the file aside and score "
                       "the new sample.")


def sync(sheet=REVIEW_SHEET, scores=REVIEW_SCORES) -> list[dict]:
    """Save the sheet's scores in sheet order. A blank sheet row keeps a score already saved for that chain."""
    saved = read_saved(scores)
    rows = [r if scored(r) else saved.get(r["chain_sha256"], r) for r in scores_from_sheet(sheet)]
    refuse_stale(saved, {r["chain_sha256"] for r in rows})
    with open(scores, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCORE_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def write_sheet(sample: list[tuple[int, str]], sheet=REVIEW_SHEET, scores=REVIEW_SCORES) -> None:
    """Called by evidence_chains: saves any scores in the old sheet, then writes the new one refilled from them."""
    if sheet.is_file():
        sync(sheet, scores)
    saved = read_saved(scores)
    refuse_stale(saved, {fingerprint(chain) for _, chain in sample})
    sheet.parent.mkdir(parents=True, exist_ok=True)
    with open(sheet, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(SHEET_COLUMNS)
        for node_id, chain in sample:
            s = saved.get(fingerprint(chain), {})
            w.writerow([node_id, chain, *(s.get(c, "") for c in CRITERIA), s.get("note", "")])


def main() -> None:
    require(REVIEW_SHEET.is_file(), f"{REVIEW_SHEET.relative_to(ROOT)} is missing; run `make all` first")
    rows = sync()
    done = [r for r in rows if r["true"]]
    yes = {c: sum(r[c] == "y" for r in done) for c in CRITERIA}
    write_result("evidence-chain-review", {
        "sample": len(rows),
        "scored": len(done),
        "answered_yes": yes,
        "yes_to_all_three": sum(all(r[c] == "y" for c in CRITERIA) for r in done),
        "rubric": RUBRIC,
        "scorer": "The author alone; there is no second scorer.",
        "drawn_from": "A seeded sample of Arm B's pre-shift queue, as recorded in results/evidence-chains.json.",
        "scores_file": str(REVIEW_SCORES.relative_to(ROOT)),
        "sheet": str(REVIEW_SHEET.relative_to(ROOT)),
    })
    print(f"evidence-chain review: {len(done)} of {len(rows)} scored; scores saved to {REVIEW_SCORES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
