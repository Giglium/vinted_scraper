# ====================================================================================
# Setup Project
ROOT := $(shell pwd)
PROJECT_FOLDER := $(ROOT)/src
DOC_FOLDER := $(ROOT)/docs
MODULE_NAME := vinted_scraper
VERSION := $(shell git -C $(PROJECT_FOLDER) describe --tags --abbrev=0 )

SUPER_LINTER_FMT := -e VALIDATE_PYTHON_MYPY=false -e FIX_JAVASCRIPT_PRETTIER=true -e FIX_MARKDOWN=true -e FIX_MARKDOWN_PRETTIER=true -e FIX_JSON=true -e FIX_JSON_PRETTIER=true -e FIX_YAML_PRETTIER=true -e FIX_PYTHON_BLACK=true -e FIX_PYTHON_ISORT=true -e FIX_PYTHON_RUFF=true

# ====================================================================================
# Actions

.PHONY: all
all: fmt lint coverage

.PHONY: test
test: ## Run all the unit test.
	@uv run python -m unittest discover

.PHONY: act.test
act.test: #! Run the tests github actions
	@act -W '.github/workflows/tests.yml'

.PHONY: act.quickstarts
act.quickstarts: #! Run the quickstarts github actions
	@act -W '.github/workflows/quickstarts.yml'

.PHONY: build
build: ## Compile the library
	@uv build

.PHONY: act.build
act.build: #! Run the release github action
	@act -W '.github/workflows/release.yml'

.PHONY: update.user.agent
update.user.agent: ## Update the user agent file
	curl -s "https://www.useragents.me/#most-common-mobile-useragents-json-csv" | grep -A 20 'id="most-common-mobile-useragents-json-csv"' | grep -A 15 'class="col-lg-6"' | grep -o '<textarea class="form-control" rows="8">.*</textarea>' | sed -E 's/<textarea class="form-control" rows="8">//;s/<\/textarea>//' > $(PROJECT_FOLDER)/$(MODULE_NAME)/utils/agents.json

.PHONY: act.update.user.agent
act.update.user.agent: #! Run the Update user agent github action
	@act -W '.github/workflows/update-user-agents.yml'

.PHONY: coverage
coverage:  ## Run the unit test and generate the coverage report
	@uv run coverage run --source=$(PROJECT_FOLDER) -m unittest discover
	@uv run coverage html
	@uv run coverage report -m

.PHONY: act.coverage
act.coverage: #! Run the coverage github action
	@act -W '.github/workflows/coverage.yml'

.PHONY: fmt
fmt: ## Properly format the python code, to format others (YAML, Markdown, etc..) use the `make lint` command
	@uv run no_implicit_optional $(ROOT)
	@uv run black $(ROOT)
	@uv run isort $(ROOT) --profile black

.PHONY: lint
lint: ## Run the static analysis tool to scan the codebase
	@docker run --rm --name=vinter-scraper-linter -e SHELL=/bin/bash -e IGNORE_GITIGNORED_FILES=true -e RUN_LOCAL=true -e DEFAULT_BRANCH=main $(SUPER_LINTER_FMT) --mount type=bind,src=$(ROOT),dst=/tmp/lint/ --mount type=volume,dst=/tmp/lint/.venv ghcr.io/super-linter/super-linter:v8.0.0

.PHONY: act.lint
act.lint: #! Run the linter github action
	@act -W '.github/workflows/linter.yml'

.PHONY: docs
docs: ## Run pdoc to auto-generates API documentation
	@uv run pdoc --footer-text $(MODULE_NAME)-$(VERSION) --output-dir $(DOC_FOLDER) $(MODULE_NAME)

.PHONY: act.lint
act.docs: #! Run the linter github action
	@act -W '.github/workflows/docs.yml'

.PHONY: clean
clean: ## Clean up project files
	-@rm .coverage
	-@rm -r htmlcov/
	-@rm -r .mypy_cache
	-@rm -rf dist
	-@rm super-linter.log

# ====================================================================================
# Utils Actions

# https://stackoverflow.com/a/47107132
.PHONY: help
help: ## Show the basic command help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

.PHONY: help.all
act.help: ## Show the act command help.
	@sed -ne '/@sed/!s/#! //p' $(MAKEFILE_LIST)
