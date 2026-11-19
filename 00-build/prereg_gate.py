import hashlib
import subprocess
from pathlib import Path

TAG = "prereg-v1"
PREREG_PATH = "01-the-bet/pre-registration.md"


class PreregistrationMismatch(RuntimeError):
    pass


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True)


def check(root: Path) -> dict:
    if _git(root, "cat-file", "-t", TAG).stdout.strip() != b"tag":
        raise PreregistrationMismatch(f"{TAG} is missing or is not an annotated tag")
    tagged = _git(root, "show", f"{TAG}:{PREREG_PATH}")
    if tagged.returncode != 0:
        raise PreregistrationMismatch(f"{PREREG_PATH} is not in the commit tagged {TAG}")
    current_path = root / PREREG_PATH
    if not current_path.is_file():
        raise PreregistrationMismatch(f"{PREREG_PATH} is missing from the working tree")
    tagged_sha = hashlib.sha256(tagged.stdout).hexdigest()
    current_sha = hashlib.sha256(current_path.read_bytes()).hexdigest()
    if tagged_sha != current_sha:
        raise PreregistrationMismatch(
            f"{PREREG_PATH} sha256 {current_sha} does not match {TAG} sha256 {tagged_sha}"
        )
    commit = _git(root, "rev-parse", f"{TAG}^{{commit}}").stdout.decode().strip()
    return {"tag": TAG, "tag_commit": commit, "prereg_sha256": current_sha}


if __name__ == "__main__":
    from paths import ROOT

    print(check(ROOT))
