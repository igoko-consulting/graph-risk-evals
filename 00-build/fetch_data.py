import json

import duckdb

from loaders import get_dataset, validate
from paths import COLUMNAR_STORE, DATASET, RAW


def main() -> None:
    dataset = get_dataset(DATASET)
    provenance = dataset.fetch(RAW)
    print(f"fetched {dataset.name} from {provenance['source']}; checksums verified")
    COLUMNAR_STORE.parent.mkdir(parents=True, exist_ok=True)
    COLUMNAR_STORE.unlink(missing_ok=True)
    with duckdb.connect(str(COLUMNAR_STORE)) as con:
        dataset.load(RAW, con)
        report = validate(con, dataset)
    print(json.dumps(report["counts_against_prd"], indent=2))
    print(f"loaded into {COLUMNAR_STORE.relative_to(COLUMNAR_STORE.parents[2])}; contract passed")


if __name__ == "__main__":
    main()
