import os
from dataclasses import dataclass

import duckdb
import numpy as np
import torch
from torch_geometric.nn import SAGEConv

from features import Frame
from protocol import PERIODS
from tuning import TRIALS

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))
torch.use_deterministic_algorithms(True)


@dataclass(frozen=True)
class Graph:
    x: torch.Tensor
    edge_index: torch.Tensor
    train_edge_index: torch.Tensor
    train_nodes: np.ndarray


def same_step_edges(src: np.ndarray, dst: np.ndarray, steps: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    keep = steps[src] == steps[dst]
    return src[keep], dst[keep]


def both_directions(src: np.ndarray, dst: np.ndarray) -> torch.Tensor:
    return torch.tensor(np.vstack([np.concatenate([src, dst]), np.concatenate([dst, src])]), dtype=torch.long)


def build_graph(frame: Frame, edge_src_ids: np.ndarray, edge_dst_ids: np.ndarray) -> Graph:
    """Edge ids are node ids; nodes are positions in frame.node_ids, which is sorted."""
    src, dst = np.searchsorted(frame.node_ids, edge_src_ids), np.searchsorted(frame.node_ids, edge_dst_ids)
    src, dst = same_step_edges(src, dst, frame.steps)
    train_nodes = frame.steps <= PERIODS["training"][1]
    mean = frame.local[train_nodes].mean(axis=0)
    std = frame.local[train_nodes].std(axis=0)
    x = ((frame.local - mean) / np.where(std > 0, std, 1.0)).astype(np.float32)
    in_training = train_nodes[src] & train_nodes[dst]
    return Graph(
        x=torch.tensor(x),
        edge_index=both_directions(src, dst),
        train_edge_index=both_directions(src[in_training], dst[in_training]),
        train_nodes=train_nodes,
    )


def load_edges(con: duckdb.DuckDBPyConnection) -> tuple[np.ndarray, np.ndarray]:
    e = con.execute("SELECT src, dst FROM edges").fetchnumpy()
    return e["src"], e["dst"]


def sample_configs(seed: int, n: int = TRIALS) -> list[dict]:
    rng = np.random.default_rng(seed)
    return [{
        "hidden": int(rng.choice([32, 64, 128])),
        "learning_rate": float(np.exp(rng.uniform(np.log(0.001), np.log(0.03)))),
        "dropout": float(rng.uniform(0.0, 0.5)),
        "weight_decay": float(np.exp(rng.uniform(np.log(1e-6), np.log(1e-3)))),
        "epochs": int(rng.integers(50, 201)),
        "class_weight": [None, "balanced"][int(rng.integers(0, 2))],
    } for _ in range(n)]


class SAGE(torch.nn.Module):
    def __init__(self, inputs: int, hidden: int, dropout: float):
        super().__init__()
        self.conv1 = SAGEConv(inputs, hidden, aggr="mean")
        self.conv2 = SAGEConv(hidden, 1, aggr="mean")
        self.dropout = dropout

    def forward(self, x, edge_index):
        h = torch.relu(self.conv1(x, edge_index))
        h = torch.nn.functional.dropout(h, p=self.dropout, training=self.training)
        return self.conv2(h, edge_index).squeeze(-1)


def fit_predict(config: dict, seed: int, graph: Graph, labels: np.ndarray, train: np.ndarray, score: np.ndarray) -> np.ndarray:
    """Trains on the training-step subgraph only, then scores score-mask nodes on the full graph."""
    assert not (train & ~graph.train_nodes).any(), "Arm D may only train on training-step nodes"
    torch.manual_seed(seed)
    positions = np.flatnonzero(graph.train_nodes)
    local_index = -np.ones(len(labels), dtype=int)
    local_index[positions] = np.arange(len(positions))
    x_train = graph.x[torch.tensor(positions)]
    edge_train = torch.tensor(local_index[graph.train_edge_index.numpy()], dtype=torch.long)
    target_idx = torch.tensor(local_index[np.flatnonzero(train)], dtype=torch.long)
    target = torch.tensor((labels[train] == 1).astype(np.float32))
    pos_weight = None
    if config["class_weight"] == "balanced":
        pos_weight = torch.tensor((target == 0).sum() / max(float(target.sum()), 1.0))

    model = SAGE(graph.x.shape[1], config["hidden"], config["dropout"])
    optimiser = torch.optim.Adam(model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"])
    model.train()
    for _ in range(config["epochs"]):
        optimiser.zero_grad()
        logits = model(x_train, edge_train)[target_idx]
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, target, pos_weight=pos_weight)
        loss.backward()
        optimiser.step()
    model.eval()
    with torch.no_grad():
        scores = torch.sigmoid(model(graph.x, graph.edge_index)).numpy()
    return scores[score].astype(np.float64)
