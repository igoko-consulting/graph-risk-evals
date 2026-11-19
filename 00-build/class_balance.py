import duckdb

from paths import COLUMNAR_STORE
from protocol import period_of, require_k_first
from results_io import write_result


def main() -> None:
    require_k_first()
    with duckdb.connect(str(COLUMNAR_STORE), read_only=True) as con:
        rows = con.execute(
            """
            SELECT n.time_step,
                   count(*) FILTER (WHERE l.label = 'illicit'),
                   count(*) FILTER (WHERE l.label = 'licit'),
                   count(*) FILTER (WHERE l.label = 'unknown')
            FROM nodes n JOIN labels l USING (node_id)
            GROUP BY n.time_step
            ORDER BY n.time_step
            """
        ).fetchall()
    by_step = []
    for step, illicit, licit, unknown in rows:
        labelled = illicit + licit
        by_step.append({
            "time_step": step,
            "period": period_of(step),
            "illicit": illicit,
            "licit": licit,
            "unknown": unknown,
            "nodes": labelled + unknown,
            "illicit_share_of_labelled": illicit / labelled if labelled else None,
        })
    path = write_result("class-balance-by-time-step", {
        "definition": "Label counts per time step. Illicit share is computed over labelled nodes only; unlabelled nodes are not treated as licit",
        "by_time_step": by_step,
    })
    print(f"class balance for {len(by_step)} time steps written to {path.name}")


if __name__ == "__main__":
    main()
