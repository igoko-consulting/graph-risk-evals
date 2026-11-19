import base64
import hashlib
import json
import os
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from loaders.contract import ContractError, Expected, check_feature_groups

FILES = ("elliptic_txs_features.csv", "elliptic_txs_edgelist.csv", "elliptic_txs_classes.csv")
# Pinned from the PyTorch Geometric mirror on 2026-11-19. A Kaggle fetch must produce the
# same bytes, which is how the mirror is verified against the publisher's copy.
SHA256 = {
    "elliptic_txs_features.csv": "fd7f83573443c9e302e371d3f110e3b6224160f5d1ed8a287757936127800ff0",
    "elliptic_txs_edgelist.csv": "a35053ba68a98e4382cae2ba65b9d9e36b23b6439e02dff084971b1b72a5156e",
    "elliptic_txs_classes.csv": "93e2e7b2405c735ba752bf6ba06b947561deddd1f5a8fc91e46f6a4c0e439493",
}

MIRROR_URL = "https://data.pyg.org/datasets/elliptic"
KAGGLE_URL = "https://www.kaggle.com/api/v1/datasets/download/ellipticco/elliptic-data-set"
KAGGLE_PAGE = "https://www.kaggle.com/datasets/ellipticco/elliptic-data-set"

# Raw features file has no header. Column 0 is the transaction id. The dataset paper
# (Weber et al. 2019) states the first 94 features are local and include the time step,
# which is column 1; the remaining 72 are one-hop aggregates. The split cannot be verified
# from the anonymised values themselves, so it is fixed here and asserted.
RAW_ID_COLUMN = 0
RAW_TIME_STEP_COLUMN = 1
RAW_LOCAL_COLUMNS = tuple(range(2, 95))
RAW_AGGREGATE_COLUMNS = tuple(range(95, 167))

LOCAL = tuple(f"local_{i:02d}" for i in range(1, len(RAW_LOCAL_COLUMNS) + 1))
AGGREGATE = tuple(f"agg_{i:02d}" for i in range(1, len(RAW_AGGREGATE_COLUMNS) + 1))

assert len(LOCAL) == 93 and len(AGGREGATE) == 72
assert RAW_TIME_STEP_COLUMN not in RAW_LOCAL_COLUMNS + RAW_AGGREGATE_COLUMNS


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _kaggle_credentials() -> tuple | None:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return os.environ["KAGGLE_USERNAME"], os.environ["KAGGLE_KEY"]
    token = Path.home() / ".kaggle" / "kaggle.json"
    if token.is_file():
        creds = json.loads(token.read_text())
        return creds["username"], creds["key"]
    return None


def _download(url: str, target: Path, headers: dict | None = None) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "graph-risk-evals-loader", **(headers or {})})
    with urllib.request.urlopen(request, timeout=120) as response, target.open("wb") as out:
        shutil.copyfileobj(response, out, 1 << 20)


def _extract(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        for member in z.namelist():
            name = Path(member).name
            if name in FILES:
                with z.open(member) as src, (out_dir / name).open("wb") as dst:
                    shutil.copyfileobj(src, dst, 1 << 20)


class Elliptic:
    name = "elliptic"
    licence = "CC BY-NC-ND 4.0, as listed on Kaggle by the publisher"
    citation = (
        "Weber, M. et al. (2019). Anti-Money Laundering in Bitcoin: Experimenting with Graph "
        "Convolutional Networks for Financial Forensics. KDD Workshop on Anomaly Detection in Finance."
    )
    feature_groups = {"local": LOCAL, "aggregate": AGGREGATE}
    expected = Expected(
        nodes=203_000,
        edges=234_000,
        time_steps=49,
        raw_feature_columns=166,
        feature_groups={"local_including_time_step": 94, "aggregate": 72},
        label_shares={"illicit": 0.02, "licit": 0.21, "unknown": 0.77},
        count_tolerance=0.01,
        share_tolerance=0.01,
        source="prds/prd-v2.md, Data requirements. Counts stated to three significant figures, shares to whole percentages.",
    )

    def fetch(self, raw_dir: Path) -> dict:
        out = raw_dir / self.name
        out.mkdir(parents=True, exist_ok=True)
        provenance_path = out / "provenance.json"
        if provenance_path.is_file() and all((out / f).is_file() for f in FILES):
            provenance = json.loads(provenance_path.read_text())
            if {f: _sha256(out / f) for f in FILES} == SHA256:
                return provenance

        source = os.environ.get("GRE_DATA_SOURCE") or ("kaggle" if _kaggle_credentials() else "mirror")
        if source == "kaggle":
            creds = _kaggle_credentials()
            if creds is None:
                raise ContractError("GRE_DATA_SOURCE=kaggle but no Kaggle credentials were found")
            auth = base64.b64encode(f"{creds[0]}:{creds[1]}".encode()).decode()
            archive = out / "kaggle.zip"
            _download(KAGGLE_URL, archive, {"Authorization": f"Basic {auth}"})
            _extract(archive, out)
            archive.unlink()
            source_url = KAGGLE_PAGE
        elif source == "mirror":
            for name in FILES:
                archive = out / f"{name}.zip"
                _download(f"{MIRROR_URL}/{name}.zip", archive)
                _extract(archive, out)
                archive.unlink()
            source_url = MIRROR_URL
        else:
            raise ContractError(f"unknown GRE_DATA_SOURCE {source!r}; use kaggle or mirror")

        observed = {f: _sha256(out / f) for f in FILES}
        if observed != SHA256:
            raise ContractError(f"checksums from {source} do not match the pinned values: {observed}")
        provenance = {
            "dataset": self.name,
            "source": source,
            "source_url": source_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "files_sha256": observed,
            "licence": self.licence,
        }
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        return provenance

    def load(self, raw_dir: Path, con: duckdb.DuckDBPyConnection) -> None:
        check_feature_groups(self.feature_groups)
        out = raw_dir / self.name
        raw_columns = {"node_id": "BIGINT", "time_step": "INTEGER"}
        raw_columns |= {c: "DOUBLE" for c in LOCAL + AGGREGATE}
        con.execute(
            "CREATE OR REPLACE TEMP TABLE raw_features AS SELECT * FROM read_csv(?, header = false, columns = ?)",
            [str(out / "elliptic_txs_features.csv"), raw_columns],
        )
        con.execute("CREATE OR REPLACE TABLE nodes AS SELECT node_id, time_step FROM raw_features ORDER BY node_id")
        columns = ", ".join(LOCAL + AGGREGATE)
        con.execute(f"CREATE OR REPLACE TABLE features AS SELECT node_id, {columns} FROM raw_features ORDER BY node_id")
        con.execute(
            "CREATE OR REPLACE TABLE edges AS SELECT CAST(txId1 AS BIGINT) AS src, CAST(txId2 AS BIGINT) AS dst "
            "FROM read_csv(?, header = true, all_varchar = true)",
            [str(out / "elliptic_txs_edgelist.csv")],
        )
        con.execute(
            "CREATE OR REPLACE TABLE labels AS SELECT CAST(txId AS BIGINT) AS node_id, "
            "CASE class WHEN '1' THEN 'illicit' WHEN '2' THEN 'licit' WHEN 'unknown' THEN 'unknown' END AS label "
            "FROM read_csv(?, header = true, all_varchar = true)",
            [str(out / "elliptic_txs_classes.csv")],
        )
        con.execute("DROP TABLE raw_features")

    def raw_shape(self, raw_dir: Path, con: duckdb.DuckDBPyConnection) -> dict:
        path = str(raw_dir / self.name / "elliptic_txs_features.csv")
        names = [d[0] for d in con.execute("SELECT * FROM read_csv(?, header = false) LIMIT 0", [path]).description]
        n_columns = len(names)
        col = f'"{names[RAW_TIME_STEP_COLUMN]}"'
        step = con.execute(
            f"SELECT min({col}), max({col}), count(DISTINCT {col}), bool_and({col} = floor({col})) "
            "FROM read_csv(?, header = false)",
            [path],
        ).fetchone()
        return {
            "raw_columns": n_columns,
            "raw_feature_columns": n_columns - 1,
            "time_step_column": {"index": RAW_TIME_STEP_COLUMN, "min": step[0], "max": step[1],
                                 "distinct": step[2], "integer_valued": bool(step[3])},
            "local_columns": {"indices": [RAW_LOCAL_COLUMNS[0], RAW_LOCAL_COLUMNS[-1]], "count": len(RAW_LOCAL_COLUMNS),
                              "names": [LOCAL[0], LOCAL[-1]]},
            "aggregate_columns": {"indices": [RAW_AGGREGATE_COLUMNS[0], RAW_AGGREGATE_COLUMNS[-1]],
                                  "count": len(RAW_AGGREGATE_COLUMNS), "names": [AGGREGATE[0], AGGREGATE[-1]]},
        }


ELLIPTIC = Elliptic()
