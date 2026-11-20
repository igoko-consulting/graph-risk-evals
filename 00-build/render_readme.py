"""Writes the generated blocks of README.md from results/.

The Phase 2 wording and the decision rules were written before any arm had run. Three pieces of Phase 3
wording were added after the Phase 3 headline was seen, to state it accurately rather than to change it:
the by-construction note on H1, the pair intervals behind H3, and finding_phase3. After the label-budget curve
was seen, H4's evidence gained the per-budget differences, its sign convention and the D minus A comparison
the protocol said would be reported alongside, and the H4 limitation gained A's precision at both ends.
The Phase 4 evidence-chain and engine wording was written after a local smoke run whose numbers were
discarded; its one conditional sentence depends on the share of the queue Arm A also queues. The queue-volume block
and the runtime line were written after their results were published; they state no outcome. Outcomes are computed in
evaluate_phase3.py and are not touched here. It is a draft for the author to edit.

Hand-written prose quotes figures through value spans, filled here from results/ like the blocks. The spans and the
generated leakage sentence were added after an audit, with every result already published; they state no outcome.
After the same audit, protocol settings that generated text had typed in (feature count, resamples, shift step,
hypothesis bars, label budgets, queue sizes, label steps) are read from results/, the Phase 3 ranking is labelled as
one of point estimates, the published comparison is cited, and the results notes state the seed-by-seed spread.
"""
import functools
import re

from paths import ENGINE_DOC, MARGIN_NOTES, README, RESULTS
from results_io import read_result

VALUE = re.compile(r"<!-- value:([a-z0-9-]+) -->.*?<!-- end value -->", re.DOTALL)
VALUE_NAMES = (
    "analyst-cost", "analyst-cost-low", "analyst-cost-high", "analyst-cost-basis", "compute-price",
    "trials-per-seed", "seeds", "arm-a-features", "aggregate-features", "resamples", "queue-smallest", "queue-largest",
    "runtime-target-minutes", "k-first-step", "k-last-step", "shift-step",
)
PRIOR_WORK = "Weber et al., 2019"


@functools.cache
def recorded() -> dict:
    """Protocol settings quoted in generated text, read from results/ rather than typed here."""
    periods = read_result("day-one-checks")["data"]["periods"]
    return {
        "shift_step": periods["post_shift_test"][0],
        "known_labels": (periods["training"][0], periods["validation"][1]),
        "arm_a_features": read_result("arm-a-tuning")["data"]["feature_count"],
    }


def arm_label(arm: str) -> str:
    return {"A": f"A, {recorded()['arm_a_features']} local features", "B": "B, plus graph features",
            "D": "D, GraphSAGE on local features"}[arm]


def budget_label(key: str) -> str:
    return f"{int(key)}%"


def pct(x: float) -> str:
    return f"{x:.1%}"


def signed(x: float) -> str:
    return f"{x * 100:+.1f} pts"


def with_ci(value: float, ci: dict) -> str:
    return f"{pct(value)} ({pct(ci['low'])} to {pct(ci['high'])})"


def diff_with_ci(c: dict) -> str:
    ci = c["interval_95"]
    return f"{signed(c['difference'])} ({signed(ci['low'])} to {signed(ci['high'])}), {c['verdict']}"


def results_block(ev: dict) -> str:
    m, ci, cmp = ev["metrics"], ev["intervals"], ev["comparisons_b_minus_a"]
    pre, post = "pre_shift_test", "post_shift_test"
    rows = [
        "| Arm | Precision at k, pre-shift | Precision at k, post-shift | PR-AUC, pre-shift | PR-AUC, post-shift | Cost per true positive |",
        "|---|---|---|---|---|---|",
    ]
    for arm, label in (("A", arm_label("A")), ("B", arm_label("B"))):
        rows.append(
            f"| {label} | {with_ci(m[arm][pre]['precision_at_k_pooled'], ci[pre][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][post]['precision_at_k_pooled'], ci[post][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][pre]['average_precision_pooled'], ci[pre][arm]['ap_pooled'])} "
            f"| {with_ci(m[arm][post]['average_precision_pooled'], ci[post][arm]['ap_pooled'])} | Phase 3 |"
        )
    rows.append(
        f"| B minus A | {diff_with_ci(cmp[pre]['p_at_k'])} | {diff_with_ci(cmp[post]['p_at_k'])} "
        f"| {diff_with_ci(cmp[pre]['ap_pooled'])} | {diff_with_ci(cmp[post]['ap_pooled'])} | |"
    )
    d = "Not built: the kill criterion fired" if ev["kill_criterion"]["fires"] else "Phase 3"
    rows.append(f"| D, GraphSAGE | {d} | | | | |")
    notes = [
        "",
        f"k = {ev['k']} alerts per time step (`results/k.json`). PR-AUC is average precision pooled over labelled "
        f"transactions in the period. Brackets are 95% paired bootstrap intervals, {ev['bootstrap']['resamples']:,} "
        "resamples stratified by time step. A difference is called only when its interval excludes zero. Labelled transactions only; unlabelled is "
        "not licit. Source: `results/evaluation-arms-a-b.json`.",
        "",
        "![Precision at k by test step](site/charts/precision-at-k-arms-a-b.svg)",
        "",
        finding(ev),
    ]
    return "\n".join(rows + notes)


def finding(ev: dict) -> str:
    cmp, m, h3 = ev["comparisons_b_minus_a"], ev["metrics"], ev["h3_relative_fall_in_average_precision"]
    pre, post = cmp["pre_shift_test"]["p_at_k"], cmp["post_shift_test"]["p_at_k"]
    k = ev["k"]
    if ev["kill_criterion"]["fires"]:
        headline = (
            f"Adding graph features did not lift precision at k outside the noise band before the regime shift: "
            f"B minus A was {diff_with_ci(pre)}. As pre-registered, Arm D is not built. On this data, the graph "
            f"features added no lift that this test can detect at a {k}-alert queue. That is not proof that no "
            "relational signal exists; it is the absence of a measurable gain over a tuned local-feature model."
        )
        if pre["interval_95"]["high"] < 0:
            headline = (
                f"Adding graph features lowered precision at k before the regime shift: B minus A was "
                f"{diff_with_ci(pre)}. As pre-registered, Arm D is not built."
            )
    else:
        headline = (
            f"Adding graph features lifted precision at k before the regime shift: B minus A was {diff_with_ci(pre)}. "
            "Arm D is built in Phase 3 to test whether learned message passing adds more than hand-built graph features."
        )
    shift = (
        f"After the shift at step {recorded()['shift_step']}, precision at k was "
        f"{pct(m['A']['post_shift_test']['precision_at_k_pooled'])} for A and {pct(m['B']['post_shift_test']['precision_at_k_pooled'])} for B; B minus A {diff_with_ci(post)}. "
        f"There are fewer illicit labels than alerts after the shift, so no model could exceed "
        f"{pct(m['A']['post_shift_test']['precision_at_k_ceiling'])} there (before the shift the ceiling is "
        f"{pct(m['A']['pre_shift_test']['precision_at_k_ceiling'])}). "
        f"Mean per-step PR-AUC fell by {pct(h3['A']['relative_fall'])} for A and {pct(h3['B']['relative_fall'])} for B "
        "from the pre-shift to the post-shift period. H3 is assessed across all arms in Phase 3."
    )
    limits = (
        "This is one Bitcoin transaction graph with anonymised features. It says nothing directly about account-level "
        "payments graphs. The post-shift period has few illicit labels, which caps precision at k there."
    )
    return f"**Phase 2 finding (draft for the author to edit).** {headline} {shift} {limits}"


def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!-- generated:{name} [^\n]*-->\n).*?(\n<!-- end generated:{name} -->)", re.DOTALL
    )
    if not pattern.search(text):
        raise SystemExit(f"README.md has no generated:{name} block")
    return pattern.sub(lambda mt: mt.group(1) + content + mt.group(2), text)


def sentence(s: str) -> str:
    return s[:1].upper() + s[1:]


def share_text(x: float) -> str:
    return "less than 0.1%" if x < 0.001 else f"at most {pct(x)}"


def euro(x) -> str:
    return "n/a" if x is None else f"€{x:,.0f}" if x >= 100 else f"€{x:,.2f}"


def cost_cell(cost: dict, arm: str) -> str:
    c = cost["by_arm"][arm]["pre_shift_test"]["cost_per_true_positive_eur"]
    return f"{euro(c['central'])} modelled; {euro(c['low'])} to {euro(c['high'])} across the analyst-cost range"


def outside(ci: dict) -> bool:
    return ci["low"] > 0 or ci["high"] < 0


def h1_by_construction(h1: dict) -> bool:
    """(B - A) / (max(B, D) - A) is exactly 1 whenever B >= D, so an interval of [1, 1] means B beat D in every resample."""
    ci = h1["interval_95"]
    return ci is not None and ci["low"] == 1.0 and ci["high"] == 1.0


def finding_phase3(ev: dict) -> str:
    m, cmp, k = ev["metrics"], ev["comparisons"], ev["k"]
    pre, post = "pre_shift_test", "post_shift_test"
    p = {a: m[a][pre]["precision_at_k_pooled"] for a in ("A", "B", "D")}
    ranked = sorted(p, key=lambda a: -p[a])
    ba, db, da = (cmp[name][pre]["p_at_k"] for name in ("B minus A", "D minus B", "D minus A"))
    parts = [
        f"Before the regime shift, on point estimates, the arms ranked {ranked[0]}, then {ranked[1]}, then {ranked[2]} "
        "on precision at k. "
        f"B minus A was {diff_with_ci(ba)}; D minus B {diff_with_ci(db)}; D minus A {diff_with_ci(da)}."
    ]
    if da["interval_95"]["high"] < 0:
        parts.append(
            "Given A's local features plus the transaction graph, the GNN still ranked below A. "
            f"That matches the direction of the published comparison ({PRIOR_WORK})."
        )
    u = {a: m[a][pre]["unlabelled_share_of_top_k_all_nodes"] for a in ("A", "B", "D")}
    parts.append(
        f"Ranked over every transaction in a step, labelled or not, unlabelled transactions would fill {pct(u['D'])} of "
        f"D's top {k} before the shift, against {pct(u['A'])} for A and {pct(u['B'])} for B."
        + (" Precision at k counts labelled transactions only, so it describes less of D's real queue than of A's or B's."
           if u["D"] > max(u["A"], u["B"]) else "")
    )
    q = {a: m[a][post]["precision_at_k_pooled"] for a in ("A", "B", "D")}
    parts.append(
        f"After the shift at step {recorded()['shift_step']}, precision at k was {pct(q['A'])} for A, {pct(q['B'])} for B "
        f"and {pct(q['D'])} for D, "
        f"against a ceiling of {pct(m['A'][post]['precision_at_k_ceiling'])} set by the number of illicit labels."
    )
    parts.append(
        "This is one Bitcoin transaction graph with anonymised features. It says nothing directly about account-level "
        "payments graphs. Arm D's search space was fixed before any result and was not widened afterwards."
    )
    return "**Phase 3 finding (draft for the author to edit).** " + " ".join(parts)


def results_block_phase3(ev: dict, cost: dict) -> str:
    m, ci, cmp = ev["metrics"], ev["intervals"], ev["comparisons"]
    pre, post = "pre_shift_test", "post_shift_test"
    rows = [
        "| Arm | Precision at k, pre-shift | Precision at k, post-shift | PR-AUC, pre-shift | PR-AUC, post-shift | Cost per true positive, pre-shift |",
        "|---|---|---|---|---|---|",
    ]
    for arm in ("A", "B", "D"):
        rows.append(
            f"| {arm_label(arm)} | {with_ci(m[arm][pre]['precision_at_k_pooled'], ci[pre][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][post]['precision_at_k_pooled'], ci[post][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][pre]['average_precision_pooled'], ci[pre][arm]['ap_pooled'])} "
            f"| {with_ci(m[arm][post]['average_precision_pooled'], ci[post][arm]['ap_pooled'])} | {cost_cell(cost, arm)} |"
        )
    for pair in ("B minus A", "D minus B", "D minus A"):
        c = cmp[pair]
        rows.append(f"| {pair} | {diff_with_ci(c[pre]['p_at_k'])} | {diff_with_ci(c[post]['p_at_k'])} "
                    f"| {diff_with_ci(c[pre]['ap_pooled'])} | {diff_with_ci(c[post]['ap_pooled'])} | |")
    a = cost["assumptions"]["analyst_cost_per_alert_eur"]
    seeds = ev["per_seed"]
    by_seed = [b[pre]["precision_at_k_pooled"] - a_[pre]["precision_at_k_pooled"] for a_, b in zip(seeds["A"], seeds["B"])]
    notes = [
        "",
        f"k = {ev['k']} alerts per time step (`results/k.json`). PR-AUC is average precision pooled over labelled "
        f"transactions in the period. Brackets on metrics are 95% paired bootstrap intervals, "
        f"{ev['bootstrap']['resamples']:,} resamples stratified by time step; a difference is called only when its "
        "interval excludes zero. Each arm's scores are the mean of its "
        f"{len(seeds['A'])} seeds' models, each tuned on its own; a deployment would run one model. The intervals hold "
        "those scores fixed and treat transactions within a step as independent, so they leave out retraining with "
        "other seeds and may be too narrow where linked transactions move together. Seed by seed, B minus A on "
        f"pre-shift precision at k ran from {signed(min(by_seed))} to {signed(max(by_seed))}. Labelled transactions only; "
        f"unlabelled is not licit. **Cost is modelled, not measured:** analyst cost of €{a['central']:.0f} per alert, "
        f"with a range of €{a['low']:.2f} to €{a['high']:.2f}, plus measured tuning time priced at "
        f"€{cost['assumptions']['compute_eur_per_vcpu_hour']:.2f} per vCPU-hour. The cost range is that assumption's "
        "range, not a confidence interval. Sources: `results/evaluation-phase-3.json`, `results/cost-per-true-positive.json`.",
        "",
        "![Precision at k by test step, all arms](site/charts/precision-at-k-all-arms.svg)",
    ]
    return "\n".join(rows + notes)


def hypotheses_block(ev: dict, budget: dict | None) -> str:
    h = ev["hypotheses"]
    h1, h2, h3 = h["H1"], h["H2"], h["H3"]
    ap = {a: ev["metrics"][a]["pre_shift_test"]["average_precision_pooled"] for a in ("A", "B", "D")}
    h1_ev = ("Undefined" if h1["interval_95"] is None else
             f"{h1['point']:.2f} ({h1['interval_95']['low']:.2f} to {h1['interval_95']['high']:.2f})")
    h1_ev = f"Share of lift, PR-AUC pre-shift: {h1_ev}. Supported needs a majority, as the hypothesis states."
    h1_outcome = sentence(h1["outcome"])
    if h1_by_construction(h1):
        h1_outcome += ", by construction"
        h1_ev += " The ratio is 1 whenever B beats D, as it did in every resample, so the available lift is B's own."
        if ap["D"] < ap["A"]:
            h1_ev += (f" D's PR-AUC was also below A's ({pct(ap['D'])} against {pct(ap['A'])}), so the GNN added no "
                      "lift for graph features to capture.")
    pairs = "; ".join(
        f"{name} {signed(v['difference'])} ({signed(v['interval_95']['low'])} to {signed(v['interval_95']['high'])}), "
        + ("outside" if outside(v["interval_95"]) else "within") + " the noise band"
        for name, v in h3["pairs"].items()
    )
    h3_ev = ("Relative fall in mean per-step PR-AUC: " + "; ".join(f"{a} fell {pct(v)}" for a, v in h3["relative_fall"].items())
             + f". Differences in fall, positive where the more complex arm fell more: {pairs}. "
             "Supported needs all three above zero.")
    rows = [
        "| Hypothesis | Outcome | Evidence |",
        "|---|---|---|",
        f"| **H1.** Graph-derived features capture the majority of available lift | {h1_outcome} | {h1_ev} |",
        f"| **H2.** The GNN does not justify its cost | {sentence(h2['outcome'])} "
        f"| D minus B, precision at k pre-shift: {diff_with_ci(ev['comparisons']['D minus B']['pre_shift_test']['p_at_k'])}. "
        f"{sentence(h2['definition'])}. |",
        f"| **H3.** Simpler arms degrade less after the regime shift | {sentence(h3['outcome'])} "
        f"| {h3_ev} |",
    ]
    if budget:
        h4 = budget["H4"]
        b, d = h4["B minus A"], h4["D minus A, reported alongside"]
        lo, hi = min(budget["curve"]), max(budget["curve"])
        pre_lo, pre_hi = budget["curve"][lo]["pre_shift_test"], budget["curve"][hi]["pre_shift_test"]
        h4_ev = (f"B minus A, precision at k pre-shift: at {budget_label(lo)} of training labels, "
                 f"{diff_with_ci(pre_lo['B minus A'])}; at {budget_label(hi)}, {diff_with_ci(pre_hi['B minus A'])}. "
                 f"Change from {budget_label(hi)} to {budget_label(lo)}, positive if the advantage "
                 f"widened: {signed(b['widening'])} ({signed(b['interval_95']['low'])} to {signed(b['interval_95']['high'])}), "
                 + ("outside" if outside(b["interval_95"]) else "within") + " the noise band. "
                 f"Reported alongside, D minus A changed by {signed(d['widening'])} "
                 f"({signed(d['interval_95']['low'])} to {signed(d['interval_95']['high'])}), {d['outcome']}")
        if d["interval_95"]["high"] < 0:
            h4_ev += ": D fell further behind A as labels shrank"
        rows.append(
            f"| **H4.** The graph-feature advantage widens as labels get scarcer | {sentence(h4['outcome'])} | {h4_ev}. |"
        )
    else:
        rows.append("| **H4.** The graph-feature advantage widens as labels get scarcer | Pending | Label-budget curve still running |")
    rows += ["", "Outcomes follow the rules fixed in `change_log.md` before Arm D or any label budget ran. Source: "
             "`results/evaluation-phase-3.json`" + (", `results/label-budget-curve.json`." if budget else ".")]
    if budget:
        rows += ["", "![Label-budget curve](site/charts/label-budget-curve.svg)"]
    return "\n".join(rows)


def decision_block(ev: dict, cost: dict) -> str:
    cmp = ev["comparisons"]
    pre = "pre_shift_test"
    ba, db, da = (cmp[p][pre]["p_at_k"] for p in ("B minus A", "D minus B", "D minus A"))
    c = {arm: cost["by_arm"][arm][pre]["cost_per_true_positive_eur"]["central"] for arm in ("A", "B", "D")}
    b_beats_a = ba["interval_95"]["low"] > 0
    cheaper_b = c["B"] is not None and c["A"] is not None and c["B"] < c["A"]
    h2_rejected = ev["hypotheses"]["H2"]["outcome"].startswith("rejected")
    all_similar = all(x["interval_95"]["low"] <= 0 <= x["interval_95"]["high"] for x in (ba, db, da))
    yes = lambda flag: "**Yes**" if flag else "No"
    rows = [
        "| Finding | Product decision | Applies here | Evidence |",
        "|---|---|---|---|",
        f"| Tabular performs comparably to graph features | Do not introduce graph complexity | {yes(not b_beats_a)} "
        f"| B minus A, precision at k pre-shift: {diff_with_ci(ba)} |",
        f"| Graph features improve detection economics | Invest in graph-derived features, not graph models "
        f"| {yes(b_beats_a and cheaper_b and not h2_rejected)} | B beats A outside the noise band: {'yes' if b_beats_a else 'no'}. "
        f"Modelled cost per true positive, pre-shift: A {euro(c['A'])}, B {euro(c['B'])} |",
        f"| The GNN adds material value beyond graph features | Investigate whether the operational burden is justified "
        f"| {yes(h2_rejected)} | D minus B: {diff_with_ci(db)}. H2 is "
        f"{ev['hypotheses']['H2']['definition'][:1].lower() + ev['hypotheses']['H2']['definition'][1:]} |",
        f"| All arms perform similarly | Do not invest further on the basis of this dataset | {yes(all_similar)} "
        f"| Every pairwise interval on pre-shift precision at k includes zero: {'yes' if all_similar else 'no'} |",
        "",
        "_Draft for the author to edit. Which row applies is decided by code from `results/`, using rules written before "
        "Arm D ran. The product decisions are the PRD's; they are about this dataset and do not transfer to payments "
        "without the account-level data this dataset lacks._",
    ]
    return "\n".join(rows)


def leakage_sentence(gate: dict) -> str:
    dropped = gate["dropped_features"]
    kept = [v for name, r in gate["per_feature"].items() if name not in dropped for key, v in r.items() if key != "passed"]
    moved = "moved" if max(kept, default=0.0) == 0 else f"moved by more than {gate['tolerance']:g}"
    tests = "the future-edge, label-shuffle or own-label tests"
    if not dropped:
        return f"No feature {moved} under {tests} (`results/leakage-tests.json`)."
    names = ", ".join(f"`{n}`" for n in dropped)
    return (f"{names} moved under {tests} and {'was' if len(dropped) == 1 else 'were'} dropped from Arm B, as "
            f"pre-registered. No other feature {moved} (`results/leakage-tests.json`).")


def limitations_block(ev: dict, cost: dict, budget: dict | None, gate: dict) -> str:
    cmp, h = ev["comparisons"], ev["hypotheses"]
    pre = "pre_shift_test"
    ba, db, da = (cmp[name][pre]["p_at_k"] for name in ("B minus A", "D minus B", "D minus A"))
    share = max(cost["by_arm"][a][pre]["compute_share_of_cost"] for a in ("A", "B", "D"))
    demonstrated = [
        f"On this dataset, before the regime shift, adding graph features to a tuned local-feature model changed "
        f"precision at k by {diff_with_ci(ba)}.",
        f"A two-layer GraphSAGE on the same local features, against graph features: D minus B {diff_with_ci(db)}. "
        f"Against the local-feature model alone: D minus A {diff_with_ci(da)}.",
        f"After the regime shift at step {recorded()['shift_step']}, mean per-step PR-AUC fell by "
        + ", ".join(f"{pct(v)} for {a}" for a, v in h["H3"]["relative_fall"].items()) + ".",
        leakage_sentence(gate),
    ]
    suggested = [
        f"H1, whether hand-built graph features capture most of the available lift: {h['H1']['outcome']}"
        + (", but only by construction, because B beat D in every resample. It says nothing about how much a "
           "stronger GNN might add." if h1_by_construction(h["H1"]) else "."),
        f"Compute is {share_text(share)} of modelled cost per true positive for every arm. Analyst time dominates, "
        "so the decision turns on alert quality, not on compute.",
    ]
    if budget:
        lo, hi = min(budget["curve"]), max(budget["curve"])
        a_lo = budget["curve"][lo]["pre_shift_test"]["A"]["precision_at_k_pooled"]
        a_hi = budget["curve"][hi]["pre_shift_test"]["A"]["precision_at_k_pooled"]
        suggested.append(f"H4, whether the graph-feature advantage widens as labels get scarcer: {budget['H4']['outcome']}. "
                         "Validation labels were kept in full at every budget, so small-budget results are somewhat optimistic. "
                         f"A's precision at k was {pct(a_lo)} at {budget_label(lo)} of training labels and {pct(a_hi)} "
                         f"at {budget_label(hi)}.")
    return ("**What this demonstrates.** _Draft for the author to edit._\n\n" + "\n".join(f"- {x}" for x in demonstrated)
            + "\n\n**What this suggests.**\n\n" + "\n".join(f"- {x}" for x in suggested))


def evidence_block(e: dict) -> str:
    k = e["k"]
    pre = e["by_period"]["pre_shift_test"]
    cols = (pre["all_flagged"], pre["flagged_illicit"], pre["flagged_licit"])
    share = lambda x: "n/a" if x is None else pct(x)
    rows = [
        "| Before the shift | All queued | Queued and illicit | Queued and licit |",
        "|---|---|---|---|",
        "| Transactions queued by Arm B | " + " | ".join(str(c["flagged"]) for c in cols) + " |",
        "| With a chain: at least one same-step link | " + " | ".join(share(c["with_chain"]) for c in cols) + " |",
        "| With a two-hop chain | " + " | ".join(share(c["with_two_hop_chain"]) for c in cols) + " |",
        f"| Strongest link also in Arm A's top {k} for its step | "
        + " | ".join(share(c["strongest_link_in_stage_one_top_k"]) for c in cols) + " |",
        "| Also queued by Arm A, without graph features | " + " | ".join(share(c["also_queued_by_arm_a"]) for c in cols) + " |",
        "| Median transactions within two hops | " + " | ".join(f"{c['median_two_hop_size']:.0f}" for c in cols) + " |",
    ]
    t, known, d = e["truth_check"], e["links_to_a_known_label"]["count"], e["arm_d"]
    a_share = cols[0]["also_queued_by_arm_a"]
    known_steps = "steps {} to {}".format(*recorded()["known_labels"])
    notes = [
        f"**Draft for the author to edit.** Every chain is built with `graph/queries/`, and all {t['facts_checked']:,} "
        f"facts in them were recomputed in SQL from the columnar store; "
        + ("none disagreed. " if t["facts_false"] == 0 else f"{t['facts_false']} disagreed. ")
        + (f"{pct(a_share)} of the queue would have been queued by Arm A without any graph feature, so for most queued "
           "transactions the chain is context rather than the reason they were queued. " if a_share > 0.5 else "")
        + "A chain can never cite a counterparty whose label was known at scoring time: edges never cross time steps, "
        + (f"and there are no links from a queued transaction to {known_steps}. " if known == 0 else
           f"and {known} links reach {known_steps}. ")
        + "On payments data the strongest evidence is often a link to a confirmed bad account; this dataset cannot show one.",
        "",
        f"**Arm D cannot produce a chain.** Its score depends on a median of {d['receptive_field_median_transactions']:.0f} "
        "transactions within two hops, through learned weights. The traversal can list them but not say which mattered, "
        "and a post-hoc explainer would add an approximation, not a fact about the graph.",
        "",
        f"Whether a chain is sufficient and actionable needs a human. A seeded sample of {e['review']['sample']} sits in "
        f"`{e['review']['file']}` for the author to score: true, sufficient, actionable. Not yet scored. "
        "Source: `results/evidence-chains.json`.",
    ]
    return "\n".join(rows + [""] + notes)


def runtime_block(rt: dict) -> str:
    m = rt["machine"]
    return (f"The last clean-clone run of `make all` took {rt['elapsed_seconds'] / 3600:.1f} hours on an {m['cpu']} with "
            f"{m['performance_cores']} performance cores, against the specification's target of "
            f"{rt['specification_target_minutes']} minutes. The target gave way to full tuning: every arm is tuned in "
            "full at every label budget, and that stage dominates. The figure includes install and download, which "
            "depend on the network. Source: `results/pipeline-runtime.json`.")


QUEUE_TABLE_SIZES = (50, 200, 500)


def queue_block(ev: dict) -> str:
    k = ev["k"]
    periods = (("pre_shift_test", "Before the shift"), ("post_shift_test", "After the shift"))
    below, above = [q for q in QUEUE_TABLE_SIZES if q < k], [q for q in QUEUE_TABLE_SIZES if q > k]
    grid = [r["queue_per_step"] for r in ev["metrics"]["A"]["pre_shift_test"]["queue_curve"]]
    rows = [
        "| Arm, period | " + " | ".join([f"{q} per step" for q in below] + [f"k = {k} per step, pre-committed"]
                                       + [f"{q} per step" for q in above]) + " |",
        "|---" * (len(QUEUE_TABLE_SIZES) + 2) + "|",
    ]
    volumes = []
    for period, label in periods:
        steps = len(ev["metrics"]["A"][period]["per_step"])
        volumes.append(f"{k * steps:,} alerts {label.lower()} ({steps} steps)")
        for arm in ("A", "B", "D"):
            m = ev["metrics"][arm][period]
            curve = {r["queue_per_step"]: r for r in m["queue_curve"]}
            cell = lambda p, r: f"{pct(p)} / {pct(r)}"
            at = {q: cell(curve[q]["precision"], curve[q]["recall"]) for q in QUEUE_TABLE_SIZES}
            rows.append(f"| {arm}, {label.lower()} | " + " | ".join(
                [at[q] for q in below] + [cell(m["precision_at_k_pooled"], m["recall_at_k_pooled"])] + [at[q] for q in above])
                + " |")
    notes = [
        "",
        "Each cell is precision / recall, pooled over the period, from seed-averaged scores. "
        f"At the pre-committed k = {k} per step the queue holds {' and '.join(volumes)}.",
        "",
        "**What this does not establish.** Which arm is better at any queue size other than k: the curve has no "
        f"intervals, and arms are compared only at k = {k}, on paired resamples (H2 to H4 above). Nor does it choose a "
        "queue size: k was fixed from the training and validation steps before any test step was read. The other sizes "
        "are round numbers for reading the table, picked after the curve was published, and decide nothing. Labelled "
        "transactions only; unlabelled is not licit. "
        f"Every {grid[1] - grid[0]} alerts from {min(grid)} to {max(grid)} is in `results/evaluation-phase-3.json`.",
        "",
        "![Precision and recall across queue sizes](site/charts/queue-volume-across-operating-points.svg)",
    ]
    return "\n".join(rows + notes)


WORKLOAD_NAMES = {"degree": "Degree", "two_hop": "Two-hop size", "neighbour_scores": "Neighbour scores",
                  "pagerank": "PageRank"}


def engine_block(e: dict) -> str:
    w, cfg, m, g = e["workloads"], e["configuration"], e["machine"], e["graph"]
    rows = [
        "| Workload | What it does | LadybugDB, median (first run) | DuckDB, median (first run) | LadybugDB time ÷ DuckDB time | Largest output difference |",
        "|---|---|---|---|---|---|",
    ]
    for name, x in w.items():
        s = x["seconds"]
        rows.append(
            f"| {WORKLOAD_NAMES.get(name, name)} | {x['description']} "
            f"| {s['ladybug']['median_of_repeats']:.2f}s ({s['ladybug']['first_run']:.2f}s) "
            f"| {s['duckdb']['median_of_repeats']:.2f}s ({s['duckdb']['first_run']:.2f}s) "
            f"| {x['ratio_ladybug_to_duckdb']:.1f} | {x['max_difference_between_engines']:.1g} |"
        )
    engines = cfg["engines"]
    memory = f"{int(m['memory_bytes']) / 2**30:.0f} GB" if m.get("memory_bytes") else "memory not recorded"
    notes = [
        "",
        f"{g['nodes']:,} transactions, {g['edges']:,} edges, {g['time_steps']} time steps. {engines['ladybug']['name']} "
        f"{engines['ladybug']['version']}; {engines['duckdb']['name']} {engines['duckdb']['version']}. "
        f"{cfg['threads']} threads in both, {cfg['repeats']} repeats after a first run, engine order alternated between "
        f"repeats. {cfg['storage']}. {cfg['result_format']}. Machine: {m['cpu']}, {m['performance_cores']} performance "
        f"cores, {memory}, {m['platform']}, Python {m['python']}.",
        "",
        "**Confounds.**",
        "",
        *[f"- {c}" for c in e["confounds"]],
        "",
        f"**What this does not establish.** {e['does_not_establish']}",
        "",
        "Source: `results/engine-comparison.json`.",
    ]
    return "\n".join(rows + notes)


def money(x: float) -> str:
    return f"€{x:,.0f}" if x == int(x) else f"€{x:,.2f}"


def is_result(name: str) -> bool:
    return (RESULTS / f"{name}.json").is_file()


def prose_values() -> dict:
    v = {}
    if is_result("cost-per-true-positive"):
        a = read_result("cost-per-true-positive")["data"]["assumptions"]
        analyst = a["analyst_cost_per_alert_eur"]
        v |= {"analyst-cost": money(analyst["central"]), "analyst-cost-low": money(analyst["low"]),
              "analyst-cost-high": money(analyst["high"]), "analyst-cost-basis": a["basis"],
              "compute-price": money(a["compute_eur_per_vcpu_hour"])}
    if all(is_result(f"arm-{arm}-tuning") for arm in "abd"):
        tuning = [read_result(f"arm-{arm}-tuning")["data"] for arm in "abd"]
        trials, seeds = {t["trials_per_seed"] for t in tuning}, {len(t["seeds"]) for t in tuning}
        if len(trials) != 1 or len(seeds) != 1:
            raise SystemExit("Arms A, B and D were not tuned with the same trials and seeds, as the README says they were")
        v |= {"trials-per-seed": str(trials.pop()), "seeds": str(seeds.pop()),
              "arm-a-features": str(tuning[0]["feature_count"])}
    if is_result("day-one-checks"):
        checks = read_result("day-one-checks")["data"]
        v |= {"aggregate-features": str(checks["feature_groups_used"]["aggregate"]),
              "shift-step": str(checks["periods"]["post_shift_test"][0])}
    if is_result("k"):
        first, last = read_result("k")["data"]["steps"]
        v |= {"k-first-step": str(first), "k-last-step": str(last)}
    if is_result("evaluation-phase-3"):
        ev = read_result("evaluation-phase-3")["data"]
        sizes = [r["queue_per_step"] for r in ev["metrics"]["A"]["pre_shift_test"]["queue_curve"]]
        v |= {"resamples": f"{ev['bootstrap']['resamples']:,}", "queue-smallest": str(min(sizes)),
              "queue-largest": str(max(sizes))}
    if is_result("pipeline-runtime"):
        v["runtime-target-minutes"] = str(read_result("pipeline-runtime")["data"]["specification_target_minutes"])
    return v


def fill_values(text: str, values: dict, doc: str) -> str:
    """A span whose source result does not exist yet keeps its last generated value."""
    def fill(m: re.Match) -> str:
        name = m.group(1)
        if name not in VALUE_NAMES:
            raise SystemExit(f"{doc} asks for an unknown value {name!r}")
        return f"<!-- value:{name} -->{values[name]}<!-- end value -->" if name in values else m.group(0)
    return VALUE.sub(fill, text)


def main() -> None:
    values = prose_values()
    text = fill_values(README.read_text(), values, "README.md")
    if (RESULTS / "evidence-chains.json").is_file():
        text = replace_block(text, "evidence-chains", evidence_block(read_result("evidence-chains")["data"]))
    if (RESULTS / "engine-comparison.json").is_file() and ENGINE_DOC.is_file():
        ENGINE_DOC.write_text(replace_block(ENGINE_DOC.read_text(), "engine-comparison",
                                            engine_block(read_result("engine-comparison")["data"])))
    phase3 = (RESULTS / "evaluation-phase-3.json").is_file() and (RESULTS / "cost-per-true-positive.json").is_file()
    if phase3:
        ev = read_result("evaluation-phase-3")["data"]
        cost = read_result("cost-per-true-positive")["data"]
        budget = read_result("label-budget-curve")["data"] if (RESULTS / "label-budget-curve.json").is_file() else None
        text = replace_block(text, "results", results_block_phase3(ev, cost) + "\n\n" + finding_phase3(ev))
        text = replace_block(text, "hypotheses", hypotheses_block(ev, budget))
        text = replace_block(text, "queue-volume", queue_block(ev))
        text = replace_block(text, "decision-matrix", decision_block(ev, cost))
        text = replace_block(text, "limitations", limitations_block(ev, cost, budget, read_result("leakage-tests")["data"]))
    elif (RESULTS / "evaluation-arms-a-b.json").is_file():
        text = replace_block(text, "results", results_block(read_result("evaluation-arms-a-b")["data"]))
    if (RESULTS / "pipeline-runtime.json").is_file():
        text = replace_block(text, "runtime", runtime_block(read_result("pipeline-runtime")["data"]))
    README.write_text(text)
    MARGIN_NOTES.write_text(fill_values(MARGIN_NOTES.read_text(), values, "03-the-margin/NOTES.md"))
    print("README.md generated blocks and quoted values updated")


if __name__ == "__main__":
    main()
