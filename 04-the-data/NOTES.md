# 04-the-data: dataset notes, labels, leakage tests

## Source and terms

- **Dataset:** the Elliptic Data Set, a Bitcoin transaction graph published by Elliptic. Weber, M. et al. (2019), *Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics*, KDD Workshop on Anomaly Detection in Finance.
- **Licence:** CC BY-NC-ND 4.0, as listed on the publisher's Kaggle page (`kaggle.com/datasets/ellipticco/elliptic-data-set`).
- **What that means here:** the data is never committed (`data/` is git-ignored) and is fetched by `loaders/`. `results/` holds aggregate figures only, never per-node features, scores or labels, so nothing published here is a redistributed or adapted copy of the dataset. Whether a given reuse counts as non-commercial is a judgement for whoever reuses it.
- **This is not payments data.** Nodes are Bitcoin transactions, not accounts. Features are anonymised.

## How the data is fetched

`make data` fetches from Kaggle when a token exists (`~/.kaggle/kaggle.json` or `KAGGLE_USERNAME` and `KAGGLE_KEY`), and otherwise from the PyTorch Geometric public mirror (`data.pyg.org/datasets/elliptic`), which needs no login. Either way the three CSV files must match the SHA-256 checksums pinned in `loaders/elliptic.py`, so both routes are held to identical bytes. Force a route with `GRE_DATA_SOURCE=kaggle` or `GRE_DATA_SOURCE=mirror`.

The checksums were pinned from the mirror. The Kaggle route has not yet been run, so the mirror has not yet been verified against the publisher's copy. The first Kaggle fetch either confirms the bytes are identical or fails loudly.

## Canonical tables

Every dataset loads into the same tables in the columnar store, `data/store/<dataset>.duckdb`, checked by `loaders/contract.py`:

| Table | Columns | Note |
|---|---|---|
| `nodes` | `node_id`, `time_step` | The only place the time step lives |
| `edges` | `src`, `dst` | Directed |
| `labels` | `node_id`, `label` | `illicit`, `licit` or `unknown` |
| `features` | `node_id`, then one column per declared feature | No time step, by construction, so Arm A cannot read it |

A second dataset plugs in by implementing `fetch` and `load` to produce these tables and declaring its feature groups. Nothing downstream changes.
