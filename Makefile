.PHONY: setup lint typecheck test check fmt clean audit boundaries

# One-command setup: install all dependencies
setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pre-commit install

# Linting (correctness + style + security)
lint:
	ruff check src/ tests/

# Type checking
typecheck:
	mypy src/

# Run tests with coverage
test:
	pytest tests/ -v

# Single-file verification: lint + typecheck a specific file
# Usage: make verify FILE=src/components/blob.py
verify:
	ruff check $(FILE)
	mypy $(FILE)

# All quality checks
check: lint typecheck test boundaries

# Auto-format
fmt:
	ruff format src/ tests/
	ruff check --fix src/ tests/

# Dependency security audit
audit:
	pip-audit

# Architectural boundary check
boundaries:
	lint-imports

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
