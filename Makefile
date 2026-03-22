.PHONY: help install run preview generate apply test lint format serve

WALLPAPER ?= ~/.config/wallpaper
THEME ?= dark

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	poetry lock && poetry install

run:  ## Run the CLI (pass ARGS, e.g. make run ARGS="-fc -p ~/.config/wallpaper")
	poetry run colorgen $(ARGS)

preview:  ## Preview palette from wallpaper
	poetry run colorgen -p -t $(THEME) $(WALLPAPER)

generate:  ## Generate all configs from wallpaper (preview included)
	poetry run colorgen -fc -p -t $(THEME) $(WALLPAPER)

apply:  ## Generate all configs and apply them
	poetry run colorgen -fc -a -p -t $(THEME) $(WALLPAPER)

test:  ## Run tests
	poetry run pytest

lint:  ## Run linting
	poetry run ruff check .

format:  ## Format code, lint, and type check
	poetry run ruff format .
	poetry run ruff check --fix .
	poetry run mypy colour gen --ignore-missing-imports

serve:  ## Serve docs locally
	poetry run mkdocs serve
