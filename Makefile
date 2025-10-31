.PHONY: help setup install dev test lint format clean docker-build docker-up docker-down demo

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up project..."
	cp .env.example .env
	python -m venv venv
	@echo "Activate virtual environment: source venv/bin/activate (Linux/Mac) or .\venv\Scripts\activate (Windows)"

install: ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

dev: ## Run development server
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

lint: ## Run linters
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

clean: ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start all services
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs
	docker-compose logs -f api

docker-restart: ## Restart API service
	docker-compose restart api

docker-clean: ## Remove all containers and volumes
	docker-compose down -v
	docker system prune -f

demo: ## Run demo script
	bash scripts/demo_run.sh

health: ## Check service health
	curl http://localhost:8000/healthz
	curl http://localhost:6333/health

migrate: ## Run database migrations (placeholder)
	@echo "Running migrations..."

seed: ## Seed sample data
	python scripts/seed_data.py

ci: lint test ## Run CI checks locally
