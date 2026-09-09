.DEFAULT_GOAL := help

# Override like: make serve PORT=8001
PORT ?= 8000
DATABASE_URL ?= postgresql://owl:owl@db:5432/owl
COMPOSE ?= docker compose
COMPOSE_ENV = API_HOST_PORT=$(PORT) DATABASE_URL=$(DATABASE_URL)
API_RUN = $(COMPOSE) run --rm -e DATABASE_URL=$(DATABASE_URL) api
MONITORING = cd monitoring && npm ci --silent

.PHONY: help hooks lint seed migrate serve web up down psql \
	monitor monitor-deploy monitor-agent

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
	$(COMPOSE_ENV) $(COMPOSE) up api

web: ## Run the React dev server (http://localhost:5173; API on :8000)
	$(COMPOSE_ENV) $(COMPOSE) up web

up: ## Start the whole stack in the background (API :8000, web :5173)
	$(COMPOSE_ENV) $(COMPOSE) up -d --wait

down: ## Stop the stack and delete its volumes
	$(COMPOSE) down -v --remove-orphans

psql: ## Open a psql shell on the app database
	$(COMPOSE) exec db psql -U owl -d owl

monitor-agent: ## Start the Checkly Private Location agent (needs CHECKLY_AGENT_API_KEY)
	$(COMPOSE) -f docker-compose.yml -f docker-compose.monitoring.yml up -d checkly-agent

monitor: ## Run the Checkly API checks (agent must be running: make monitor-agent)
	$(MONITORING) && npx checkly test

monitor-deploy: ## Deploy the Checkly checks to run on a schedule
	$(MONITORING) && npx checkly deploy --force
