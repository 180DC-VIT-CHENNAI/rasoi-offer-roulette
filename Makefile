PYTHON ?= python3
export PYTHONPATH := src

.PHONY: install test lint typecheck inspect train submit api ui bench clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src

inspect:
	$(PYTHON) -m rasoi.cli inspect --data data/public

train:
	$(PYTHON) -m rasoi.cli train --data data/public

submit:
	$(PYTHON) -m rasoi.cli submit --data data/public --out submission/

api:
	$(PYTHON) -m uvicorn rasoi.serve.api:app --reload --port 8000

ui:
	$(PYTHON) -m streamlit run ui/app.py

bench:
	$(PYTHON) benchmarks/bench_uplift.py

clean:
	rm -rf submission/predictions.csv submission/plan.csv submission/portfolio.json submission/manifest.json .pytest_cache .mypy_cache .ruff_cache
