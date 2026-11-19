// PageRank within each time step, part 1 of 4: same-step out-degree, step size, uniform start.
MATCH (t:Tx)
OPTIONAL MATCH (t)-[:PAYS]->(o:Tx)
WHERE o.time_step = t.time_step
WITH t, count(o) AS d
SET t.outdeg = d;

MATCH (t:Tx)
WITH t.time_step AS step, count(*) AS n
MATCH (u:Tx)
WHERE u.time_step = step
SET u.n_step = n;

MATCH (t:Tx)
SET t.pr = 1.0 / t.n_step;
