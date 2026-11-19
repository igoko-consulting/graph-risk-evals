// PageRank within each time step, part 3 of 4: largest change in this iteration.
MATCH (t:Tx)
RETURN max(abs(t.pr_next - t.pr)) AS delta;
