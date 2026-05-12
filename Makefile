.PHONY: help dev test lint format clean docker-build docker-run

help:  ## Show this help message
	@echo "Usage: make [target]"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

dev:  ## Run development server with hot reload
	CV_API_LOG_LEVEL=DEBUG CV_API_ENABLE_HOT_RELOAD=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-plain:  ## Run development server with plain logs
	CV_API_LOG_LEVEL=INFO CV_API_LOG_FORMAT=plain uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=app --cov-report=term --cov-report=html

lint:  ## Run linter
	ruff check app/

format:  ## Format code
	ruff format app/

format-check:  ## Check code formatting
	ruff format --check app/

type-check:  ## Run type checker
	mypy app/ --ignore-missing-imports

check-all: lint type-check test  ## Run all checks

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info

docker-build:  ## Build Docker image
	docker build -t cv-api:latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 -v $(PWD)/data:/app/data cv-api:latest

docker-dev:  ## Run Docker in development mode
	docker run -p 8000:8000 -v $(PWD)/data:/app/data -e CV_API_LOG_LEVEL=DEBUG cv-api:latest

docker-bash:  ## Get shell in running container
	docker run -it --rm -v $(PWD)/data:/app/data cv-api:latest /bin/bash

install-dev:  ## Install development dependencies
	pip install -r requirements/dev.txt
