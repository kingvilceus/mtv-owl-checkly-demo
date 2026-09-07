.DEFAULT_GOAL := help

# Override like: make serve PORT=8001
PORT ?= 8000
DATABASE_URL ?= postgresql://owl:owl@db:5432/owl
COMPOSE ?= docker compose
API_RUN = $(COMPOSE) run --rm -e DATABASE_URL=$(DATABASE_URL) api

.PHONY: help hooks lint seed migrate serve web up down psql

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

hooks: ## Install git pre-commit hooks
	uvx pre-commit install

lint: ## Run all linters / formatters on the whole tree
	uvx pre-commit run --all-files

seed: ## Drop & recreate the database, run migrations, load funds.csv
	$(COMPOSE) up -d --wait db
	$(API_RUN) python scripts/seed.py

migrate: ## Apply every migration up to the current checkout
	$(COMPOSE) up -d --wait db
	$(API_RUN) yoyo apply --batch --database "$(DATABASE_URL)"

serve: ## Run the API on PORT (default 8000)
	$(COMPOSE) up -d --wait db
	API_HOST_PORT=$(PORT) $(COMPOSE) run --rm --service-ports \
		-e DATABASE_URL=$(DATABASE_URL) api

web: ## Run the React dev server (http://localhost:5173)
	$(COMPOSE) up web

up: ## Start the whole stack in the background
	$(COMPOSE) up -d --wait

down: ## Stop the stack and delete its volumes
	$(COMPOSE) down -v

psql: ## Open a psql shell on the app database
	$(COMPOSE) exec db psql -U owl -d owl
