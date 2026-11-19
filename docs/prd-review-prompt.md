# PRD review prompt — graph-risk-evals

Paste into a fresh chat with the PRD attached. Run once with each model. Keep both replies verbatim.

---

You are reviewing a PRD for a public, personal engineering lab. I want it challenged, not improved politely.

**Assume the premise is sound.** The author is a senior product leader with production experience in fraud and payments, graph databases and data platforms, but no graph machine learning. The repo exists to close that gap honestly and to test when graph methods stop paying for themselves. Do not spend the review questioning whether the project should exist.

**Hard constraints. A recommendation that breaks one of these is not useful.**

- One person, roughly five days of focused work, alongside a job search.
- Public repository, public data only, no employer data.
- Static: no server, no hosting cost, no API keys at view time.
- Runs on a laptop CPU.
- The deliverable is an argument with evidence, not a product.

**Do two separate passes in one reply.**

**Pass 1: as a sceptical CPTO.** You are deciding whether this is worth the author's week, and whether it would change your view of them as a candidate for a principal product role in regulated fintech.

**Pass 2: as a staff engineer who runs graph and ML systems in production.** You are deciding whether the method is sound and whether the results would survive your scrutiny.

**For each pass, give me exactly this:**

1. **The five most serious problems, ranked.** For each: what is wrong, what it would cost if unaddressed, and the smallest change that fixes it. Not a list of everything that could be better.
2. **What you would cut.** Name at least two things in the PRD that should be removed or deferred, and say what the author gains by cutting them. You must name something; "nothing" is not an acceptable answer.
3. **The one claim most likely to be attacked**, and how you would attack it.
4. **What would make you reject this outright** as evidence of the author's judgement.
5. **What is already good enough and should not be touched.** Be specific, because the author will otherwise over-revise.

**Rules for your answer.**

- Rank by consequence, not by how easy the issue is to spot.
- Do not suggest anything that needs more than half a day unless it replaces something already in scope.
- Do not propose additional datasets, frameworks, infrastructure or features unless you are cutting something to pay for them.
- If the pre-registration, the kill criteria or the equal-tuning requirement are weak, say so first. They carry the repo's credibility.
- Be concrete about numbers. If an operating point, a threshold or a cost assumption is arbitrary, say what it should be instead and why.
- If you think the honest answer is that the result will be uninteresting, say that plainly and say what would make it interesting.

End with a single line: **ship as specified, ship with the changes above, or do not ship.**
