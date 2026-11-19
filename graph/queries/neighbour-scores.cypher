// Mean and maximum stage-one score over same-step in-neighbours and out-neighbours.
// Nodes with no neighbour on a side return null for that side.
MATCH (t:Tx)
OPTIONAL MATCH (s:Tx)-[:PAYS]->(t)
WHERE s.time_step = t.time_step
WITH t, avg(s.score) AS in_mean, max(s.score) AS in_max
OPTIONAL MATCH (t)-[:PAYS]->(o:Tx)
WHERE o.time_step = t.time_step
RETURN t.node_id AS node_id, in_mean, in_max, avg(o.score) AS out_mean, max(o.score) AS out_max
ORDER BY node_id;
