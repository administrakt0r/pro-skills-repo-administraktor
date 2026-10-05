---
name: php-development
description: >-
  Architect, build, test, refactor, and maintain modern PHP 8.0-8.4 applications, libraries, and APIs using strict typing, modern language features, PSR standards, Composer dependency management, PDO database access, PHPUnit/Pest testing, PHPStan/Psalm static analysis, and secure coding practices.
---

# Modern PHP Development

Modern PHP (PHP 8.0 through 8.4) is a strictly typed, compiled-to-bytecode, object-oriented language with functional capabilities, native enumerations, pattern matching, cooperative multitasking (fibers), property hooks, and comprehensive static analysis tooling. This skill covers architectural principles, language features, tooling standards, security hardening, and testing workflows required to deliver reliable PHP applications.

For detailed pattern implementations, code cheatsheets, and production templates, refer to [references/modern-php-patterns.md](references/modern-php-patterns.md).

---

## When to Use

- Writing new PHP applications, microservices, CLI tools, or reusable libraries.
- Upgrading legacy PHP codebases (PHP 5.x / 7.x) to PHP 8.0+.
- Implementing or refactoring domain models, value objects, and service architectures.
- Configuring Composer dependencies, autoloading, and scripts.
- Enforcing PSR standards (PSR-4 autoloading, PSR-12/PER-CS style, PSR-7/PSR-15 HTTP message processing).
- Adding automated tests using PHPUnit or Pest.
- Configuring static analysis with PHPStan or Psalm at high strictness levels.
- Hardening application security (PDO prepared statements, Argon2id/Bcrypt password hashing, input sanitization).
- Tuning production performance via OPcache, JIT compilation, and preloading.

---

## Prerequisites

- **PHP CLI**: PHP 8.2, 8.3, or 8.4 installed (`php -v`).
- **Composer**: Composer 2.x installed globally (`composer --version`).
- **Required Extensions**: `ext-mbstring`, `ext-json`, `ext-pdo`, `ext-openssl`, `ext-filter`, `ext-tokenizer`.
- **Development Tools**:
  - Testing: `phpunit/phpunit` (v10/v11) or `pestphp/pest` (v3).
  - Static Analysis: `phpstan/phpstan` (v1.12+) or `vimeo/psalm` (v5+).
  - Code Style: `friendsofphp/php-cs-fixer` or `squizlabs/php_codesniffer`.

Verify environment:
```bash
php -v
composer --version
php -m | grep -E "mbstring|json|pdo|opcache"
```

---

## Steps

### 1. Initialize Project and Configure Composer (PSR-4)

Initialize the project with strict typing defaults, security constraints, and PSR-4 autoloading:

```bash
composer init --no-interaction \
  --name="vendor-name/package-name" \
  --type="project" \
  --require="php:^8.3 || ^8.4"
```

Configure `composer.json` with strict platform pinning and autoload paths:

```json
{
  "name": "app/service",
  "type": "project",
  "require": {
    "php": "~8.3.0 || ~8.4.0",
    "psr/http-message": "^2.0",
    "psr/log": "^3.0"
  },
  "require-dev": {
    "phpstan/phpstan": "^1.12",
    "phpunit/phpunit": "^11.3",
    "pestphp/pest": "^3.0",
    "friendsofphp/php-cs-fixer": "^3.64"
  },
  "autoload": {
    "psr-4": {
      "App\\": "src/"
    }
  },
  "autoload-dev": {
    "psr-4": {
      "App\\Tests\\": "tests/"
    }
  },
  "config": {
    "sort-packages": true,
    "optimize-autoloader": true,
    "platform": {
      "php": "8.3.0"
    }
  },
  "scripts": {
    "test": "pest",
    "analyse": "phpstan analyse -c phpstan.neon",
    "format": "php-cs-fixer fix --dry-run --diff",
    "format:fix": "php-cs-fixer fix",
    "check": ["@format", "@analyse", "@test"]
  }
}
```

Regenerate autoloader:
```bash
composer dump-autoload
```

---

### 2. Enforce Strict Typing and Modern Type Declarations

Place `declare(strict_types=1);` as the first statement in **every single PHP file**. Use the complete PHP 8 type system:

```php
<?php

declare(strict_types=1);

namespace App\Domain\Model;

// 1. Union Types (PHP 8.0)
function calculateTax(int|float $amount, float $rate): float
{
    return (float) ($amount * $rate);
}

// 2. Intersection Types (PHP 8.1)
function countItems(\Countable&\Traversable $collection): int
{
    return count($collection);
}

// 3. Disjunctive Normal Form (DNF) Types (PHP 8.2)
function exportCollection((\Countable&\Iterator)|null $items): int
{
    return $items !== null ? count($items) : 0;
}

// 4. Standalone literal types & never return type (PHP 8.1 / 8.2)
function alwaysFails(): never
{
    throw new \RuntimeException('Operation halted');
}

function verifyFlag(bool $condition): true
{
    if (!$condition) {
        throw new \InvalidArgumentException('Condition must be true');
    }
    return true;
}
```

PHP 8.4 asymmetric visibility and property hooks:
```php
<?php

declare(strict_types=1);

namespace App\Domain\Model;

final class Invoice
{
    // Asymmetric visibility: public read, private write (PHP 8.4)
    public private(set) string $id;

    // Property hooks: native get/set logic (PHP 8.4)
    public float $rawTotal = 0.0;
    public float $finalTotal {
        get => $this->rawTotal * 1.20; // Includes 20% VAT
        set (float $value) {
            $this->rawTotal = $value / 1.20;
        }
    }

    public function __construct(string $id, float $rawTotal)
    {
        $this->id = $id;
        $this->rawTotal = $rawTotal;
    }
}
```

---

### 3. Implement Object-Oriented Architecture (Enums, Readonly, Interfaces)

- Use `readonly class` (PHP 8.2+) for immutable Data Transfer Objects (DTOs) and Value Objects.
- Use Backed Enums (PHP 8.1+) with methods and interfaces for domain states.
- Follow Interface Segregation: declare small, role-based interfaces.

```php
<?php

declare(strict_types=1);

namespace App\Domain\Order;

interface HasLabelInterface
{
    public function label(): string;
}

// Backed Enum with interface implementation
enum OrderStatus: string implements HasLabelInterface
{
    case Draft     = 'draft';
    case Pending   = 'pending';
    case Completed = 'completed';
    case Cancelled = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::Draft     => 'Draft Order',
            self::Pending   => 'Pending Payment',
            self::Completed => 'Fulfilled',
            self::Cancelled => 'Cancelled',
        };
    }

    public function canCancel(): bool
    {
        return match ($this) {
            self::Draft, self::Pending => true,
            self::Completed, self::Cancelled => false,
        };
    }
}

// Immutable Readonly DTO with constructor property promotion
readonly class CreateOrderCommand
{
    public function __construct(
        public string $customerId,
        public array $items,
        public OrderStatus $initialStatus = OrderStatus::Draft,
    ) {}
}
```

Proper trait usage:
```php
<?php

declare(strict_types=1);

namespace App\Domain\Shared;

// Traits MUST only contain reusable stateless behavioral methods
trait FormatsTimestampsTrait
{
    public function formatIso(\DateTimeInterface $dateTime): string
    {
        return $dateTime->format(\DateTimeInterface::ATOM);
    }
}
```

---

### 4. Utilize Match Expressions, Named Arguments & First-Class Callables

Replace error-prone `switch` statements and dynamic string callbacks:

```php
<?php

declare(strict_types=1);

namespace App\Application\Pricing;

use App\Domain\Order\OrderStatus;

final readonly class DiscountCalculator
{
    public function calculate(OrderStatus $status, float $subtotal, int $loyaltyPoints = 0): float
    {
        // Match expression: returns value, strict comparison (===), throws UnhandledMatchError if missing
        $multiplier = match ($status) {
            OrderStatus::Draft, OrderStatus::Pending => 1.0,
            OrderStatus::Completed                   => 0.95,
            OrderStatus::Cancelled                   => 0.0,
        };

        return $subtotal * $multiplier;
    }

    public function filterOrders(array $orders): array
    {
        // First-class callable syntax (PHP 8.1+)
        $validator = $this->isValid(...);
        return array_filter($orders, $validator);
    }

    private function isValid(array $order): bool
    {
        return !empty($order['id']);
    }
}

// Invocation with Named Arguments (PHP 8.0+)
$calc = new DiscountCalculator();
$total = $calc->calculate(
    status: OrderStatus::Completed,
    subtotal: 150.00,
    loyaltyPoints: 10
);
```

---

### 5. Apply Native PHP 8 Attributes

Replace dockblock `@annotation` tags with native `#[Attribute]` syntax:

```php
<?php

declare(strict_types=1);

namespace App\Infrastructure\Routing;

use Attribute;

#[Attribute(Attribute::TARGET_CLASS | Attribute::TARGET_METHOD)]
final readonly class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET',
        public int $priority = 0,
    ) {}
}
```

Applying and reading attributes via Reflection:
```php
<?php

declare(strict_types=1);

namespace App\Infrastructure\Routing;

use ReflectionClass;

#[Route(path: '/api/v1/orders', method: 'POST')]
final class OrderController
{
    #[\Override] // PHP 8.3 native override check
    public function __toString(): string
    {
        return self::class;
    }
}

// Reflection inspection
$reflector = new ReflectionClass(OrderController::class);
$attributes = $reflector->getAttributes(Route::class);

foreach ($attributes as $attribute) {
    /** @var Route $routeInstance */
    $routeInstance = $attribute->newInstance();
    // Register $routeInstance->path and $routeInstance->method
}
```

---

### 6. Concurrency and Cooperative Multitasking with Fibers

Use `Fiber` (PHP 8.1+) for cooperative multitasking without blocking the thread:

```php
<?php

declare(strict_types=1);

namespace App\Infrastructure\Async;

use Fiber;

final class TaskRunner
{
    /**
     * @param array<callable(): mixed> $tasks
     * @return array<int, mixed>
     */
    public function runParallel(array $tasks): array
    {
        $fibers = [];
        $results = [];

        foreach ($tasks as $i => $task) {
            $fibers[$i] = new Fiber($task);
            $results[$i] = $fibers[$i]->start();
        }

        while (!empty($fibers)) {
            foreach ($fibers as $i => $fiber) {
                if ($fiber->isTerminated()) {
                    $results[$i] = $fiber->getReturn();
                    unset($fibers[$i]);
                    continue;
                }

                if ($fiber->isSuspended()) {
                    $fiber->resume();
                }
            }
        }

        return $results;
    }
}
```

---

### 7. Architect Secure Database Operations with PDO

Never concatenate SQL. Disable emulated prepared statements, enable strict exception mode, and wrap multi-step changes in transactions:

```php
<?php

declare(strict_types=1);

namespace App\Infrastructure\Persistence;

use PDO;
use PDOException;

final readonly class DatabaseConnection
{
    public static function connect(string $dsn, string $user, #[\SensitiveParameter] string $pass): PDO
    {
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false, // Native prepared statements
            PDO::ATTR_STRINGIFY_FETCHES  => false,
        ];

        return new PDO($dsn, $user, $pass, $options);
    }
}

final readonly class OrderDatabaseService
{
    public function __construct(private PDO $pdo) {}

    public function createOrderWithTransaction(string $userId, array $items): int
    {
        $this->pdo->beginTransaction();

        try {
            // Prepared statement with named parameters
            $orderStmt = $this->pdo->prepare(
                'INSERT INTO orders (user_id, status, created_at) VALUES (:user_id, :status, NOW())'
            );
            $orderStmt->execute([
                'user_id' => $userId,
                'status'  => 'pending',
            ]);

            $orderId = (int) $this->pdo->lastInsertId();

            $itemStmt = $this->pdo->prepare(
                'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (:order_id, :product_id, :qty, :price)'
            );

            foreach ($items as $item) {
                $itemStmt->execute([
                    'order_id'   => $orderId,
                    'product_id' => $item['product_id'],
                    'qty'        => $item['quantity'],
                    'price'      => $item['price'],
                ]);
            }

            $this->pdo->commit();
            return $orderId;
        } catch (PDOException $e) {
            $this->pdo->rollBack();
            throw $e;
        }
    }
}
```

---

### 8. Enforce Application Security Controls

#### Input Validation
```php
$email = filter_var($inputEmail, FILTER_VALIDATE_EMAIL);
if ($email === false) {
    throw new \InvalidArgumentException('Invalid email address format.');
}

$age = filter_var($inputAge, FILTER_VALIDATE_INT, [
    'options' => ['min_range' => 18, 'max_range' => 120]
]);
```

#### Password Hashing (Argon2id & Bcrypt)
```php
// Hash using modern Argon2id algorithm (or PASSWORD_BCRYPT)
$hash = password_hash($plainPassword, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,
    'time_cost'   => 4,
    'threads'     => 1,
]);

// Verification
if (!password_verify($plainPassword, $hash)) {
    throw new \DomainException('Invalid credentials.');
}

// Automatic rehashing if cost parameters changed
if (password_needs_rehash($hash, PASSWORD_ARGON2ID)) {
    $newHash = password_hash($plainPassword, PASSWORD_ARGON2ID);
    // Persist $newHash
}
```

#### XSS Prevention
Always escape template output using `htmlspecialchars` with `ENT_QUOTES | ENT_SUBSTITUTE` and `UTF-8`:
```php
function escapeHtml(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
```

#### CSRF Verification
Generate cryptographically secure tokens using `random_bytes()` and verify with `hash_equals()`:
```php
$token = bin2hex(random_bytes(32));

if (!hash_equals($sessionToken, $submittedToken)) {
    throw new \DomainException('CSRF validation failed.');
}
```

---

### 9. Standardize Error and Exception Handling

Convert PHP warnings/notices into `ErrorException` and manage a structured domain exception hierarchy:

```php
<?php

declare(strict_types=1);

namespace App\Infrastructure\Error;

use ErrorException;
use Throwable;
use Psr\Log\LoggerInterface;

final class ErrorHandler
{
    public static function register(LoggerInterface $logger): void
    {
        error_reporting(E_ALL);

        // Convert notices/warnings to exceptions
        set_error_handler(
            static function (int $severity, string $message, string $file, int $line): bool {
                if (!(error_reporting() & $severity)) {
                    return false;
                }
                throw new ErrorException($message, 0, $severity, $file, $line);
            }
        );

        // Global uncaught exception logger
        set_exception_handler(
            static function (Throwable $e) use ($logger): void {
                $logger->critical('Uncaught exception: ' . $e->getMessage(), [
                    'exception' => $e::class,
                    'file'      => $e->getFile(),
                    'line'      => $e->getLine(),
                    'trace'     => $e->getTraceAsString(),
                ]);

                if (php_sapi_name() !== 'cli') {
                    http_response_code(500);
                    echo json_encode(['error' => 'An unexpected internal error occurred.']);
                }
                exit(1);
            }
        );
    }
}
```

---

### 10. Implement Automated Testing (PHPUnit & Pest)

#### PHPUnit 11 Setup
Test class using PHP 8 attributes:
```php
<?php

declare(strict_types=1);

namespace App\Tests\Unit;

use App\Domain\Order\OrderStatus;
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\DataProvider;

final class OrderStatusTest extends TestCase
{
    #[Test]
    public function it_identifies_cancellable_states(): void
    {
        $this->assertTrue(OrderStatus::Draft->canCancel());
        $this->assertTrue(OrderStatus::Pending->canCancel());
        $this->assertFalse(OrderStatus::Completed->canCancel());
        $this->assertFalse(OrderStatus::Cancelled->canCancel());
    }

    #[Test]
    #[DataProvider('statusLabelProvider')]
    public function it_returns_correct_label(OrderStatus $status, string $expectedLabel): void
    {
        $this->assertSame($expectedLabel, $status->label());
    }

    /**
     * @return array<string, array{0: OrderStatus, 1: string}>
     */
    public static function statusLabelProvider(): array
    {
        return [
            'draft'     => [OrderStatus::Draft, 'Draft Order'],
            'pending'   => [OrderStatus::Pending, 'Pending Payment'],
            'completed' => [OrderStatus::Completed, 'Fulfilled'],
            'cancelled' => [OrderStatus::Cancelled, 'Cancelled'],
        ];
    }
}
```

#### Pest 3 Setup
Declarative test suite (`tests/Unit/OrderStatusTest.php`):
```php
<?php

declare(strict_types=1);

use App\Domain\Order\OrderStatus;

describe('OrderStatus', function (): void {
    it('determines cancellation capability correctly', function (OrderStatus $status, bool $expected): void {
        expect($status->canCancel())->toBe($expected);
    })->with([
        [OrderStatus::Draft, true],
        [OrderStatus::Pending, true],
        [OrderStatus::Completed, false],
        [OrderStatus::Cancelled, false],
    ]);
});
```

Run test suite:
```bash
./vendor/bin/phpunit
# or with Pest
./vendor/bin/pest
```

---

### 11. Enforce Static Analysis and Code Quality

Configure `phpstan.neon` at level 8 or 9 (highest strictness):

```neon
parameters:
    level: 8
    paths:
        - src
        - tests
    checkMissingIterableValueType: true
    checkGenericClassInNonGenericObjectType: true
    treatPhpDocTypesAsCertain: false
```

Run static analysis:
```bash
./vendor/bin/phpstan analyse
./vendor/bin/psalm --show-info=false
```

Format code according to PSR-12 / PER Coding Style 2.0 with PHP-CS-Fixer (`.php-cs-fixer.dist.php`):
```php
<?php

$finder = PhpCsFixer\Finder::create()
    ->in([__DIR__ . '/src', __DIR__ . '/tests']);

return (new PhpCsFixer\Config())
    ->setRiskyAllowed(true)
    ->setRules([
        '@PER-CS2.0'                 => true,
        'strict_param'               => true,
        'declare_strict_types'       => true,
        'no_unused_imports'          => true,
        'ordered_imports'            => ['sort_algorithm' => 'alpha'],
        'single_quote'               => true,
    ])
    ->setFinder($finder);
```

Fix and verify style:
```bash
./vendor/bin/php-cs-fixer fix
```

---

### 12. Optimize Performance: OPcache, JIT, and Preloading

In production, configure `php.ini` to compile bytecode into shared memory:

```ini
; Production OPcache configuration
opcache.enable=1
opcache.enable_cli=0
opcache.memory_consumption=256
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.validate_timestamps=0
opcache.save_comments=1

; PHP 8 JIT (Tracing JIT)
opcache.jit=tracing
opcache.jit_buffer_size=100M

; OPcache Preloading
opcache.preload=/var/www/app/preload.php
opcache.preload_user=www-data
```

Create `preload.php` to prime the autoloader and core classes before requests arrive:
```php
<?php

declare(strict_types=1);

require_once __DIR__ . '/vendor/autoload.php';

$files = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator(__DIR__ . '/src')
);

foreach ($files as $file) {
    if ($file->isFile() && $file->getExtension() === 'php') {
        opcache_compile_file($file->getRealPath());
    }
}
```

Production Composer dump:
```bash
composer dump-autoload --no-dev --classmap-authoritative
```

---

## Best Practices

- **Strict Types Everywhere**: Add `declare(strict_types=1);` to all files.
- **Immutability by Default**: Use `readonly class` for DTOs and Value Objects. Use asymmetric visibility (`public private(set)`) when mutation is encapsulated.
- **Favor Enums over Constants**: Replace arrays of string constants with typed Backed Enums.
- **Parameter Redaction**: Protect secrets in function arguments with `#[\SensitiveParameter]`.
- **Prepared Statements**: Disable `PDO::ATTR_EMULATE_PREPARES` to ensure true parameterized database execution.
- **Domain Exceptions**: Throw specific domain exceptions rather than generic `\Exception` or `\Error`.
- **Authoritative Autoloading**: Run `composer dump-autoload -o -a` in deployment pipelines to bypass runtime file lookups.

---

## Common Pitfalls

- **Missing `declare(strict_types=1);`**: Without this header, PHP silently coerces types across file boundaries even if type hints are present.
- **Catching Generic `\Exception`**: Catches standard exceptions but misses runtime engine errors like `TypeError` or `DivisionByZeroError`. Catch `\Throwable` at the application boundary.
- **Overusing Traits as Multiple Inheritance**: Using stateful traits couples classes invisibly. Restrict traits to small, stateless helper methods or use dependency injection composition.
- **Dynamic Property Assignment**: Deprecated in PHP 8.2 and fatal in PHP 9.0. Always declare properties on classes.
- **Loose Comparisons (`==`)**: Always use `===` or `match()` expressions to avoid unexpected truthy coercions.
- **Trusting `unserialize()`**: Never pass untrusted user input to `unserialize()`. Use `json_decode()` or safe binary serializers.
- **Emulated Prepares Vulnerabilities**: Leaving `PDO::ATTR_EMULATE_PREPARES => true` allows potential SQL injection edge cases in certain multi-byte character sets.

---

## Verification

To verify that the modern PHP codebase is properly configured and functional:

1. **Verify PHP Syntax and Linting**:
   ```bash
   find src tests -name "*.php" -exec php -l {} \; | grep -v "No syntax errors detected" || echo "All files pass syntax lint"
   ```

2. **Verify Dependencies and Security Audit**:
   ```bash
   composer validate --strict
   composer audit
   ```

3. **Verify Autoloading Performance**:
   ```bash
   composer dump-autoload --optimize --classmap-authoritative --dry-run
   ```

4. **Verify Static Analysis Quality Gate**:
   ```bash
   ./vendor/bin/phpstan analyse -c phpstan.neon --no-progress
   ```

5. **Verify Automated Test Suite**:
   ```bash
   ./vendor/bin/phpunit --testdox
   # or with Pest
   ./vendor/bin/pest
   ```

6. **Verify Code Style Compliance**:
   ```bash
   ./vendor/bin/php-cs-fixer fix --dry-run --diff
   ```
