// Distinct transactions within two hops, ignoring direction, excluding the node itself.
// Every node on the path, intermediate included, must be in the step. Parameter: $step.
MATCH (t:Tx)-[:PAYS*1..2 (r, n | WHERE n.time_step = $step)]-(x:Tx)
WHERE t.time_step = $step AND x.time_step = $step AND x.node_id <> t.node_id
RETURN t.node_id AS node_id, count(DISTINCT x.node_id) AS two_hop_size
ORDER BY node_id;
