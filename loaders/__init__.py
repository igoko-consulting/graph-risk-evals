from loaders.contract import ContractError, Dataset, validate
from loaders.elliptic import ELLIPTIC

DATASETS = {ELLIPTIC.name: ELLIPTIC}


def get_dataset(name: str) -> Dataset:
    if name not in DATASETS:
        raise ContractError(f"unknown dataset {name!r}; registered: {sorted(DATASETS)}")
    return DATASETS[name]
