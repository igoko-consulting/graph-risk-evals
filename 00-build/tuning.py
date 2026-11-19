import time

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score

TRIALS = 40
SEEDS = (0, 1, 2, 3, 4)
REFERENCE_CONFIG = {
    "learning_rate": 0.1, "max_iter": 100, "max_leaf_nodes": 31, "min_samples_leaf": 20,
    "l2_regularization": 0.0, "max_features": 1.0, "class_weight": None,
}


def sample_configs(seed: int, n: int = TRIALS) -> list[dict]:
    rng = np.random.default_rng(seed)
    configs = []
    for _ in range(n):
        configs.append({
            "learning_rate": float(np.exp(rng.uniform(np.log(0.01), np.log(0.3)))),
            "max_iter": int(rng.integers(50, 501)),
            "max_leaf_nodes": int(rng.integers(15, 128)),
            "min_samples_leaf": int(rng.integers(10, 201)),
            "l2_regularization": float(np.exp(rng.uniform(np.log(1e-4), np.log(10.0)))),
            "max_features": float(rng.uniform(0.5, 1.0)),
            "class_weight": [None, "balanced"][int(rng.integers(0, 2))],
        })
    return configs


def make_model(config: dict, seed: int) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(**config, early_stopping=False, random_state=seed)


def fit_predict(config: dict, seed: int, X: np.ndarray, y: np.ndarray, train: np.ndarray, score: np.ndarray) -> np.ndarray:
    model = make_model(config, seed).fit(X[train], y[train])
    return model.predict_proba(X[score])[:, 1]


def tune(X: np.ndarray, y: np.ndarray, train: np.ndarray, validation: np.ndarray, seed: int) -> tuple[dict, list[dict]]:
    trials = []
    for config in sample_configs(seed):
        started = time.perf_counter()
        scores = fit_predict(config, seed, X, y, train, validation)
        trials.append({
            "config": config,
            "validation_average_precision": float(average_precision_score(y[validation], scores)),
            "fit_seconds": time.perf_counter() - started,
        })
    best = max(range(len(trials)), key=lambda i: trials[i]["validation_average_precision"])
    return trials[best]["config"], trials
