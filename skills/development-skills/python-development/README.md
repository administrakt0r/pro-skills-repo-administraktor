# Python Development Skill

A universal coding agent skill for modern Python development (Python 3.10 through 3.13+), covering project packaging, modern toolchains (`uv`, `ruff`, `pytest`), type safety, data modeling, concurrency, and architecture patterns.

## What it does

This skill equips AI coding agents to architect, write, refactor, package, and test modern Python code using current industry standards and toolchains.

### Covers

- **Python 3.10 - 3.13+ Features**: Structural pattern matching (`match`/`case`), union syntax (`X | Y`), exception groups (`ExceptionGroup`, `except*`), `tomllib`, `Self`, PEP 695 type parameter syntax (`type`, generic functions/classes), `@override`, enhanced f-strings, and free-threaded (no-GIL) Python awareness.
- **Modern Toolchains & Packaging**: Fast dependency and virtual environment management via `uv` (`uv pip`, `uv venv`, `uv run`, `uv add`, `uv sync`), standard `venv`, and `poetry`. Unified packaging with `pyproject.toml` (PEP 517/518/621) and the recommended `src` directory layout.
- **Static Typing**: Modern PEP 604 unions, PEP 585 built-in collections, `typing.Protocol`, `TypedDict`, `Annotated`, `Literal`, and strict type checking with `mypy`/`pyright`.
- **Data Modeling**: Modern dataclasses (`slots=True`, `frozen=True`, `kw_only=True`) and Pydantic v2 validation models and environment settings (`pydantic-settings`).
- **Asynchronous Concurrency**: Modern `asyncio` with `asyncio.TaskGroup` for structured concurrency, background worker threads (`asyncio.to_thread`), and async HTTP clients with `httpx`.
- **Error Handling & Filesystem**: Custom domain exception hierarchies, exception chaining (`raise from`), exception notes (`add_note()`), and robust filesystem operations with `pathlib.Path`.
- **CLI Development**: Modern CLI development using `typer`, `click`, and standard library `argparse`.
- **Testing, Linting, & Formatting**: Test suites with `pytest` (fixtures, parametrization, markers, conftest) and lightning-fast linting/formatting via `ruff`.

## Directory Structure

```text
python-development/
├── README.md
├── SKILL.md
└── references/
    └── project-structure.md
```

## Reference Documentation

- [`references/project-structure.md`](references/project-structure.md): Deep-dive reference covering `src` vs flat layouts, complete production `pyproject.toml` templates (Hatchling, Flit, Setuptools), pytest configuration patterns, Makefile/justfile task runners, GitHub Actions CI workflows, and multi-stage Docker patterns.
