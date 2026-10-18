# PHP Guidelines

> Verified: 2026-10-18, PHP Official Manual & PHP-FIG Standards, applies to PHP 8.1+ / 8.2 / 8.3 / 8.4

## Modern Language Conventions
- **Strict Typing**: Add `declare(strict_types=1);` as the first statement in all new PHP files.
- **Standards**: Adhere to PSR-12 / PER Coding Style 2.0 and PSR-4 autoloading conventions.
- **Language Features**: Leverage constructor property promotion, match expressions, typed class properties, and enums where supported by the project's minimum PHP version.

## Database & Output Security
- **Prepared Statements**: Always use PDO or MySQLi parameterized prepared statements for database queries. Never concatenate variables or user input into SQL queries.
- **Contextual Output Escaping**: Escape all output based on context (`htmlspecialchars($str, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` for HTML body/attributes).
- **Password Hashing**: Use `password_hash()` with `PASSWORD_DEFAULT` or `PASSWORD_ARGON2ID` and `password_verify()`. Never use md5, sha1, or custom hashing.

## Verification Commands
- Linting: `./vendor/bin/phpcs` or `composer lint`
- Tests: `./vendor/bin/phpunit` or `composer test`
- Static Analysis: `./vendor/bin/phpstan analyse` or `./vendor/bin/psalm`
