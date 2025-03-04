# Use qvm to manage quarto, also update:
# * `quarto.path` in .vscode/settings.json
# * quarto version in .github/workflows/docs-publish.yml
QUARTO_VERSION ?= v1.6.42
QVM_QUARTO_PATH = ~/.local/share/qvm/versions/${QUARTO_VERSION}/bin/quarto

.PHONY: install-quarto
install-quarto:
	@echo "🔵 Installing quarto"
	@if ! [ -z $(command -v qvm)]; then \
		@echo "Error: qvm is not installed. Please visit https://github.com/dpastoor/qvm/releases/ to install it." >&2 \
		exit 1; \
	fi
	qvm install ${QUARTO_VERSION}
	@echo "🔹 Updating .vscode/settings.json"
	@awk -v path="~/.local/share/qvm/versions/${QUARTO_VERSION}/bin/quarto" '/"quarto.path":/ {gsub(/"quarto.path": ".*"/, "\"quarto.path\": \"" path "\"")} 1' .vscode/settings.json > .vscode/settings.json.tmp && mv .vscode/settings.json.tmp .vscode/settings.json
	@echo "🔹 Updating .github/workflows/docs-publish.yml"
	@awk -v ver="${QUARTO_VERSION}" '/QUARTO_VERSION:/ {gsub(/QUARTO_VERSION: .*/, "QUARTO_VERSION: " ver)} 1' .github/workflows/docs-publish.yml > .github/workflows/docs-publish.yml.tmp && mv .github/workflows/docs-publish.yml.tmp .github/workflows/docs-publish.yml


.PHONY: docs
docs:  ## [docs] Build the documentation
	${QVM_QUARTO_PATH} render docs

.PHONY: docs-preview
docs-preview:  ## [docs] Preview the documentation
	${QVM_QUARTO_PATH} preview docs

.PHONY: pre-commit-all
pre-commit-all:
	uv run pre-commit run --files $$(git ls-files | grep -E "[.]([qR]?md|py|R|ya?ml|[jt]s|toml)$$")

.PHONY: py-setup
py-setup:  ## [py] Setup python environment
	uv sync --all-extras
	uv run pre-commit install

.PHONY: py-check
py-check:  py-check-format py-check-types py-check-tests ## [py] Run python checks

.PHONY: py-check-tox
py-check-tox:  ## [py] Run python 3.9 - 3.12 checks with tox
	@echo ""
	@echo "🔄 Running tests and type checking with tox for Python 3.9--3.12"
	uv run tox run-parallel

.PHONY: py-check-tests
py-check-tests:  ## [py] Run python tests
	@echo ""
	@echo "🧪 Running tests with pytest"
	uv run pytest

.PHONY: py-check-types
py-check-types:  ## [py] Run python type checks
	@echo ""
	@echo "📝 Checking types with pyright"
	uv run pyright

.PHONY: py-check-format
py-check-format:
	@echo ""
	@echo "📐 Checking format with ruff"
	uv run ruff check pkg-py --config pyproject.toml

.PHONY: py-format
py-format: ## [py] Format python code
	uv run ruff check --fix pkg-py --config pyproject.toml
	uv run ruff format pkg-py --config pyproject.toml

.PHONY: py-coverage
py-coverage: ## [py] Generate coverage report
	@echo "📔 Generating coverage report"
	uv run coverage run -m pytest
	uv run coverage report

.PHONY: py-coverage-report
py-coverage-report: py-coverage ## [py] Generate coverage report and open it in browser
	uv run coverage html
	@echo ""
	@echo "📡 Serving coverage report at http://localhost:8081/"
	@npx http-server htmlcov --silent -p 8081

.PHONY: py-update-snaps
py-update-snaps:  ## [py] Update python test snapshots
	@echo "📸 Updating pytest snapshots"
	uv run pytest --snapshot-update

.PHONY: py-docs
py-docs:  ## [py] Generate python docs
	@echo "📖 Generating python docs with quartodoc"
	@$(eval export IN_QUARTODOC=true)
	cd docs && uv run quartodoc build
	cd docs && uv run quartodoc interlinks

.PHONY: py-docs-watch
py-docs-watch:  ## [py] Generate python docs
	@echo "📖 Generating python docs with quartodoc"
	@$(eval export IN_QUARTODOC=true)
	uv run quartodoc build --config docs/_quarto.yml --watch

.PHONY: py-docs-clean
py-docs-clean:   ## [py] Clean python docs
	@echo "🧹 Cleaning python docs"
	find docs/pkg/py -name '*.qmd' ! -name 'index.qmd' -delete
	find docs/pkg/py -name '*.quarto_ipynb' -delete

.PHONY: py-build
py-build:   ## [py] Build python package
	@echo "🧳 Building python package"
	@[ -d dist ] && rm -r dist || true
	uv build

.PHONY: help
help:  ## Show help messages for make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; { \
		printf "\033[32m%-18s\033[0m", $$1; \
		if ($$2 ~ /^\[docs\]/) { \
			printf "\033[34m[docs]\033[0m%s\n", substr($$2, 7); \
		} else if ($$2 ~ /^\[py\]/) { \
			printf "  \033[33m[py]\033[0m%s\n", substr($$2, 5); \
		} else if ($$2 ~ /^\[r\]/) { \
			printf "   \033[31m[r]\033[0m%s\n", substr($$2, 4); \
		} else { \
			printf "       %s\n", $$2; \
		} \
	}'

.DEFAULT_GOAL := help
