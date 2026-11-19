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


def main() -> None:
    text = README.read_text()
    if (RESULTS / "evaluation-arms-a-b.json").is_file():
        text = replace_block(text, "results", results_block(read_result("evaluation-arms-a-b")["data"]))
    README.write_text(text)
    print("README.md generated blocks updated")


if __name__ == "__main__":
    main()
