PYTHON_VERSION := $(shell cat .python-version)
VENV := .venv
PY := $(VENV)/bin/python
UV := $(shell command -v uv 2>/dev/null || ls $(HOME)/.local/bin/uv 2>/dev/null)
EXCLUDE_NEWER ?= 2026-11-05
STAGES := compute_k class_balance day_one_checks build_graph_store render_charts

export PYTHONPATH := $(CURDIR):$(CURDIR)/00-build

.PHONY: all data test clean distclean lock

all: test data
	@for stage in $(STAGES); do echo "== $$stage"; $(PY) 00-build/$$stage.py || exit 1; done

$(VENV)/.installed: requirements.txt .python-version
ifneq ($(UV),)
	$(UV) venv --clear --python $(PYTHON_VERSION) $(VENV)
	$(UV) pip sync --python $(PY) requirements.txt
else
	python3.13 -m venv --clear $(VENV)
	$(PY) -m pip install -r requirements.txt
endif
	@touch $@

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
	$(UV) pip compile requirements.in --universal --python-version 3.13 --exclude-newer $(EXCLUDE_NEWER) --no-header --no-annotate -o requirements.txt
