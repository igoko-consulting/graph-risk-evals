from dataclasses import dataclass

import duckdb
import numpy as np

from loaders import ELLIPTIC
from protocol import PERIODS, require

LOCAL = ELLIPTIC.feature_groups["local"]
AGGREGATE = ELLIPTIC.feature_groups["aggregate"]
STAGE_ONE_BLOCKS = ((1, 6), (7, 12), (13, 18), (19, 24), (25, 29))

ILLICIT, LICIT, UNKNOWN = 1, 0, -1


@dataclass(frozen=True)
class Frame:
    node_ids: np.ndarray
    steps: np.ndarray
    labels: np.ndarray
    local: np.ndarray
    aggregate: np.ndarray

    def mask(self, period: str) -> np.ndarray:
        first, last = PERIODS[period]
        return (self.steps >= first) & (self.steps <= last)

    @property
    def labelled(self) -> np.ndarray:
        return self.labels != UNKNOWN

    def with_labels(self, labels: np.ndarray) -> "Frame":
        return Frame(self.node_ids, self.steps, labels, self.local, self.aggregate)


def load_frame(con: duckdb.DuckDBPyConnection) -> Frame:
    columns = ", ".join(f"f.{c}" for c in LOCAL + AGGREGATE)
    data = con.execute(
        f"""
        SELECT n.node_id, n.time_step,
               CASE l.label WHEN 'illicit' THEN {ILLICIT} WHEN 'licit' THEN {LICIT} ELSE {UNKNOWN} END AS label,
               {columns}
        FROM nodes n JOIN labels l USING (node_id) JOIN features f USING (node_id)
        ORDER BY n.node_id
        """
    ).fetchnumpy()
    return Frame(
        node_ids=data["node_id"],
        steps=data["time_step"].astype(int),
        labels=data["label"].astype(int),
        local=np.column_stack([data[c] for c in LOCAL]).astype(float),
        aggregate=np.column_stack([data[c] for c in AGGREGATE]).astype(float),
    )


def arm_a(frame: Frame) -> tuple[np.ndarray, tuple]:
    """Red line 3: the 93 local features, never the time step, never anything from the graph store."""
    names = tuple(LOCAL)
    require(len(names) == 93 and "time_step" not in names, "Arm A must use the 93 local features and never the time step")
    require(frame.local.shape[1] == len(names), "Arm A's feature matrix does not match its feature names")
    require(not any(np.array_equal(frame.local[:, i], frame.steps) for i in range(frame.local.shape[1])), "a column of Arm A's features is a copy of the time step")
    return frame.local, names


def arm_b(frame: Frame, structural: dict, aggregates: dict, dropped: set) -> tuple[np.ndarray, tuple]:
    blocks = [frame.local, frame.aggregate]
    names = list(LOCAL) + list(AGGREGATE)
    for name, values in {**structural, **aggregates}.items():
        if name not in dropped:
            blocks.append(values[:, None])
            names.append(name)
    require("time_step" not in names, "Arm B's features may not include the time step")
    return np.hstack(blocks), tuple(names)


def stage_one_scores(frame: Frame, fit_predict) -> np.ndarray:
    """Out-of-fold over contiguous training blocks; evaluation steps scored by a model trained on steps 1 to 29.

    fit_predict(train_mask, score_mask) fits on train_mask and returns scores for score_mask.
    """
    scores = np.full(len(frame.node_ids), np.nan)
    training = frame.mask("training") & frame.labelled
    for first, last in STAGE_ONE_BLOCKS:
        block = (frame.steps >= first) & (frame.steps <= last)
        scores[block] = fit_predict(training & ~block, block)
    evaluation = frame.steps > PERIODS["training"][1]
    scores[evaluation] = fit_predict(training, evaluation)
    require(not np.isnan(scores).any(), "stage-one scores contain NaN")
    return scores


BUDGETS = (0.05, 0.10, 0.25, 0.50, 1.00)


def budget_labels(frame: Frame, fraction: float, seed: int) -> np.ndarray:
    """Keeps `fraction` of each class among labelled training nodes; one permutation per seed, so budgets nest."""
    rng = np.random.default_rng([seed, 20261119])
    labels = frame.labels.copy()
    training = frame.mask("training")
    for cls in (ILLICIT, LICIT):
        members = np.flatnonzero(training & (frame.labels == cls))
        order = rng.permutation(members)
        keep = int(round(fraction * len(members)))
        labels[order[keep:]] = UNKNOWN
    return labels
