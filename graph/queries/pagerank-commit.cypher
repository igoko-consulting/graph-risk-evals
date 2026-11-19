// PageRank within each time step, part 4 of 4: accept the iteration.
MATCH (t:Tx)
SET t.pr = t.pr_next;
