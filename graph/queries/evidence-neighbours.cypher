// Every same-step neighbour of the given transactions, with direction and stage-one score.
// The evidence chain for a flagged transaction is built from these rows. Parameter: $ids.
MATCH (s:Tx)-[:PAYS]->(t:Tx)
WHERE t.node_id IN $ids AND s.time_step = t.time_step
RETURN t.node_id AS node_id, s.node_id AS neighbour, 'in' AS direction, s.score AS score
UNION ALL
MATCH (t:Tx)-[:PAYS]->(o:Tx)
WHERE t.node_id IN $ids AND o.time_step = t.time_step
RETURN t.node_id AS node_id, o.node_id AS neighbour, 'out' AS direction, o.score AS score;
