"""Build time per arm: lab time estimated from the repository's history, beside the author's production estimate.

Neither figure is an input to cost per true positive. The production estimate is the author's, modelled, and read
from 03-the-margin/build-days.csv so that no figure is typed into a document.
"""
import csv
import hashlib
import subprocess

from paths import BUILD_DAYS, ROOT
from protocol import require
from results_io import write_result

# History is measured up to this commit, so later work cannot move the figures.
END = "df2e649"
CODE = ("00-build/", "graph/", "loaders/", "tests/", "Makefile", "requirements.in")
ARM_FILES = {
    "A": ("00-build/features.py", "00-build/tuning.py", "00-build/run_arms.py", "00-build/evaluate_arms.py"),
    "B": ("graph/queries/", "00-build/graph_store.py", "00-build/build_graph_store.py", "00-build/leakage_gate.py",
          "tests/test_graph_queries.py"),
    "D": ("00-build/arm_d.py", "00-build/run_arm_d.py"),
}
GAP_CAP_SECONDS = 3600
BATCH_SECONDS = 120
METHOD = (
    "Commits made within two minutes of each other form one batch, because the work was committed in batches. "
    "A batch's work time is the gap since the previous commit, capped at an hour because longer gaps hold pipeline "
    "runs or breaks, and it is split between arms by their share of the code lines the batch changed. The upper "
    "bound gives each arm the whole capped window of every batch that touched its files. Arm A owns the shared "
    "tabular pipeline, which B and D reuse, so B and D are counted for what they add; Gate 2 counts under B, whose "
    "graph features it exists to test."
)
CAVEAT = (
    "The repository was built with an AI coding assistant in a two-day sprint, so lab time is far below what a team "
    "would need and says little about production cost."
)


def batches() -> list[dict]:
    log = subprocess.run(["git", "-C", str(ROOT), "log", "--reverse", "--numstat", "--format=@%ct", END],
                         capture_output=True, text=True)
    require(log.returncode == 0, f"commit {END} is not in this clone's history; a full clone is needed")
    out = []
    for line in log.stdout.splitlines():
        if line.startswith("@"):
            t = int(line[1:])
            if out and t - out[-1]["end"] <= BATCH_SECONDS:
                out[-1]["end"] = t
            else:
                out.append({"start": t, "end": t, "files": {}})
        elif line.strip():
            added, deleted, path = line.split("\t")
            if added != "-":
                out[-1]["files"][path] = out[-1]["files"].get(path, 0) + int(added) + int(deleted)
    return out


def lab_minutes() -> dict:
    estimate = {arm: 0.0 for arm in ARM_FILES}
    upper = {arm: 0.0 for arm in ARM_FILES}
    previous = None
    for b in batches():
        work = min(b["start"] - previous, GAP_CAP_SECONDS) if previous is not None else 0
        previous = b["end"]
        code = sum(n for path, n in b["files"].items() if path.startswith(CODE))
        for arm, prefixes in ARM_FILES.items():
            lines = sum(n for path, n in b["files"].items() if path.startswith(prefixes))
            if lines:
                estimate[arm] += work * lines / code / 60
                upper[arm] += work / 60
    return {arm: {"estimate": round(estimate[arm], 1), "upper_bound": round(upper[arm], 1)} for arm in ARM_FILES}


def production_days() -> dict:
    with open(BUILD_DAYS, newline="") as f:
        rows = {r["arm"]: r for r in csv.DictReader(f)}
    require(set(rows) == set(ARM_FILES), f"{BUILD_DAYS.name} must have one row each for arms {', '.join(ARM_FILES)}")
    out = {}
    for arm in ARM_FILES:
        r = rows[arm]
        low, high, basis = r["production_days_low"].strip(), r["production_days_high"].strip(), r["basis"].strip()
        if not (low or high):
            out[arm] = None
            continue
        require(bool(low and high), f"{BUILD_DAYS.name}, arm {arm}: give both a low and a high estimate, equal if exact")
        low_f, high_f = float(low), float(high)
        require(0 < low_f <= high_f, f"{BUILD_DAYS.name}, arm {arm}: low must be positive and no more than high")
        require(bool(basis), f"{BUILD_DAYS.name}, arm {arm}: say what the estimate assumes in the basis column")
        out[arm] = {"low": low_f, "high": high_f, "basis": basis}
    return out


def main() -> None:
    write_result("build-days", {
        "lab_minutes": lab_minutes(),
        "lab_method": METHOD,
        "lab_caveat": CAVEAT,
        "lab_history_end": END,
        "production_days_modelled": production_days(),
        "production_source": f"{BUILD_DAYS.relative_to(ROOT)}, adopted by the author; each basis says where it came from",
        "production_file_sha256": hashlib.sha256(BUILD_DAYS.read_bytes()).hexdigest(),
        "used_in_cost_per_true_positive": False,
    })
    print("build days recorded")


if __name__ == "__main__":
    main()
