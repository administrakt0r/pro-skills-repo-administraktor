# Python Guidelines

> Verified: 2026-10-18, Python Official Docs & PEP Standards, applies to Python 3.8+ (including 3.10 / 3.11 / 3.12 / 3.13)

## Type Annotations & Clean Code
- **Type Hints & Version Compatibility**: Provide type hints for all function arguments, return types, and class attributes on public interfaces.
  - Python 3.10+: Use modern built-in generics (`list[str]`, `dict[str, Any]`) and `|` union syntax (`str | None`).
  - Python 3.8 / 3.9: Add `from __future__ import annotations` at the top of the module to use `|` union syntax and built-in generics in annotations, or use `typing.Union` / `typing.Optional`.
- **No Mutable Defaults**: Never use mutable objects (empty lists `[]`, dictionaries `{}`) as default parameter values. Use `None` as the default and initialize inside the function body.
- **Filesystem & Paths**: Use `pathlib.Path` instead of raw string manipulation with `os.path`.

## Error Handling & Resources
- **Resource Management**: Always use `with` context managers for files, sockets, database transactions, and network sessions to guarantee resource cleanup.
- **No Bare Except**: Never catch generic `except:` without an exception class. Catch specific exceptions (`ValueError`, `KeyError`) or at minimum `except Exception as err:` with logging.

## Database & Query Security
- **Parameterized Queries**: Never construct SQL queries via f-strings or `%` string formatting. Always pass query parameters via DB-API parameter tuples or ORM query builders.

## Framework Add-ons (Apply when detected)
- **FastAPI**: Use Pydantic v2 schemas for request validation and response models. Enforce dependency injection via `Depends()` for authentication and database sessions.
- **Django**: Run queries through the ORM; use `select_related()` and `prefetch_related()` to prevent N+1 query bottlenecks. Handle migrations via `python manage.py makemigrations --check`.
- **Flask**: Use blueprints to structure modular views; sanitize file uploads with `werkzeug.utils.secure_filename`.

## Verification Commands
- Lint & format: `ruff check .` and `ruff format --check .` (or project-configured linter).
- Tests: `pytest`
- Type checking: `mypy` or `pyright`
