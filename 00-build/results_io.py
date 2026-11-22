import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import prereg_gate
from paths import GENERATED_DOCS, RAW, RESULTS, REVIEW_SCORES, REVIEW_SCORES_MODEL, ROOT, DATASET

NO_FEATURES = "not applicable: no model feature values are used or written"


class ResultRefused(RuntimeError):
    pass


def _git_state(root: Path) -> dict:
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    # The pipeline rewrites its own outputs mid-run, so they must not count as uncommitted code.
    outputs = [":!results", ":!site/charts", *(f":!{p.relative_to(ROOT)}" for p in (*GENERATED_DOCS, REVIEW_SCORES, REVIEW_SCORES_MODEL))]
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no", "--", ".", *outputs],
                           capture_output=True, text=True)
    return {"commit": head.stdout.strip(), "uncommitted_changes": bool(dirty.stdout.strip())}


def dataset_provenance() -> dict:
    path = RAW / DATASET / "provenance.json"
    if not path.is_file():
        raise ResultRefused(f"{path} is missing; run `make data` first")
    return json.loads(path.read_text())


def leakage_gate_status(root: Path, results_dir: Path) -> dict:
    path = results_dir / "leakage-tests.json"
    if not path.is_file():
        raise ResultRefused("the leakage gate has not run, so no feature-derived result may be written")
    gate = json.loads(path.read_text())
    if not gate["data"]["gate_passed"]:
        raise ResultRefused("the leakage gate did not pass")
    if gate["provenance"]["git"]["commit"] != _git_state(root)["commit"]:
        raise ResultRefused("the leakage gate passed at a different commit; rerun it")
    if gate["provenance"]["dataset"]["files_sha256"] != dataset_provenance()["files_sha256"]:
        raise ResultRefused("the leakage gate passed on different data; rerun it")
    return {"passed_at": gate["provenance"]["generated_at"], "dropped_features": gate["data"]["dropped_features"]}


def write_result(name: str, data: dict, *, uses_model_features: bool = False,
                 root: Path = ROOT, results_dir: Path = RESULTS) -> Path:
    gate = prereg_gate.check(root)
    leakage = leakage_gate_status(root, results_dir) if uses_model_features else NO_FEATURES
    raw = dataset_provenance()
    doc = {
        "result": name,
        "provenance": {
            "generated_by": Path(sys.argv[0]).name,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git": _git_state(root),
            "preregistration": gate,
            "leakage_gate": leakage,
            "dataset": {"name": raw["dataset"], "source": raw["source"], "files_sha256": raw["files_sha256"]},
        },
        "data": data,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    target = results_dir / f"{name}.json"
    tmp = results_dir / f"{name}.tmp"
    tmp.write_text(json.dumps(doc, indent=2) + "\n")
    os.replace(tmp, target)
    return target


def read_result(name: str) -> dict:
    path = RESULTS / f"{name}.json"
    if not path.is_file():
        raise ResultRefused(f"{path} is missing; an earlier stage has not run")
    return json.loads(path.read_text())
