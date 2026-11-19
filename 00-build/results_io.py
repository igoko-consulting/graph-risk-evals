import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import prereg_gate
from paths import RAW, RESULTS, ROOT, DATASET

NO_FEATURES = "not applicable: no model feature values are used or written"


class ResultRefused(RuntimeError):
    pass


def _git_state(root: Path) -> dict:
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
    return {"commit": head.stdout.strip(), "uncommitted_changes": bool(dirty.stdout.strip())}


def dataset_provenance() -> dict:
    path = RAW / DATASET / "provenance.json"
    if not path.is_file():
        raise ResultRefused(f"{path} is missing; run `make data` first")
    return json.loads(path.read_text())


def write_result(name: str, data: dict, *, uses_model_features: bool = False,
                 root: Path = ROOT, results_dir: Path = RESULTS) -> Path:
    gate = prereg_gate.check(root)
    if uses_model_features:
        raise ResultRefused("leakage tests are not implemented yet, so no feature-derived result may be written")
    raw = dataset_provenance()
    doc = {
        "result": name,
        "provenance": {
            "generated_by": Path(sys.argv[0]).name,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git": _git_state(root),
            "preregistration": gate,
            "leakage_gate": NO_FEATURES,
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
