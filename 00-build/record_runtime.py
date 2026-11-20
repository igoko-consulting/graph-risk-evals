import os
import platform
import subprocess
import time

from paths import STORE
from results_io import write_result

CLOCK = STORE / "started-at"


def sysctl(name: str) -> str | None:
    out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True)
    return out.stdout.strip() or None


def main() -> None:
    if not CLOCK.is_file():
        raise SystemExit(f"{CLOCK} is missing; the runtime is only recorded by `make all`")
    elapsed = time.time() - int(CLOCK.read_text())
    write_result("pipeline-runtime", {
        "elapsed_seconds": round(elapsed),
        "covers": "Everything `make all` runs: environment install, tests, data download, every stage. "
                  "Install and download depend on the network and on caches.",
        "specification_target_minutes": 30,
        "machine": {
            "cpu": sysctl("machdep.cpu.brand_string") or platform.processor(),
            "performance_cores": sysctl("hw.perflevel0.physicalcpu"),
            "logical_cpus": os.cpu_count(),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "platform": platform.platform(),
        },
    })
    print(f"pipeline runtime: {elapsed / 3600:.1f} hours")


if __name__ == "__main__":
    main()
