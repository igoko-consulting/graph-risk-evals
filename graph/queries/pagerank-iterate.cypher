// PageRank within each time step, part 2 of 4: one power iteration. Dangling mass is spread
// uniformly over the dangling node's own step. Parameter: $damping.
MATCH (t:Tx)
SET t.dangling = 0.0;

MATCH (d:Tx)
WHERE d.outdeg = 0
WITH d.time_step AS step, sum(d.pr) AS mass
MATCH (u:Tx)
WHERE u.time_step = step
SET u.dangling = mass;

MATCH (t:Tx)
OPTIONAL MATCH (s:Tx)-[:PAYS]->(t)
WHERE s.time_step = t.time_step
WITH t, sum(s.pr / s.outdeg) AS inflow
SET t.pr_next = (1.0 - $damping) / t.n_step + $damping * (coalesce(inflow, 0.0) + t.dangling / t.n_step);
