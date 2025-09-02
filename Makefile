.PHONY: help install test lint format type-check security clean all

help:  ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup
install:  ## Install all dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

##@ Development
test:  ## Run all tests with coverage
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage (faster)
	pytest tests/ -v

lint:  ## Run linting checks
	ruff check src tests

format:  ## Format code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

format-check:  ## Check code formatting without making changes
	ruff format --check src/ tests/
	ruff check src/ tests/

type-check:  ## Run type checking (using ruff's type-aware rules)
	ruff check --select=F,E9,W6 src tests

security:  ## Run security checks
	bandit -r src/
	safety check

##@ Cleanup
clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

##@ All-in-one
all: format lint security test  ## Run all checks and tests

ci: lint security test  ## Run CI checks (without formatting)
