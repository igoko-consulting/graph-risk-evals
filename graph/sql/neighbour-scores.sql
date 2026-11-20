-- Engine comparison only; Arm B never reads this. Same result as graph/queries/neighbour-scores.cypher.
-- Mean and maximum score over same-step in-neighbours and out-neighbours.
WITH same_step AS (
    SELECT e.src, e.dst
    FROM edges e
    JOIN nodes a ON a.node_id = e.src
    JOIN nodes b ON b.node_id = e.dst
    WHERE a.time_step = b.time_step
),
incoming AS (
    SELECT s.dst AS node_id, avg(sc.score) AS in_mean, max(sc.score) AS in_max
    FROM same_step s JOIN scores sc ON sc.node_id = s.src
    GROUP BY s.dst
),
outgoing AS (
    SELECT s.src AS node_id, avg(sc.score) AS out_mean, max(sc.score) AS out_max
    FROM same_step s JOIN scores sc ON sc.node_id = s.dst
    GROUP BY s.src
)
SELECT n.node_id, i.in_mean, i.in_max, o.out_mean, o.out_max
FROM nodes n
LEFT JOIN incoming i USING (node_id)
LEFT JOIN outgoing o USING (node_id)
ORDER BY n.node_id;
