import math

import duckdb

from paths import COLUMNAR_STORE
from protocol import K_STEPS
from results_io import write_result


def main() -> None:
    first, last = K_STEPS
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        rows = con.execute(
            """
            SELECT s.step, count(n.node_id) AS nodes, count(l.node_id) FILTER (WHERE l.label = 'illicit') AS illicit
            FROM range(?, ? + 1) s(step)
            LEFT JOIN nodes n ON n.time_step = s.step
            LEFT JOIN labels l ON l.node_id = n.node_id
            GROUP BY s.step
            ORDER BY s.step
            """,
            [first, last],
        ).fetchall()
    steps = [r[0] for r in rows]
    assert steps == list(range(first, last + 1)), "k must cover every step from 1 to 34"
    assert all(r[1] > 0 for r in rows), "a step in 1 to 34 has no nodes"
    illicit = {r[0]: r[2] for r in rows}
    k_mean = sum(illicit.values()) / len(illicit)
    k = math.floor(k_mean + 0.5)
    path = write_result("k", {
        "definition": "Mean number of illicit labels per time step across steps 1 to 34, computed before any test step is read",
        "steps": [first, last],
        "illicit_labels_per_step": illicit,
        "illicit_labels_total": sum(illicit.values()),
        "k_mean": k_mean,
        "k": k,
        "integer_rule": "nearest whole number, halves rounded up; fixed 2026-11-19 before any arm was built (see change_log.md)",
    })
    print(f"k = {k} (mean {k_mean:.4f}) from steps {first} to {last}; written to {path.name}")


if __name__ == "__main__":
    main()
