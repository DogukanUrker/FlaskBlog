# FlaskBlog Makefile

APP_DIR := app
TESTS_DIR := tests/e2e
UV := uv

.DEFAULT_GOAL := help

.PHONY: help install install-app run docker docker-build docker-run test test-slow lint ci clean

# Help
help: ## Show all available commands
	@echo "FlaskBlog Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Dependencies
install: ## Install all dependencies (app + dev + test + Playwright)
	cd $(APP_DIR) && $(UV) sync --all-extras
	cd $(APP_DIR) && $(UV) run playwright install chromium --with-deps

install-app: ## Install app dependencies only
	cd $(APP_DIR) && $(UV) sync

# Application
run: ## Run the Flask application (http://localhost:1283)
	cd $(APP_DIR) && $(UV) run app.py

# Docker
docker: docker-build docker-run ## Build and run with Docker

docker-build: ## Build Docker image
	docker build -t flaskblog .

docker-run: ## Run Docker container
	docker run --name flaskblog -d \
		--rm -p 1283:1283 \
		$(if $(wildcard .env),--env-file .env) \
		--network businessnet \
		flaskblog

# Testing
test: ## Run E2E tests (parallel)
	cd $(APP_DIR) && $(UV) run pytest ../$(TESTS_DIR) -v

test-slow: ## Run tests with visible browser in slow-mo (sequential)
	cd $(APP_DIR) && $(UV) run pytest ../$(TESTS_DIR) --headed --slowmo 500 -v -n 0

# Code Quality
lint: ## Format and lint code with Ruff (with auto-fix)
	cd $(APP_DIR) && $(UV) run ruff format ..
	cd $(APP_DIR) && $(UV) run ruff check --fix ..
	cd $(APP_DIR) && $(UV) run ruff format ..

# CI
ci: ## Run CI checks (format check + lint)
	cd $(APP_DIR) && $(UV) run ruff format --check --diff ..
	cd $(APP_DIR) && $(UV) run ruff check ..

# Cleanup
clean: ## Remove cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
