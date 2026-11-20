-- Engine comparison only; Arm B never reads this. Same result as graph/queries/two-hop-size.cypher.
-- Distinct transactions within two hops, ignoring direction, excluding the node itself. Parameter: $step.
WITH step_nodes AS (
    SELECT node_id FROM nodes WHERE time_step = $step
),
links AS (
    SELECT e.src AS a, e.dst AS b
    FROM edges e
    JOIN step_nodes x ON x.node_id = e.src
    JOIN step_nodes y ON y.node_id = e.dst
),
u AS (
    SELECT a, b FROM links
    UNION ALL
    SELECT b, a FROM links
),
reach AS (
    SELECT a, b AS x FROM u
    UNION
    SELECT u1.a, u2.b FROM u u1 JOIN u u2 ON u2.a = u1.b
)
SELECT a AS node_id, count(DISTINCT x) AS two_hop_size
FROM reach
WHERE x <> a
GROUP BY a
ORDER BY a;
