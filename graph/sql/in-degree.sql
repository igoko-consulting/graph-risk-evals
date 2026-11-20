-- Engine comparison only; Arm B never reads this. Same result as graph/queries/in-degree.cypher.
-- In-degree of every transaction in one time step, counting same-step neighbours only. Parameter: $step.
SELECT t.node_id, count(s.node_id) AS in_degree
FROM nodes t
LEFT JOIN edges e ON e.dst = t.node_id
LEFT JOIN nodes s ON s.node_id = e.src AND s.time_step = t.time_step
WHERE t.time_step = $step
GROUP BY t.node_id
ORDER BY t.node_id;
