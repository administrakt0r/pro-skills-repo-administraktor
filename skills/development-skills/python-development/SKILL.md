---
name: python-development
description: >-
  Provides modern Python development standards (3.10-3.13+), covering environment management (uv, venv, poetry), packaging (pyproject.toml, src layout), static typing (PEP 604, PEP 695), data modeling (dataclasses, Pydantic v2), async concurrency (asyncio, TaskGroup, httpx), error handling, pathlib, structured logging, CLI creation (typer, click, argparse), pytest testing, and ruff linting/formatting. Use when creating, refactoring, packaging, or testing Python projects.
---

# Modern Python Development

A comprehensive engineering guide for modern, production-grade Python development across Python 3.10, 3.11, 3.12, and 3.13+. Focuses on strict static typing, modern toolchains centered around `uv` and `ruff`, robust project architectures using the `src` layout and `pyproject.toml`, structured concurrency, and automated testing with `pytest`.

See [project-structure.md](references/project-structure.md) for full `pyproject.toml` configurations, GitHub Actions CI workflows, Docker multi-stage builds, and directory templates.

---

## When to Use

- Initializing new Python services, libraries, or command-line tools.
- Modernizing legacy Python codebases (migrating from `setup.py` / `setup.cfg` / `requirements.txt` to `pyproject.toml` and `uv`).
- Writing type-safe, maintainable Python code with PEP 604 unions (`X | Y`) and PEP 695 type parameter syntax (`type`, generic functions/classes).
- Implementing data models with `dataclasses` or `pydantic` v2.
- Writing asynchronous I/O workflows with `asyncio.TaskGroup` and `httpx`.
- Setting up fast, modern linting and code formatting with `ruff`.
- Architecting unit and integration test suites with `pytest` fixtures, parametrization, and async test runners.

---

## Prerequisites

- **Python Runtime**: Python 3.10 or newer (Python 3.12+ recommended; Python 3.13+ supported).
- **Package & Environment Manager**: `uv` (strongly recommended for modern workflows) or standard `python3 -m venv` / `poetry`.
- **Code Quality Tools**: `ruff` (linter and formatter) and `mypy` or `pyright` (static type checking).
- **Test Runner**: `pytest` (with `pytest-asyncio` and `pytest-cov`).

---

## Steps

### 1. Environment and Package Management (`uv`, `venv`, `poetry`)

Modern Python development uses isolated virtual environments per project. `uv` is the standard next-generation toolchain: written in Rust, 10-100x faster than `pip`, and capable of managing Python versions, dependencies, and virtual environments without external tools.

#### 1.1 Managing Environments with `uv` (Recommended)

```bash
# Install a specific Python version automatically
uv python install 3.12

# Initialize a new project with src layout and pyproject.toml
uv init --package my-project
cd my-project

# Create a virtual environment
uv venv .venv --python 3.12

# Activate environment (or let 'uv run' handle execution automatically)
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Add production dependencies to pyproject.toml
uv add httpx pydantic pydantic-settings typer

# Add development/testing dependencies into dependency groups
uv add --dev ruff mypy
uv add --group test pytest pytest-asyncio pytest-cov

# Sync dependencies exactly to uv.lock (reproducible environments)
uv sync

# Run any tool inside the managed virtual environment without manual activation
uv run pytest
uv run ruff check .
```

#### 1.2 Managing Environments with Standard `venv` & `pip`

```bash
# Create virtual environment using system Python
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Upgrade pip and install wheel tools
python -m pip install --upgrade pip setuptools wheel

# Install in editable mode from pyproject.toml
pip install -e ".[dev,test]"
```

#### 1.3 Managing Environments with Poetry

```bash
# Initialize Poetry project
poetry init --no-interaction
poetry env use python3.12

# Add dependencies
poetry add httpx pydantic
poetry add --group dev ruff mypy pytest

# Install and spawn shell
poetry install
poetry run pytest
```

---

### 2. Project Packaging: `pyproject.toml` vs `requirements.txt`

#### Understanding the Distinction:
- **`pyproject.toml` (PEP 517 / 518 / 621)**: The single source of truth for project metadata, abstract dependencies (e.g., `httpx>=0.27.0`), build configurations, scripts, and tool settings (`ruff`, `pytest`, `mypy`). Use for all libraries, packages, and modern applications.
- **`requirements.txt` / Lockfiles (`uv.lock`, `poetry.lock`)**: Concrete, fully pinned versions with cryptographic hashes (e.g., `httpx==0.27.2 --hash=...`). Lockfiles guarantee deterministic, byte-for-byte deployment builds.

#### Migration from Legacy Configs:
- Replace `setup.py`, `setup.cfg`, and disparate `pytest.ini` / `.flake8` files with a single `pyproject.toml`.
- Structure the code in a `src/` layout: `src/<package_name>/__init__.py`.

```toml
# pyproject.toml minimal standard definition
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "service-engine"
version = "0.1.0"
description = "Scalable high-performance engine"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.7.0",
]

[project.scripts]
service-cli = "service_engine.cli:main"

[dependency-groups]
dev = ["ruff>=0.5.0", "mypy>=1.10.0"]
test = ["pytest>=8.2.0", "pytest-asyncio>=0.23.0"]
```

---

### 3. Leveraging Modern Python Version Features (3.10 - 3.13+)

#### Python 3.10: Structural Pattern Matching & Union Types

```python
# Structural pattern matching with match/case
def handle_event(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": int(x), "y": int(y)}:
            return f"Clicked at ({x}, {y})"
        case {"type": "keypress", "key": str(key)} if len(key) == 1:
            return f"Key pressed: {key}"
        case {"type": "quit"} | {"type": "exit"}:
            return "Terminating application"
        case _:
            return "Unknown event"


# Parenthesized context managers for clean multi-context handling
with (
    open("input.txt", "r", encoding="utf-8") as source,
    open("output.txt", "w", encoding="utf-8") as target,
):
    target.write(source.read())
```

#### Python 3.11: Task Groups, Exception Groups, `tomllib`, and `Self`

```python
import asyncio
import tomllib
from pathlib import Path
from typing import Self


# Built-in fast TOML parser
def load_config(path: Path) -> dict[str, object]:
    with path.open("rb") as f:
        return tomllib.load(f)


# Self type for fluent builders
class QueryBuilder:

    def __init__(self) -> None:
        self.clauses: list[str] = []

    def where(self, clause: str) -> Self:
        self.clauses.append(clause)
        return self


# asyncio.TaskGroup for structured concurrency & ExceptionGroup handling
async def fetch_metrics() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(asyncio.sleep(0.1, result=10))
            t2 = tg.create_task(asyncio.sleep(0.1, result=20))
    except* TimeoutError as eg:
        for exc in eg.exceptions:
            print(f"Handled timeout: {exc}")
```

#### Python 3.12: PEP 695 Type Parameters, `@override`, & Enhanced F-Strings

```python
from typing import override


# PEP 695: Clean generic type aliases and generic functions
type Coordinate = tuple[float, float]
type JSONValue = (
    str | int | float | bool | None | list[JSONValue] | dict[str, JSONValue]
)


def get_first[T](items: list[T]) -> T | None:
    return items[0] if items else None


class BaseService:

    def execute(self) -> str:
        return "base"


class SpecializedService(BaseService):

    @override  # Static verification that the method overrides a parent method
    def execute(self) -> str:
        return "specialized"


# Enhanced f-strings: quotes reuse, backslashes, and expressions
items = ["apple", "banana", "cherry"]
formatted = f"Items: {', '.join([item.upper() for item in items])}"
```

#### Python 3.13: Free-Threading & JIT Awareness

```python
# Python 3.13 introduces:
# 1. Experimental free-threaded (no-GIL) build support (python3.13t).
#    Code relying on CPU parallelism can scale via threading in nogil builds.
# 2. Copy-on-write and basic JIT compilation infrastructure.
# 3. New interactive REPL with multiline editing and colorized output.
# 4. Defaults for TypeVar (PEP 696): type KeyValue[K, V = str] = tuple[K, V]
```

---

### 4. Modern Static Typing & Type Annotations

Write fully type-annotated code adhering to modern PEPs:

```python
from collections.abc import Callable, Generator, Sequence
from typing import Annotated, Any, Literal, Protocol, TypedDict

# 1. Modern PEP 604 Union syntax (X | Y) instead of Optional[X] / Union[X, Y]
Status = Literal["pending", "active", "completed"]


# 2. Structural subtyping via Protocol (Duck typing with static guarantees)
class Renderable(Protocol):

    def render(self) -> str: ...


def print_ui(widget: Renderable) -> None:
    print(widget.render())


# 3. TypedDict for fixed-shape dictionaries
class UserProfile(TypedDict):
    id: int
    username: str
    is_admin: bool


# 4. Modern collections (PEP 585): use list, dict, set instead of typing.List, typing.Dict
def process_records(
    records: Sequence[UserProfile],
    callback: Callable[[UserProfile], bool] | None = None,
) -> dict[str, int]:
    counts: dict[str, int] = {"passed": 0, "failed": 0}
    for record in records:
        if callback and callback(record):
            counts["passed"] += 1
        else:
            counts["failed"] += 1
    return counts
```

---

### 5. Data Modeling: Dataclasses vs Pydantic v2

#### When to Choose:
- **`dataclasses`**: Domain models inside internal logic, mathematical operations, performance-critical loops without boundary serialization.
- **Pydantic v2**: Boundary models (HTTP requests, API payloads, config validation via `pydantic-settings`, parsing external inputs).

#### 5.1 Modern Dataclasses

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True, frozen=True, kw_only=True)
class Order:
    order_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_id: str
    items: list[str] = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def item_count(self) -> int:
        return len(self.items)
```

#### 5.2 Pydantic v2 Models & Settings

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    username: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=120)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    app_name: str = "CoreEngine"
    debug: bool = False
    port: int = 8000
    database_url: str
```

---

### 6. Resilient Error Handling and Exception Architecture

```python
# 1. Structured custom exception hierarchy
class AppBaseError(Exception):
    """Base error for all application domain exceptions."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ResourceNotFoundError(AppBaseError):

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            f"{resource} '{identifier}' not found", code="NOT_FOUND"
        )
        self.resource = resource
        self.identifier = identifier


# 2. Exception chaining ('raise ... from') & Exception Notes (Python 3.11+)
def parse_record(raw_id: str, payload: str) -> dict[str, object]:
    try:
        import json

        return json.loads(payload)
    except json.JSONDecodeError as err:
        custom_err = ResourceNotFoundError("Record", raw_id)
        # Preserve original traceback cause
        custom_err.add_note(f"Failed to parse payload chunk: {payload[:20]}...")
        raise custom_err from err
```

---

### 7. File I/O and Filesystem Operations with `pathlib`

Avoid legacy `os.path` operations. Use `pathlib.Path` with explicit encoding:

```python
from pathlib import Path
import tempfile


def safe_atomic_write(target_path: Path, content: str) -> None:
    """Safely write data to a file using an atomic temp-file rename."""
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file in the same directory, then replace atomically
    with tempfile.NamedTemporaryFile(
        "w",
        dir=target_path.parent,
        encoding="utf-8",
        delete=False,
    ) as tmp_file:
        tmp_file.write(content)
        temp_name = Path(tmp_file.name)

    temp_name.replace(target_path)


def scan_and_collect(directory: Path, pattern: str = "*.json") -> list[str]:
    """Recursively discover and read files with UTF-8 encoding."""
    if not directory.is_dir():
        return []

    return [
        path.read_text(encoding="utf-8")
        for path in directory.rglob(pattern)
        if path.is_file()
    ]
```

---

### 8. Asynchronous Concurrency (`asyncio` and `httpx`)

```python
import asyncio
from typing import Any
import httpx


async def fetch_resource(
    client: httpx.AsyncClient, url: str
) -> dict[str, Any] | None:
    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as err:
        print(f"HTTP error for {url}: {err.response.status_code}")
    except httpx.RequestError as err:
        print(f"Network error for {url}: {err}")
    return None


async def run_concurrent_pipeline(urls: list[str]) -> list[dict[str, Any]]:
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:
        results: list[dict[str, Any]] = []

        # Python 3.11+ structured concurrency with TaskGroup
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_resource(client, u)) for u in urls]

        for task in tasks:
            res = task.result()
            if res:
                results.append(res)
        return results


# Executing CPU-bound work without blocking the event loop
async def compute_heavy_data(data: list[int]) -> int:
    return await asyncio.to_thread(sum, data)
```

---

### 9. Logging Best Practices

Configure structured logging per module. Avoid root logger pollution:

```python
import logging
import sys


def setup_application_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    # Configure top-level package logger
    pkg_logger = logging.getLogger("service_engine")
    pkg_logger.setLevel(level)
    pkg_logger.addHandler(handler)
    pkg_logger.propagate = False


# In individual modules:
logger = logging.getLogger(__name__)


def process_item(item_id: str) -> None:
    logger.debug("Starting processing for item %s", item_id)
    try:
        logger.info("Successfully processed item %s", item_id)
    except Exception:
        logger.exception("Unexpected error while processing item %s", item_id)
        raise
```

---

### 10. Building Modern CLI Applications

#### 10.1 With `typer` (Recommended: Type-hint driven)

```python
from pathlib import Path
import typer

app = typer.Typer(help="Modern Service Automation CLI")


@app.command()
def process(
    input_file: Path = typer.Argument(
        ..., help="Path to input configuration file"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Simulate execution without changes"
    ),
    retries: int = typer.Option(
        3, "--retries", "-r", min=1, max=10, help="Number of retry attempts"
    ),
) -> None:
    """Process an incoming batch configuration file."""
    typer.echo(
        f"Processing {input_file} (dry_run={dry_run}, retries={retries})"
    )


if __name__ == "__main__":
    app()
```

#### 10.2 With `click` (Composable command groups)

```python
import click


@click.group()
def cli() -> None:
    """Data processing utility."""


@cli.command()
@click.argument("name")
@click.option("--count", default=1, help="Number of repetitions.")
def greet(name: str, count: int) -> None:
    for _ in range(count):
        click.echo(f"Hello, {name}!")
```

#### 10.3 With Standard `argparse` (Zero dependency)

```python
import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zero-dependency utility")
    parser.add_argument("source", help="Source file path")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logs"
    )
    return parser


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args)
    if parsed.verbose:
        print(f"Processing {parsed.source} in verbose mode")
    return 0
```

---

### 11. Testing Strategies with `pytest`

#### 11.1 Test Organization & Parametrization

```python
# tests/unit/test_calculator.py
import pytest


def add_numbers(a: int, b: int) -> int:
    return a + b


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300),
    ],
    ids=["positive", "canceling", "zeros", "large"],
)
def test_add_numbers(a: int, b: int, expected: int) -> None:
    assert add_numbers(a, b) == expected
```

#### 11.2 Fixture Teardown and Async Tests

```python
# tests/conftest.py
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
import tempfile
import pytest
import httpx


@pytest.fixture
def clean_workspace() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        yield path  # Test runs here
        # Cleanup occurs automatically when context exits


@pytest.fixture
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=2.0) as client:
        yield client


# tests/unit/test_async_api.py
import pytest


@pytest.mark.asyncio
async def test_client_connection(api_client: httpx.AsyncClient) -> None:
    assert api_client.is_closed is False
```

---

### 12. Linting and Formatting with `ruff`

`ruff` replaces `flake8`, `isort`, `black`, `bandit`, and `pydocstyle` in a single binary.

```bash
# Check code style, unused imports, and common bugs
uv run ruff check .

# Automatically apply safe fixes
uv run ruff check --fix .

# Check formatting compliance
uv run ruff format --check .

# Automatically format code according to PEP 8
uv run ruff format .
```

---

## Best Practices

| Category | Recommended Pattern | Anti-Pattern |
|---|---|---|
| **Layout** | `src/` layout (`src/pkg/__init__.py`) | Flat root layout mixing code and tooling config |
| **Manifest** | Unified `pyproject.toml` (PEP 621) | Fragmented `setup.py`, `setup.cfg`, `requirements.txt` |
| **Typing** | `X \| None`, `list[str]`, `def f[T](x: T) -> T` | `Optional[X]`, `typing.List[str]`, unannotated `Any` |
| **Models** | `slots=True, frozen=True` dataclasses; Pydantic v2 | Unvalidated mutable dicts or untyped custom classes |
| **Paths** | `pathlib.Path("a") / "b"`, `path.read_text("utf-8")` | `os.path.join()`, `open("f")` without explicit UTF-8 |
| **Async** | `asyncio.TaskGroup()`, `httpx.AsyncClient` | `asyncio.gather()` without error boundaries, `requests` in async |
| **Logging** | `logging.getLogger(__name__)`, `%s` placeholders | `print()`, root logger pollution, f-strings in log calls |
| **Packaging** | `uv sync`, `uv lock` | Manual non-deterministic `pip install` without lockfile |

---

## Common Pitfalls

1. **Mutable Default Arguments**:
   - *Bad*: `def append_item(val: str, items: list[str] = []) -> list[str]:`
   - *Fix*: `def append_item(val: str, items: list[str] | None = None) -> list[str]: items = items if items is not None else []`
2. **Missing File Encoding**:
   - *Bad*: `open("file.txt", "w")` (defaults to system locale; breaks across OS environments).
   - *Fix*: `open("file.txt", "w", encoding="utf-8")` or `Path("file.txt").write_text("...", encoding="utf-8")`.
3. **Bare `except:` Statements**:
   - *Bad*: `except:` catches `KeyboardInterrupt`, `SystemExit`, and hides bugs.
   - *Fix*: `except Exception as err:` or catch explicit domain exceptions (`KeyError`, `ValueError`).
4. **Blocking I/O in Async Coroutines**:
   - *Bad*: Using `time.sleep()`, synchronous `requests.get()`, or slow disk I/O directly in `async def`.
   - *Fix*: Use `await asyncio.sleep()`, `httpx.AsyncClient()`, or wrap blocking functions in `await asyncio.to_thread(func, *args)`.
5. **Overriding Without Notice**:
   - Forgetting `@override` leads to silent bugs if parent class signatures change during refactorings.

---

## Verification

Run this verification suite to confirm that the Python project conforms to modern quality standards:

```bash
# 1. Verify environment and lockfile integrity
uv sync --check

# 2. Check code style and modern syntax rules
uv run ruff check .

# 3. Check code formatting compliance
uv run ruff format --check .

# 4. Run static type checking with strict rules
uv run mypy src

# 5. Execute test suite with branch coverage enforcement
uv run pytest --cov=src --cov-fail-under=85 tests/

# 6. Verify build packaging produces valid sdist and wheel
uv run python -m build --sdist --wheel
```
