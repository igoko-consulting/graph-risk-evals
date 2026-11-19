"""Writes the generated blocks of README.md from results/.

Every branch of wording below was written before any arm had run, so the text that appears is
selected by the result, not composed after seeing it. It is a draft for the author to edit.
"""
import re

from paths import RESULTS, ROOT
from results_io import read_result

README = ROOT / "README.md"


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
    for arm, label in (("A", "A, 93 local features"), ("B", "B, plus graph features")):
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
        "transactions in the period. Brackets are 95% paired bootstrap intervals, 1,000 resamples stratified by time "
        "step. A difference is called only when its interval excludes zero. Labelled transactions only; unlabelled is "
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
        f"After the shift at step 43, precision at k was {pct(m['A']['post_shift_test']['precision_at_k_pooled'])} for A "
        f"and {pct(m['B']['post_shift_test']['precision_at_k_pooled'])} for B; B minus A {diff_with_ci(post)}. "
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


ARM_LABELS = {"A": "A, 93 local features", "B": "B, plus graph features", "D": "D, GraphSAGE on local features"}


def sentence(s: str) -> str:
    return s[:1].upper() + s[1:]


def share_text(x: float) -> str:
    return "less than 0.1%" if x < 0.001 else f"at most {pct(x)}"


def euro(x) -> str:
    return "n/a" if x is None else f"€{x:,.0f}" if x >= 100 else f"€{x:,.2f}"


def cost_cell(cost: dict, arm: str) -> str:
    c = cost["by_arm"][arm]["pre_shift_test"]["cost_per_true_positive_eur"]
    return f"{euro(c['central'])} ({euro(c['low'])} to {euro(c['high'])}), modelled"


def results_block_phase3(ev: dict, cost: dict) -> str:
    m, ci, cmp = ev["metrics"], ev["intervals"], ev["comparisons"]
    pre, post = "pre_shift_test", "post_shift_test"
    rows = [
        "| Arm | Precision at k, pre-shift | Precision at k, post-shift | PR-AUC, pre-shift | PR-AUC, post-shift | Cost per true positive, pre-shift |",
        "|---|---|---|---|---|---|",
    ]
    for arm in ("A", "B", "D"):
        rows.append(
            f"| {ARM_LABELS[arm]} | {with_ci(m[arm][pre]['precision_at_k_pooled'], ci[pre][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][post]['precision_at_k_pooled'], ci[post][arm]['p_at_k'])} "
            f"| {with_ci(m[arm][pre]['average_precision_pooled'], ci[pre][arm]['ap_pooled'])} "
            f"| {with_ci(m[arm][post]['average_precision_pooled'], ci[post][arm]['ap_pooled'])} | {cost_cell(cost, arm)} |"
        )
    for pair in ("B minus A", "D minus B", "D minus A"):
        c = cmp[pair]
        rows.append(f"| {pair} | {diff_with_ci(c[pre]['p_at_k'])} | {diff_with_ci(c[post]['p_at_k'])} "
                    f"| {diff_with_ci(c[pre]['ap_pooled'])} | {diff_with_ci(c[post]['ap_pooled'])} | |")
    a = cost["assumptions"]["analyst_cost_per_alert_eur"]
    notes = [
        "",
        f"k = {ev['k']} alerts per time step (`results/k.json`). PR-AUC is average precision pooled over labelled "
        "transactions in the period. Brackets on metrics are 95% paired bootstrap intervals, 1,000 resamples stratified "
        "by time step; a difference is called only when its interval excludes zero. Labelled transactions only; "
        f"unlabelled is not licit. **Cost is modelled, not measured:** analyst cost of €{a['central']:.0f} per alert, "
        f"bracketed at €{a['low']:.2f} to €{a['high']:.2f}, plus compute at true scale. Sources: "
        "`results/evaluation-phase-3.json`, `results/cost-per-true-positive.json`.",
        "",
        "![Precision at k by test step, all arms](site/charts/precision-at-k-all-arms.svg)",
    ]
    return "\n".join(rows + notes)


def hypotheses_block(ev: dict, budget: dict | None) -> str:
    h = ev["hypotheses"]
    h1, h2, h3 = h["H1"], h["H2"], h["H3"]
    h1_ev = ("Undefined" if h1["interval_95"] is None else
             f"{h1['point']:.2f} ({h1['interval_95']['low']:.2f} to {h1['interval_95']['high']:.2f})")
    h3_ev = "; ".join(f"{a} fell {pct(v)}" for a, v in h3["relative_fall"].items())
    rows = [
        "| Hypothesis | Outcome | Evidence |",
        "|---|---|---|",
        f"| **H1.** Graph-derived features capture the majority of available lift | {sentence(h1['outcome'])} "
        f"| Share of lift, PR-AUC pre-shift: {h1_ev}. Threshold 0.5. |",
        f"| **H2.** The GNN does not justify its cost | {sentence(h2['outcome'])} "
        f"| D minus B, precision at k pre-shift: {diff_with_ci(ev['comparisons']['D minus B']['pre_shift_test']['p_at_k'])}. "
        "Bar: +5.0 pts and excluding zero. |",
        f"| **H3.** Simpler arms degrade less after the regime shift | {sentence(h3['outcome'])} "
        f"| Relative fall in mean per-step PR-AUC: {h3_ev}. |",
    ]
    if budget:
        h4 = budget["H4"]
        b = h4["B minus A"]
        rows.append(
            f"| **H4.** The graph-feature advantage widens as labels get scarcer | {sentence(h4['outcome'])} "
            f"| Change in B minus A from 100% to 5% of labels: {signed(b['widening'])} "
            f"({signed(b['interval_95']['low'])} to {signed(b['interval_95']['high'])}). |"
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
        f"| {yes(h2_rejected)} | D minus B: {diff_with_ci(db)}. H2 bar: +5.0 pts and excluding zero |",
        f"| All arms perform similarly | Do not invest further on the basis of this dataset | {yes(all_similar)} "
        f"| Every pairwise interval on pre-shift precision at k includes zero: {'yes' if all_similar else 'no'} |",
        "",
        "_Draft for the author to edit. Which row applies is decided by code from `results/`, using rules written before "
        "Arm D ran. The product decisions are the PRD's; they are about this dataset and do not transfer to payments "
        "without the account-level data this dataset lacks._",
    ]
    return "\n".join(rows)


def limitations_block(ev: dict, cost: dict, budget: dict | None) -> str:
    cmp, h = ev["comparisons"], ev["hypotheses"]
    pre = "pre_shift_test"
    ba, db = cmp["B minus A"][pre]["p_at_k"], cmp["D minus B"][pre]["p_at_k"]
    share = max(cost["by_arm"][a][pre]["compute_share_of_cost"] for a in ("A", "B", "D"))
    demonstrated = [
        f"On this dataset, before the regime shift, adding graph features to a tuned local-feature model changed "
        f"precision at k by {diff_with_ci(ba)}.",
        f"A two-layer GraphSAGE on the same local features, against graph features: D minus B {diff_with_ci(db)}.",
        "After the regime shift at step 43, mean per-step PR-AUC fell by "
        + ", ".join(f"{pct(v)} for {a}" for a, v in h["H3"]["relative_fall"].items()) + ".",
        "No feature moved under the future-edge, label-shuffle or own-label tests (`results/leakage-tests.json`).",
    ]
    suggested = [
        f"H1, whether hand-built graph features capture most of the available lift: {h['H1']['outcome']}.",
        f"Compute is {share_text(share)} of modelled cost per true positive for every arm. Analyst time dominates, "
        "so the decision turns on alert quality, not on compute.",
    ]
    if budget:
        suggested.append(f"H4, whether the graph-feature advantage widens as labels get scarcer: {budget['H4']['outcome']}. "
                         "Validation labels were kept in full at every budget, so small-budget results are somewhat optimistic.")
    return ("**What this demonstrates.** _Draft for the author to edit._\n\n" + "\n".join(f"- {x}" for x in demonstrated)
            + "\n\n**What this suggests.**\n\n" + "\n".join(f"- {x}" for x in suggested))


def main() -> None:
    text = README.read_text()
    phase3 = (RESULTS / "evaluation-phase-3.json").is_file() and (RESULTS / "cost-per-true-positive.json").is_file()
    if phase3:
        ev = read_result("evaluation-phase-3")["data"]
        cost = read_result("cost-per-true-positive")["data"]
        budget = read_result("label-budget-curve")["data"] if (RESULTS / "label-budget-curve.json").is_file() else None
        phase2 = read_result("evaluation-arms-a-b")["data"]
        text = replace_block(text, "results", results_block_phase3(ev, cost) + "\n\n" + finding(phase2))
        text = replace_block(text, "hypotheses", hypotheses_block(ev, budget))
        text = replace_block(text, "decision-matrix", decision_block(ev, cost))
        text = replace_block(text, "limitations", limitations_block(ev, cost, budget))
    elif (RESULTS / "evaluation-arms-a-b.json").is_file():
        text = replace_block(text, "results", results_block(read_result("evaluation-arms-a-b")["data"]))
    README.write_text(text)
    print("README.md generated blocks updated")


if __name__ == "__main__":
    main()
