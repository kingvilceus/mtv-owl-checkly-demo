.DEFAULT_GOAL := help

.PHONY: help hooks lint

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

hooks: ## Install git pre-commit hooks
	uvx pre-commit install

lint: ## Run all linters / formatters on the whole tree
	uvx pre-commit run --all-files
