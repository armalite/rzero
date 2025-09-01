.PHONY: install dev test lint type build clean

# Create virtualenv and install in editable mode
install:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip
	. .venv/bin/activate && pip install -e .

# Same as install but includes dev dependencies
dev:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip
	. .venv/bin/activate && pip install -e .[dev]

# Run pytest
test:
	. .venv/bin/activate && pytest -q

# Run ruff for linting
lint:
	. .venv/bin/activate && ruff check . --fix

# Run pyright for type checking
type:
	. .venv/bin/activate && pyright

# Build package for PyPI
build:
	. .venv/bin/activate && python3.10 -m build

# Clean build/dist caches
clean:
	rm -rf .venv/ build/ dist/ *.egg-info .pytest_cache .ruff_cache .pyright
