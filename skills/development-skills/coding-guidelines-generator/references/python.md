# Python Guidelines

> Verified: 2026-10-18, Python Official Docs & PEP Standards, applies to Python 3.10+ / 3.11 / 3.12 / 3.13

## Type Annotations & Clean Code
- **Type Hints**: Provide type hints for all function arguments, return types, and class attributes on public interfaces. Use modern built-in generics (`list[str]`, `dict[str, Any]`, `X | Y` union syntax).
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
