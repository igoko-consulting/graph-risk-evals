from results_io import ResultRefused, dataset_provenance, read_result

# Fixed by 01-the-bet/pre-registration.md. Not tunable.
PERIODS = {
    "training": (1, 29),
    "validation": (30, 34),
    "pre_shift_test": (35, 42),
    "post_shift_test": (43, 49),
}
K_STEPS = (PERIODS["training"][0], PERIODS["validation"][1])


def require(condition, message: str) -> None:
    """For checks that enforce the protocol: `python -O` strips assert statements, not these."""
    if not condition:
        raise SystemExit(message)


def period_of(step: int) -> str:
    for name, (first, last) in PERIODS.items():
        if first <= step <= last:
            return name
    raise ValueError(f"time step {step} is outside every pre-registered period")


def require_k_first() -> dict:
    """Any stage that reads test steps calls this, so k is always computed before test steps are read."""
    k = read_result("k")
    if k["provenance"]["dataset"]["files_sha256"] != dataset_provenance()["files_sha256"]:
        raise ResultRefused("results/k.json was computed on different data; rerun compute_k.py first")
    return k
