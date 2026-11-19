import json
import subprocess
from pathlib import Path

import pytest

import prereg_gate
import results_io
from paths import ROOT
from prereg_gate import PREREG_PATH, TAG, PreregistrationMismatch


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "test")
    prereg = tmp_path / PREREG_PATH
    prereg.parent.mkdir(parents=True)
    prereg.write_text("# Pre-registration\n\nH1. A hypothesis.\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "Commit pre-registration")
    git(tmp_path, "tag", "-a", TAG, "-m", "tag")
    return tmp_path


def test_real_repository_passes():
    assert prereg_gate.check(ROOT)["tag"] == TAG


def test_untouched_file_passes(repo):
    assert len(prereg_gate.check(repo)["prereg_sha256"]) == 64


def test_edited_file_fails(repo):
    (repo / PREREG_PATH).write_text("# Pre-registration\n\nH1. A different hypothesis.\n")
    with pytest.raises(PreregistrationMismatch, match="does not match"):
        prereg_gate.check(repo)


def test_whitespace_change_fails(repo):
    path = repo / PREREG_PATH
    path.write_text(path.read_text() + " ")
    with pytest.raises(PreregistrationMismatch):
        prereg_gate.check(repo)


def test_missing_tag_fails(repo):
    git(repo, "tag", "-d", TAG)
    with pytest.raises(PreregistrationMismatch, match="missing"):
        prereg_gate.check(repo)


def test_lightweight_tag_fails(repo):
    git(repo, "tag", "-d", TAG)
    git(repo, "tag", TAG)
    with pytest.raises(PreregistrationMismatch, match="annotated"):
        prereg_gate.check(repo)


def test_deleted_file_fails(repo):
    (repo / PREREG_PATH).unlink()
    with pytest.raises(PreregistrationMismatch, match="missing"):
        prereg_gate.check(repo)


def test_nothing_is_written_on_mismatch(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(results_io, "dataset_provenance", lambda: {"dataset": "x", "source": "x", "files_sha256": {}})
    out = tmp_path / "results"
    (repo / PREREG_PATH).write_text("edited after the tag\n")
    with pytest.raises(PreregistrationMismatch):
        results_io.write_result("anything", {"value": 1}, root=repo, results_dir=out)
    assert not out.exists()


def test_write_succeeds_when_gate_passes(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(results_io, "dataset_provenance", lambda: {"dataset": "x", "source": "x", "files_sha256": {}})
    out = tmp_path / "results"
    path = results_io.write_result("anything", {"value": 1}, root=repo, results_dir=out)
    doc = json.loads(path.read_text())
    assert doc["provenance"]["preregistration"]["tag"] == TAG
    assert doc["data"] == {"value": 1}


def test_feature_derived_results_are_refused_until_leakage_tests_exist(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(results_io, "dataset_provenance", lambda: {"dataset": "x", "source": "x", "files_sha256": {}})
    out = tmp_path / "results"
    with pytest.raises(results_io.ResultRefused):
        results_io.write_result("arm-a", {"value": 1}, uses_model_features=True, root=repo, results_dir=out)
    assert not out.exists()
