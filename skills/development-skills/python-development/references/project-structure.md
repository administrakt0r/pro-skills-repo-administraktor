# Python Project Structure and Architecture Reference

Comprehensive reference guide for Python project architectures, standard configuration manifests, testing pipelines, automation runners, CI/CD workflows, and containerization strategies.

---

## 1. Directory Layouts

### 1.1 The `src` Layout (Recommended)

The `src` layout isolates application and library source code into a dedicated `src/` directory. This is the industry standard for Python packages and applications because it prevents the Python interpreter from importing the in-development working directory instead of the installed package during test execution.

```text
my-python-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker/
│   ├── Dockerfile
│   └── .dockerignore
├── docs/
│   └── index.md
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── py.typed             # PEP 561 typing marker
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── exceptions.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── domain.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── processor.py
│       └── cli.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_processor.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
├── .editorconfig
├── .gitignore
├── Makefile
├── pyproject.toml
├── README.md
└── uv.lock
```

#### Why `src` Layout Matters:
1. **Import Parity**: When running `pytest` from the project root, a flat layout allows tests to import `my_package` directly from the current working directory, even if package installation, entry points, or file inclusion in `pyproject.toml` is broken. The `src` layout forces the test runner to test against the installed package (e.g. editable install `pip install -e .` or `uv run pytest`).
2. **Clean Packaging**: Build backends (`hatchling`, `flit`, `setuptools`) automatically recognize `src/<name>` without mistakenly bundling root-level configuration files or scratch scripts into the distribution wheel.
3. **Explicit Namespace**: Clear boundary between build tooling, tests, documentation, and shippable code.

---

### 1.2 Flat Layout (Simpler Services / Standalone Scripts)

Used primarily for internal microservices or single-module scripts where wheel distribution is not required.

```text
my-service/
├── service/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── routes.py
├── tests/
│   ├── conftest.py
│   └── test_routes.py
├── .gitignore
├── Dockerfile
├── pyproject.toml
└── README.md
```

> **Caution**: In flat layouts, ensure `pytest` runs with `python -m pytest` or that `pythonpath = ["."]` is explicitly declared in `pyproject.toml` if relative imports fail.

---

### 1.3 Monorepo Layout

For repositories containing multiple interdependent Python packages or services.

```text
monorepo/
├── packages/
│   ├── core-lib/
│   │   ├── src/core_lib/
│   │   ├── pyproject.toml
│   │   └── tests/
│   └── common-data/
│       ├── src/common_data/
│       ├── pyproject.toml
│       └── tests/
├── services/
│   ├── api-gateway/
│   │   ├── src/gateway/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── tests/
│   └── worker/
│       ├── src/worker/
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── tests/
├── pyproject.toml               # Workspace configuration (uv or hatch workspace)
├── uv.lock
└── Makefile
```

---

## 2. Standard `pyproject.toml` Configurations

`pyproject.toml` (PEP 517 / PEP 518 / PEP 621) is the unified configuration format for Python packaging and tooling.

### 2.1 Complete Production Configuration (Hatchling Backend)

```toml
[build-system]
requires = ["hatchling>=1.20.0"]
build-backend = "hatchling.build"

[project]
name = "my-service"
version = "0.1.0"
description = "Modern scalable Python service"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
    { name = "Engineering Team", email = "dev@example.com" }
]
keywords = ["api", "asyncio", "service"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "typer>=0.12.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.10.0",
    "pre-commit>=3.7.0",
    "ruff>=0.5.0",
]
test = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
]

[project.scripts]
my-service = "my_package.cli:app"

# uv workspace and dependency groups
[dependency-groups]
dev = [
    { include-group = "test" },
    "mypy>=1.10.0",
    "ruff>=0.5.0",
]
test = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
]

# Hatch build target configuration
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]

# Ruff Configuration (Linting and Formatting)
[tool.ruff]
target-version = "py311"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade (modernizes syntax)
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # Line length handled by formatter
    "B008",   # Do not perform function calls in argument defaults (useful in FastAPI/Typer)
]

[tool.ruff.lint.isort]
known-first-party = ["my_package"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# Pytest Configuration
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=my_package",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html:coverage_html",
    "--cov-fail-under=85",
]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests requiring external services",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:httpx.*:",
]

# Coverage Configuration
[tool.coverage.run]
branch = true
source = ["src/my_package"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

# Mypy Static Type Checking
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
pretty = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

---

### 2.2 Flit Backend Alternative (Pure Python Libraries)

For lightweight, standard pure-Python libraries without custom build steps:

```toml
[build-system]
requires = ["flit_core>=3.9.0,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my-library"
dynamic = ["version", "description"]
authors = [{ name = "Author Name", email = "author@example.com" }]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27.0",
]
```

---

### 2.3 Setuptools Backend Alternative (PEP 621 Standard)

For legacy projects migrating away from `setup.py` / `setup.cfg`:

```toml
[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "legacy-migrated-project"
version = "1.0.0"
dependencies = [
    "pydantic>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```

---

## 3. Pytest Configuration & Fixture Patterns

### 3.1 Recommended `tests/conftest.py`

```python
"""Global pytest fixtures and configuration."""

from collections.abc import AsyncGenerator, Generator
from pathlib import Path
import tempfile
import pytest
import httpx


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the absolute path to the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide an isolated, self-cleaning temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_str:
        yield Path(tmp_str)


@pytest.fixture
def sample_payload() -> dict[str, object]:
    """Provide realistic sample data for API and domain models."""
    return {
        "id": "item-123",
        "name": "Sample Asset",
        "value": 42.5,
        "is_active": True,
        "tags": ["prod", "primary"],
    }


@pytest.fixture
async def async_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an asynchronous HTTP client session with mock transport or timeout."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        yield client
```

### 3.2 Unit vs Integration Testing Pattern

```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from my_package.models.domain import ItemModel


def test_item_creation_valid(sample_payload: dict[str, object]) -> None:
    item = ItemModel.model_validate(sample_payload)
    assert item.id == "item-123"
    assert item.value == 42.5


def test_item_creation_invalid_value() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ItemModel.model_validate({"id": "x", "name": "bad", "value": -10.0})
    assert "greater_than_equal" in str(exc_info.value)


# tests/integration/test_service.py
import pytest
from my_package.services.processor import RemoteDataProcessor


@pytest.mark.integration
async def test_fetch_and_process_external_data() -> None:
    processor = RemoteDataProcessor(base_url="https://api.example.com")
    result = await processor.fetch_summary("item-123")
    assert result.status == "SUCCESS"
```

---

## 4. Makefile and Task Runners

### 4.1 Production `Makefile`

```makefile
.PHONY: help install sync lint format type-check test test-cov run clean build docker-build

SHELL := /usr/bin/env bash
PYTHON ?= python3

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install uv virtual environment and all dependencies
	uv sync --all-groups

sync: ## Synchronize dependencies with uv.lock
	uv sync --frozen

lint: ## Check code style, types, and imports using Ruff and Mypy
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

format: ## Automatically format and fix lint errors
	uv run ruff check --fix .
	uv run ruff format .

type-check: ## Run static type checking with Mypy
	uv run mypy src

test: ## Run unit tests with pytest
	uv run pytest tests/unit

test-cov: ## Run full test suite with coverage report
	uv run pytest --cov=src --cov-report=term-missing tests/

test-integration: ## Run integration tests only
	uv run pytest -m integration tests/integration

build: ## Build wheel and sdist distributions
	uv run python -m build

clean: ## Clean cache files, coverage artifacts, and bytecode
	rm -rf .pytest_cache .ruff_cache .coverage coverage_html dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build: ## Build the Docker image
	docker build -t my-python-app:latest -f docker/Dockerfile .
```

### 4.2 Modern `justfile` Alternative

For environments using `just`:

```just
# List available commands
default:
    @just --list

# Install all dependencies with uv
install:
    uv sync --all-groups

# Format and check code
check:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src

# Run tests
test *args:
    uv run pytest {{args}}
```

---

## 5. GitHub Actions CI Pipeline

A fast, hardened GitHub Actions workflow leveraging `astral-sh/setup-uv` for dependency caching and Python matrix testing.

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-and-typecheck:
    name: Code Quality (Ruff & Mypy)
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --group dev

      - name: Run Ruff Lint
        run: uv run ruff check .

      - name: Run Ruff Format Check
        run: uv run ruff format --check .

      - name: Run Mypy Type Checking
        run: uv run mypy src

  test-matrix:
    name: Test on Python ${{ matrix.python-version }}
    needs: lint-and-typecheck
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --group test

      - name: Run Pytest
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage artifact (Python 3.12 only)
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
```

---

## 6. Production Docker Patterns for Python Applications

### 6.1 Multi-Stage Dockerfile with `uv`

Optimized for small image size, build caching, and security (non-root execution).

```dockerfile
# ==========================================
# Build Stage: Dependency compilation & wheel installation
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies if C extensions are required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency manifests first to maximize layer cache
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment without development packages
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and install project itself
COPY src/ ./src/
COPY README.md ./
RUN uv sync --frozen --no-dev

# ==========================================
# Runtime Stage: Minimal production image
# ==========================================
FROM python:3.12-slim-bookworm AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create unprivileged system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

# Copy virtual environment and installed app from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src

# Switch to unprivileged user
USER appuser

# Expose service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)" || exit 1

# Entrypoint running through virtualenv binary
CMD ["python", "-m", "my_package.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Standard `.dockerignore`

```text
.git
.github
.gitignore
.env
.env.*
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.ruff_cache/
.mypy_cache/
htmlcov/
coverage.xml
.coverage
dist/
build/
*.egg-info/
docs/
tests/
Dockerfile
.dockerignore
Makefile
```
