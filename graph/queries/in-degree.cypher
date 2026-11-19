// In-degree of every transaction in one time step. Parameter: $step.
MATCH (t:Tx)
WHERE t.time_step = $step
OPTIONAL MATCH (s:Tx)-[:PAYS]->(t)
RETURN t.node_id AS node_id, count(s) AS in_degree
ORDER BY node_id;
