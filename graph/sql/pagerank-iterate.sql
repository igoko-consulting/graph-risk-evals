-- Engine comparison only; Arm B never reads this. Same result as graph/queries/pagerank-iterate.cypher
-- followed by pagerank-commit.cypher. Part 2 of 2: one power iteration, replacing the table.
-- Dangling mass is spread uniformly over the dangling node's own step. Parameter: $damping.
CREATE OR REPLACE TEMP TABLE pr AS
WITH dangling AS (
    SELECT time_step, sum(pr) AS mass FROM pr WHERE outdeg = 0 GROUP BY time_step
),
inflow AS (
    SELECT e.dst AS node_id, sum(s.pr / s.outdeg) AS inflow
    FROM edges e
    JOIN pr s ON s.node_id = e.src
    JOIN pr t ON t.node_id = e.dst
    WHERE s.time_step = t.time_step
    GROUP BY e.dst
)
SELECT p.node_id, p.time_step, p.outdeg, p.n_step,
       (1.0 - $damping) / p.n_step
         + $damping * (coalesce(i.inflow, 0.0) + coalesce(d.mass, 0.0) / p.n_step) AS pr
FROM pr p
LEFT JOIN inflow i USING (node_id)
LEFT JOIN dangling d USING (time_step);
