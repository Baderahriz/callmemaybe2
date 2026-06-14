.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache .ruff_cache data/output

lint:
	uv run flake8 src
	uv run mypy src 

lint-strict: lint
	uv run python -m py_compile main.py
