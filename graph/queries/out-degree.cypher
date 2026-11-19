// Out-degree of every transaction in one time step, counting same-step neighbours only. Parameter: $step.
MATCH (t:Tx)
WHERE t.time_step = $step
OPTIONAL MATCH (t)-[:PAYS]->(o:Tx)
WHERE o.time_step = t.time_step
RETURN t.node_id AS node_id, count(o) AS out_degree
ORDER BY node_id;
