from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
STORE = DATA / "store"
RESULTS = ROOT / "results"
QUERIES = ROOT / "graph" / "queries"
CHARTS = ROOT / "site" / "charts"
DATA_NOTES = ROOT / "04-the-data" / "NOTES.md"

DATASET = "elliptic"
COLUMNAR_STORE = STORE / f"{DATASET}.duckdb"
GRAPH_STORE = STORE / f"{DATASET}.lbug"
