.PHONY: help install run test lint format

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	poetry lock && poetry install

run:  ## Run the CLI
	poetry run colorgen

test:  ## Run tests
	poetry run pytest

lint:  ## Run linting
	poetry run ruff check .

format:  ## Format code, lint, and type check
	poetry run ruff format .
	poetry run ruff check --fix .
	poetry run mypy colour gen --ignore-missing-imports
