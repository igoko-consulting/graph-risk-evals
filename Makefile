PYTHON_VERSION := $(shell cat .python-version)
VENV := .venv
PY := $(VENV)/bin/python
UV := $(shell command -v uv 2>/dev/null || ls $(HOME)/.local/bin/uv 2>/dev/null)
EXCLUDE_NEWER ?= 2026-11-05
# CPU-only PyTorch, consulted for PyTorch packages only, so a Linux clone does not pull CUDA libraries.
TORCH_CPU_INDEX := https://download.pytorch.org/whl/cpu
STAGES := compute_k class_balance day_one_checks build_graph_store leakage_gate run_arms evaluate_arms \
	run_arm_d evaluate_phase3 evidence_chains engine_comparison render_charts render_readme run_label_budgets evaluate_label_budgets render_charts record_runtime render_readme

export PYTHONPATH := $(CURDIR):$(CURDIR)/00-build
# Performance cores only: on Apple silicon, threads on efficiency cores make every fit wait for stragglers.
OMP_NUM_THREADS ?= $(shell sysctl -n hw.perflevel0.physicalcpu 2>/dev/null || nproc 2>/dev/null || echo 4)
export OMP_NUM_THREADS

.PHONY: all data test clean distclean lock start-clock

all: start-clock test data
	@for stage in $(STAGES); do echo "== $$stage"; $(PY) 00-build/$$stage.py || exit 1; done

$(VENV)/.installed: requirements.txt .python-version
ifneq ($(UV),)
	$(UV) venv --clear --python $(PYTHON_VERSION) $(VENV)
	$(UV) pip sync --python $(PY) --torch-backend cpu requirements.txt
else
	python3.13 -m venv --clear $(VENV)
	$(PY) -m pip install --extra-index-url $(TORCH_CPU_INDEX) -r requirements.txt
endif
	@touch $@

start-clock:
	@mkdir -p data/store && date +%s > data/store/started-at

data: $(VENV)/.installed
	$(PY) 00-build/fetch_data.py

test: $(VENV)/.installed
	$(PY) -m pytest

clean:
	rm -rf data/store
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

distclean: clean
	rm -rf data $(VENV)

lock:
	$(UV) pip compile requirements.in --universal --python-version 3.13 --exclude-newer $(EXCLUDE_NEWER) \
	  --no-header --no-annotate --torch-backend cpu -o requirements.txt
