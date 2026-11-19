from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import duckdb

LABELS = ("illicit", "licit", "unknown")

CANONICAL_TABLES = {
    "nodes": {"node_id": "BIGINT", "time_step": "INTEGER"},
    "edges": {"src": "BIGINT", "dst": "BIGINT"},
    "labels": {"node_id": "BIGINT", "label": "VARCHAR"},
}


class ContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class Expected:
    """Figures as the PRD states them, with the precision the PRD states them to."""

    nodes: int
    edges: int
    time_steps: int
    raw_feature_columns: int
    feature_groups: dict
    label_shares: dict
    count_tolerance: float
    share_tolerance: float
    source: str


class Dataset(Protocol):
    name: str
    licence: str
    citation: str
    feature_groups: dict
    expected: Expected

    def fetch(self, raw_dir: Path) -> dict: ...

    def load(self, raw_dir: Path, con: duckdb.DuckDBPyConnection) -> None: ...


def check_feature_groups(groups: dict) -> None:
    seen: set = set()
    for name, columns in groups.items():
        if "time_step" in columns or "node_id" in columns:
            raise ContractError(f"feature group {name} contains an identifier or the time step")
        overlap = seen & set(columns)
        if overlap:
            raise ContractError(f"feature group {name} overlaps another group: {sorted(overlap)[:5]}")
        seen |= set(columns)


def _columns(con, table: str) -> dict:
    rows = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = ? ORDER BY ordinal_position",
        [table],
    ).fetchall()
    return dict(rows)


def validate(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> dict:
    """Structural checks raise. Count checks are returned for reporting and raise if outside tolerance."""
    check_feature_groups(dataset.feature_groups)
    for table, schema in CANONICAL_TABLES.items():
        if _columns(con, table) != schema:
            raise ContractError(f"table {table} does not match the contract {schema}")
    feature_columns = list(_columns(con, "features"))
    expected_features = ["node_id"] + [c for cols in dataset.feature_groups.values() for c in cols]
    if feature_columns != expected_features:
        raise ContractError("features table columns do not match the declared feature groups")

    q = lambda sql: con.execute(sql).fetchone()[0]
    structural = {
        "duplicate node ids": q("SELECT count(*) - count(DISTINCT node_id) FROM nodes"),
        "null node ids or time steps": q("SELECT count(*) FROM nodes WHERE node_id IS NULL OR time_step IS NULL"),
        "feature rows not matching nodes": q("SELECT (SELECT count(*) FROM features) - (SELECT count(*) FROM features JOIN nodes USING (node_id))"),
        "nodes without a feature row": q("SELECT count(*) FROM nodes ANTI JOIN features USING (node_id)"),
        "nodes without a label row": q("SELECT count(*) FROM nodes ANTI JOIN labels USING (node_id)"),
        "labels outside the label set": q(f"SELECT count(*) FROM labels WHERE label IS NULL OR label NOT IN {LABELS}"),
        "edges with an endpoint outside nodes": q("SELECT count(*) FROM edges e WHERE e.src NOT IN (SELECT node_id FROM nodes) OR e.dst NOT IN (SELECT node_id FROM nodes)"),
    }
    broken = {k: v for k, v in structural.items() if v}
    if broken:
        raise ContractError(f"structural checks failed: {broken}")

    exp = dataset.expected
    n_nodes = q("SELECT count(*) FROM nodes")
    observed_counts = {
        "nodes": n_nodes,
        "edges": q("SELECT count(*) FROM edges"),
        "time_steps": q("SELECT count(DISTINCT time_step) FROM nodes"),
    }
    counts = {}
    for key, observed in observed_counts.items():
        expected = getattr(exp, key)
        tol = 0 if key == "time_steps" else exp.count_tolerance
        counts[key] = {
            "prd": expected,
            "observed": observed,
            "relative_difference": round((observed - expected) / expected, 6),
            "tolerance": tol,
            "within_tolerance": abs(observed - expected) <= tol * expected,
        }
    label_counts = dict(con.execute("SELECT label, count(*) FROM labels GROUP BY label").fetchall())
    shares = {}
    for label in LABELS:
        share = label_counts.get(label, 0) / n_nodes
        shares[label] = {
            "prd": exp.label_shares[label],
            "observed": round(share, 6),
            "tolerance_absolute": exp.share_tolerance,
            "within_tolerance": abs(share - exp.label_shares[label]) <= exp.share_tolerance,
        }
    report = {
        "structural_checks": {k: {"violations": v} for k, v in structural.items()},
        "counts_against_prd": counts,
        "label_shares_against_prd": shares,
        "label_counts": {label: label_counts.get(label, 0) for label in LABELS},
        "expected_source": exp.source,
    }
    off = [k for k, v in {**counts, **shares}.items() if not v["within_tolerance"]]
    if off:
        raise ContractError(f"data does not match the PRD for: {off}. Stop and ask before continuing.")
    return report
