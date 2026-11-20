-- Engine comparison only; Arm B never reads this. Same result as graph/queries/pagerank-setup.cypher.
-- PageRank within each time step, part 1 of 2: same-step out-degree, step size, uniform start.
CREATE OR REPLACE TEMP TABLE pr AS
WITH outdeg AS (
    SELECT e.src AS node_id, count(*) AS outdeg
    FROM edges e
    JOIN nodes a ON a.node_id = e.src
    JOIN nodes b ON b.node_id = e.dst
    WHERE a.time_step = b.time_step
    GROUP BY e.src
),
sizes AS (
    SELECT time_step, count(*) AS n_step FROM nodes GROUP BY time_step
)
SELECT n.node_id, n.time_step, coalesce(o.outdeg, 0) AS outdeg, s.n_step, 1.0 / s.n_step AS pr
FROM nodes n
LEFT JOIN outdeg o USING (node_id)
JOIN sizes s USING (time_step);
