.PHONY: help install install-dev test lint format clean run muzik run-default run-hello run-info run-status run-menu run-simple build check pre-commit test-coverage format-check

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip3 install -e .

install-dev: ## Install development dependencies
	pip3 install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=muzik --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 muzik/ tests/
	mypy muzik/

format: ## Format code with black
	black muzik/ tests/

format-check: ## Check code formatting
	black --check muzik/ tests/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

muzik: ## Run the Muzik application with interactive menu
	python3 -m muzik.main

run: ## Run the application (shows help)
	python3 -m muzik.main --help

run-default: ## Run the application with default action
	python3 -m muzik.main hello

run-hello: ## Run hello command
	python3 -m muzik.main hello

run-info: ## Run info command
	python3 -m muzik.main info

run-status: ## Run status command
	python3 -m muzik.main status

run-menu: ## Run interactive menu
	python3 -m muzik.main menu

run-simple: ## Run simple interactive menu (more reliable)
	python3 -m muzik.main simple

build: ## Build the package
	python3 -m build

check: ## Run all checks (lint, format, test)
	$(MAKE) lint
	$(MAKE) format-check
	$(MAKE) test

pre-commit: ## Run pre-commit checks
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test 