.PHONY: help install test lint format type-check security clean build docker docs

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install --with dev

install-prod:  ## Install production dependencies only
	poetry install --without dev

install-hooks:  ## Install pre-commit hooks
	poetry run pre-commit install

test:  ## Run tests with coverage
	poetry run pytest --cov --cov-report=term-missing --cov-report=html

test-verbose:  ## Run tests with verbose output
	poetry run pytest -vv --cov --cov-report=term-missing

test-watch:  ## Run tests in watch mode
	poetry run ptw --runner "pytest --cov"

lint:  ## Run linting checks
	poetry run ruff check .

lint-fix:  ## Run linting checks and fix issues
	poetry run ruff check . --fix

format:  ## Format code
	poetry run ruff format .

format-check:  ## Check code formatting
	poetry run ruff format --check .

type-check:  ## Run type checking
	poetry run mypy colour gen --ignore-missing-imports

security:  ## Run security checks
	poetry run bandit -r colour gen -f screen
	poetry run safety check

quality:  ## Run all quality checks
	@make lint
	@make format-check
	@make type-check
	@make security

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true

build:  ## Build package
	poetry build

publish-test:  ## Publish to TestPyPI
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

publish:  ## Publish to PyPI
	poetry publish

docker-build:  ## Build Docker image
	docker build -t colorgen:latest .

docker-run:  ## Run Docker container
	docker-compose up colorgen

docker-dev:  ## Run Docker container in development mode
	docker-compose up colorgen-dev

docs:  ## Build documentation
	poetry run mkdocs build

docs-serve:  ## Serve documentation locally
	poetry run mkdocs serve

docs-deploy:  ## Deploy documentation to GitHub Pages
	poetry run mkdocs gh-deploy

tui:  ## Run TUI application
	poetry run python -m colorgen.tui.app

cli:  ## Run CLI application (example)
	poetry run python colorgen.py --help

demo:  ## Run demo with test image
	@echo "Creating demo with test image..."
	poetry run python colorgen.py tests/test.png --config kitty --theme dark --verbose

ci:  ## Run CI checks locally
	@make quality
	@make test

version-patch:  ## Bump patch version
	poetry version patch
	@echo "New version: $$(poetry version -s)"

version-minor:  ## Bump minor version
	poetry version minor
	@echo "New version: $$(poetry version -s)"

version-major:  ## Bump major version
	poetry version major
	@echo "New version: $$(poetry version -s)"
