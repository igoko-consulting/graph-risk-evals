from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
STORE = DATA / "store"
RESULTS = ROOT / "results"
QUERIES = ROOT / "graph" / "queries"
CHARTS = ROOT / "site" / "charts"
DATA_NOTES = ROOT / "04-the-data" / "NOTES.md"
README = ROOT / "README.md"
ENGINE_DOC = ROOT / "docs" / "engine-comparison.md"
MARGIN_NOTES = ROOT / "03-the-margin" / "NOTES.md"
GENERATED_DOCS = (README, ENGINE_DOC, DATA_NOTES, MARGIN_NOTES)

DATASET = "elliptic"
COLUMNAR_STORE = STORE / f"{DATASET}.duckdb"
GRAPH_STORE = STORE / f"{DATASET}.lbug"
RUNS = STORE / "runs"
