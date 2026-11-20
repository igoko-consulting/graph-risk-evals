-- Engine comparison only; Arm B never reads this. Same result as graph/queries/out-degree.cypher.
-- Out-degree of every transaction in one time step, counting same-step neighbours only. Parameter: $step.
SELECT t.node_id, count(o.node_id) AS out_degree
FROM nodes t
LEFT JOIN edges e ON e.src = t.node_id
LEFT JOIN nodes o ON o.node_id = e.dst AND o.time_step = t.time_step
WHERE t.time_step = $step
GROUP BY t.node_id
ORDER BY t.node_id;
