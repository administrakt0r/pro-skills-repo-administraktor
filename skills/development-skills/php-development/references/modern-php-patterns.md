# Modern PHP Patterns and Reference Guide

This reference guide provides code patterns, cheatsheets, and production best practices for modern PHP development (PHP 8.0 through PHP 8.4).

---

## 1. PHP 8.x Feature Cheatsheet

### PHP 8.0
- **Named Arguments**: Pass arguments by name, skipping optional defaults and improving readability.
  ```php
  array_fill(start_index: 0, count: 100, value: 'placeholder');
  ```
- **Constructor Property Promotion**: Declare visibility directly in constructor parameter lists to eliminate boilerplate assignments.
  ```php
  final class Money
  {
      public function __construct(
          public int $amountInCents,
          public string $currency = 'USD',
      ) {}
  }
  ```
- **Match Expression**: Strict equality (`===`), returns a value, exhaustive checking, throws `UnhandledMatchError` if unmatched.
  ```php
  $statusText = match ($statusCode) {
      200, 201 => 'OK',
      400 => 'Bad Request',
      404 => 'Not Found',
      500 => 'Server Error',
      default => 'Unknown Status',
  };
  ```
- **Nullsafe Operator (`?->`)**: Safely traverse chains of nullable object references.
  ```php
  $country = $session?->user?->getAddress()?->country;
  ```
- **Union Types**: Combine multiple types using `|`.
  ```php
  public function find(int|string $identifier): User|null
  {
      // ...
  }
  ```
- **Attributes**: Native structured metadata (replacing PHPDoc annotations).
  ```php
  #[Attribute(Attribute::TARGET_CLASS | Attribute::TARGET_METHOD)]
  final class Route
  {
      public function __construct(public string $path, public string $method = 'GET') {}
  }
  ```
- **Throw Expressions**: Use `throw` in arrow functions, null coalescing, or ternary expressions.
  ```php
  $config = $options['api_key'] ?? throw new InvalidArgumentException('Missing API key');
  ```
- **String Helpers**: Native functions `str_contains()`, `str_starts_with()`, `str_ends_with()`.

---

### PHP 8.1
- **Pure and Backed Enums**: Type-safe enumerations with method support.
  ```php
  enum OrderStatus: string
  {
      case Pending = 'pending';
      case Paid = 'paid';
      case Shipped = 'shipped';
      case Cancelled = 'cancelled';

      public function isTerminal(): bool
      {
          return match ($this) {
              self::Shipped, self::Cancelled => true,
              self::Pending, self::Paid => false,
          };
      }
  }
  ```
- **Readonly Properties**: Properties that can only be initialized once, preventing mutation.
  ```php
  final class Customer
  {
      public function __construct(
          public readonly string $id,
          public readonly string $email,
      ) {}
  }
  ```
- **First-Class Callable Syntax**: Create callables cleanly with `(...)`.
  ```php
  $stringLength = strlen(...);
  $lengths = array_map(strlen(...), ['apple', 'banana', 'cherry']);

  $handler = $service->process(...);
  ```
- **Intersection Types**: Require an argument to satisfy all specified interfaces using `&`.
  ```php
  public function processCollection(Countable&Traversable $items): int
  {
      return count($items);
  }
  ```
- **Fibers**: Low-level cooperative multitasking (coroutines/green threads).
  ```php
  $fiber = new Fiber(function (): void {
      $input = Fiber::suspend('paused');
      echo "Fiber resumed with: {$input}\n";
  });

  $state = $fiber->start(); // Returns 'paused'
  $fiber->resume('data payload');
  ```
- **`never` Return Type**: Indicates that a function terminates the program via `exit()`, `die()`, or always throws.
  ```php
  public function abort(string $message, int $code = 400): never
  {
      throw new DomainException($message, $code);
  }
  ```
- **Final Class Constants**: Prevent constants from being overridden in child classes.
  ```php
  class BaseGateway
  {
      final public const API_VERSION = 'v2';
  }
  ```

---

### PHP 8.2
- **Readonly Classes**: Marks all properties inside the class as `readonly` and prevents dynamic property creation.
  ```php
  readonly class Address
  {
      public function __construct(
          public string $street,
          public string $city,
          public string $postalCode,
          public string $country,
      ) {}
  }
  ```
- **Disjunctive Normal Form (DNF) Types**: Combine intersection and union types using parentheses `(A&B)|C`.
  ```php
  public function process((Countable&Traversable)|null $items): void
  {
      if ($items === null) {
          return;
      }
      echo count($items);
  }
  ```
- **Standalone `null`, `false`, and `true` Types**: Use literal types in parameters and return signatures.
  ```php
  public function verifyToken(string $token): true
  {
      if (!hash_equals($this->expected, $token)) {
          throw new UnauthorizedException('Token invalid');
      }
      return true;
  }
  ```
- **Sensitive Parameter Redaction**: Hide sensitive values from backtraces and error outputs.
  ```php
  public function authenticate(
      string $username,
      #[\SensitiveParameter] string $password,
  ): bool {
      // $password will appear as Object(SensitiveParameterValue) in traces
      return password_verify($password, $this->hash);
  }
  ```
- **Deprecation of Dynamic Properties**: Accessing undeclared properties emits a deprecation notice unless the class is decorated with `#[\AllowDynamicProperties]`.

---

### PHP 8.3
- **Typed Class Constants**: Type hints for class, interface, and enum constants.
  ```php
  interface CacheConfig
  {
      public const int DEFAULT_TTL = 3600;
      public const string PREFIX = 'app_cache_';
  }
  ```
- **Dynamic Class Constant Fetch**: Fetch class constants with variable syntax.
  ```php
  $constName = 'DEFAULT_TTL';
  $ttl = CacheConfig::{$constName};
  ```
- **`#[\Override]` Attribute**: Guarantees that a method overrides a parent method or implements an interface method. Triggers compile error if parent method is renamed or removed.
  ```php
  class ConcreteRepository extends AbstractRepository
  {
      #[\Override]
      public function findById(int $id): ?Entity
      {
          return $this->records[$id] ?? null;
      }
  }
  ```
- **Native `json_validate()`**: Fast JSON syntax verification without memory allocation for parsed structures.
  ```php
  if (!json_validate($payload)) {
      throw new InvalidArgumentException('Malformed JSON received: ' . json_last_error_msg());
  }
  ```
- **Deep Cloning of Readonly Properties**: Readonly properties can be reinitialized inside `__clone()`.
  ```php
  readonly class Document
  {
      public function __construct(
          public string $id,
          public DateTimeImmutable $createdAt,
      ) {}

      public function __clone(): void
      {
          $this->id = bin2hex(random_bytes(16)); // Allowed in PHP 8.3+
      }
  }
  ```

---

### PHP 8.4
- **Property Hooks**: Concise getters and setters directly attached to properties.
  ```php
  final class User
  {
      public string $firstName;
      public string $lastName;

      public string $fullName {
          get => "{$this->firstName} {$this->lastName}";
          set (string $value) {
              [$first, $last] = explode(' ', $value, 2);
              $this->firstName = $first;
              $this->lastName = $last;
          }
      }
  }
  ```
- **Asymmetric Visibility**: Separate visibility for read and write operations on properties.
  ```php
  final class Order
  {
      public function __construct(
          public private(set) string $id,
          public private(set) float $total,
      ) {}

      public function applyDiscount(float $percentage): void
      {
          $this->total -= $this->total * ($percentage / 100);
      }
  }
  ```
- **New Without Parentheses**: Instantiate and immediately invoke methods or access properties.
  ```php
  $result = new RequestHandler()->handle($request);
  $name = new ReflectionClass(Order::class)->getShortName();
  ```
- **Array Find Functions**: Native collection search utilities.
  ```php
  $items = [
      ['id' => 1, 'active' => false],
      ['id' => 2, 'active' => true],
      ['id' => 3, 'active' => true],
  ];

  $firstActive = array_find($items, fn(array $item) => $item['active']);
  $activeKey   = array_find_key($items, fn(array $item) => $item['active']);
  $hasActive   = array_any($items, fn(array $item) => $item['active']);
  $allActive   = array_all($items, fn(array $item) => $item['active']);
  ```
- **`#[\Deprecated]` Attribute**: Native attribute declaring deprecated elements with optional message and replacement version.
  ```php
  #[\Deprecated(message: 'Use findById() instead', since: '2.0.0')]
  public function get(int $id): ?Entity
  {
      return $this->findById($id);
  }
  ```

---

## 2. Composer.json Best Practices

### Hardened Production `composer.json` Template
```json
{
  "name": "vendor-name/package-name",
  "description": "Production-grade modern PHP package",
  "type": "project",
  "license": "MIT",
  "require": {
    "php": "~8.3.0 || ~8.4.0",
    "psr/http-message": "^2.0",
    "psr/http-server-handler": "^1.0",
    "psr/log": "^3.0"
  },
  "require-dev": {
    "phpstan/phpstan": "^1.12",
    "phpunit/phpunit": "^11.3",
    "pestphp/pest": "^3.0",
    "friendsofphp/php-cs-fixer": "^3.64",
    "vimeo/psalm": "^5.26"
  },
  "autoload": {
    "psr-4": {
      "VendorName\\PackageName\\": "src/"
    },
    "files": [
      "src/functions.php"
    ]
  },
  "autoload-dev": {
    "psr-4": {
      "VendorName\\PackageName\\Tests\\": "tests/"
    }
  },
  "config": {
    "sort-packages": true,
    "optimize-autoloader": true,
    "preferred-install": "dist",
    "platform": {
      "php": "8.3.0"
    },
    "allow-plugins": {
      "pestphp/pest-plugin": true
    }
  },
  "scripts": {
    "test": "pest --coverage",
    "analyse": "phpstan analyse -c phpstan.neon --memory-limit=1G",
    "format": "php-cs-fixer fix --dry-run --diff",
    "format:fix": "php-cs-fixer fix",
    "audit": "composer audit",
    "check": [
      "@format",
      "@analyse",
      "@test"
    ]
  }
}
```

### Essential Composer Commands
| Command | Purpose |
|---|---|
| `composer install --no-dev --optimize-autoloader` | Production installation with optimized classmap. |
| `composer dump-autoload -o -a` | Generates authoritative, optimized classmap (`-a` prevents filesystem fallback checks). |
| `composer audit` | Scans dependencies for known security vulnerabilities. |
| `composer outdated --direct` | Lists direct dependencies with available updates. |
| `composer validate --strict` | Validates `composer.json` syntax and lockfile consistency. |

---

## 3. Autoloading Patterns

### PSR-4 Directory Mapping
- Standard namespace to directory mapping maps namespace prefixes to relative paths:
  ```json
  "autoload": {
    "psr-4": {
      "App\\": "src/",
      "App\\Infrastructure\\": "src/Infrastructure/"
    }
  }
  ```
- File naming must match class name exactly (case-sensitive on Linux systems):
  - `App\Domain\Model\User` -> `src/Domain/Model/User.php`.
  - `App\Tests\Unit\UserTest` -> `tests/Unit/UserTest.php`.

### Classmap Optimization
- During development: Composer searches the filesystem for PSR-4 classes.
- In production, run `composer dump-autoload --classmap-authoritative` (`-a`). Composer builds a single static dictionary of class names to paths. If a class is not in the classmap, Composer throws immediately without checking disk, reducing file I/O latency.

---

## 4. Design Patterns in Modern PHP

### Value Object Pattern
Immutable, self-validating, compared by equality of value rather than identity.
```php
declare(strict_types=1);

namespace App\Domain\ValueObject;

use InvalidArgumentException;

final readonly class EmailAddress
{
    public string $value;

    public function __construct(string $rawEmail)
    {
        $filtered = filter_var(trim($rawEmail), FILTER_VALIDATE_EMAIL);
        if ($filtered === false) {
            throw new InvalidArgumentException(sprintf('Invalid email address: "%s"', $rawEmail));
        }

        $this->value = mb_strtolower($filtered);
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }

    public function domain(): string
    {
        return substr(strrchr($this->value, '@') ?: '', 1);
    }

    public function __toString(): string
    {
        return $this->value;
    }
}
```

---

### Repository Pattern with PDO
Abstract data persistence behind a clean domain interface.
```php
declare(strict_types=1);

namespace App\Domain\Repository;

use App\Domain\Model\User;

interface UserRepositoryInterface
{
    public function findById(int $id): ?User;
    public function findByEmail(string $email): ?User;
    public function save(User $user): void;
    public function delete(int $id): bool;
}
```

```php
declare(strict_types=1);

namespace App\Infrastructure\Persistence;

use App\Domain\Model\User;
use App\Domain\Repository\UserRepositoryInterface;
use PDO;

final readonly class PdoUserRepository implements UserRepositoryInterface
{
    public function __construct(
        private PDO $pdo,
    ) {}

    #[\Override]
    public function findById(int $id): ?User
    {
        $stmt = $this->pdo->prepare('SELECT id, name, email, created_at FROM users WHERE id = :id LIMIT 1');
        $stmt->execute(['id' => $id]);
        
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row === false) {
            return null;
        }

        return $this->hydrate($row);
    }

    #[\Override]
    public function findByEmail(string $email): ?User
    {
        $stmt = $this->pdo->prepare('SELECT id, name, email, created_at FROM users WHERE email = :email LIMIT 1');
        $stmt->execute(['email' => $email]);
        
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row === false) {
            return null;
        }

        return $this->hydrate($row);
    }

    #[\Override]
    public function save(User $user): void
    {
        if ($user->id === null) {
            $stmt = $this->pdo->prepare(
                'INSERT INTO users (name, email, created_at) VALUES (:name, :email, :created_at)'
            );
            $stmt->execute([
                'name' => $user->name,
                'email' => $user->email,
                'created_at' => $user->createdAt->format('Y-m-d H:i:s'),
            ]);
            $user->assignId((int) $this->pdo->lastInsertId());
            return;
        }

        $stmt = $this->pdo->prepare(
            'UPDATE users SET name = :name, email = :email WHERE id = :id'
        );
        $stmt->execute([
            'id' => $user->id,
            'name' => $user->name,
            'email' => $user->email,
        ]);
    }

    #[\Override]
    public function delete(int $id): bool
    {
        $stmt = $this->pdo->prepare('DELETE FROM users WHERE id = :id');
        $stmt->execute(['id' => $id]);
        return $stmt->rowCount() > 0;
    }

    /**
     * @param array{id: int|numeric-string, name: string, email: string, created_at: string} $row
     */
    private function hydrate(array $row): User
    {
        return new User(
            id: (int) $row['id'],
            name: $row['name'],
            email: $row['email'],
            createdAt: new \DateTimeImmutable($row['created_at']),
        );
    }
}
```

---

### Strategy Pattern (Enum-Backed)
Leverage PHP 8 Backed Enums with matching execution strategies.
```php
declare(strict_types=1);

namespace App\Domain\Payment;

interface PaymentProcessorInterface
{
    public function charge(float $amount, string $currency): string;
}

final readonly class StripeProcessor implements PaymentProcessorInterface
{
    public function charge(float $amount, string $currency): string
    {
        return "stripe_ch_{$amount}_{$currency}";
    }
}

final readonly class PayPalProcessor implements PaymentProcessorInterface
{
    public function charge(float $amount, string $currency): string
    {
        return "paypal_pay_{$amount}_{$currency}";
    }
}

enum PaymentMethod: string
{
    case Stripe = 'stripe';
    case PayPal = 'paypal';

    public function createProcessor(): PaymentProcessorInterface
    {
        return match ($this) {
            self::Stripe => new StripeProcessor(),
            self::PayPal => new PayPalProcessor(),
        };
    }
}
```

---

### Pipeline / Middleware Pattern (PSR-15 Compatible)
Process requests or commands sequentially through a chain of handlers.
```php
declare(strict_types=1);

namespace App\Infrastructure\Http;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface;

final readonly class Pipeline implements RequestHandlerInterface
{
    /**
     * @param array<MiddlewareInterface> $middlewares
     */
    public function __construct(
        private RequestHandlerInterface $fallbackHandler,
        private array $middlewares = [],
    ) {}

    #[\Override]
    public function handle(ServerRequestInterface $request): ResponseInterface
    {
        return $this->resolve(0)->handle($request);
    }

    private function resolve(int $index): RequestHandlerInterface
    {
        if (!isset($this->middlewares[$index])) {
            return $this->fallbackHandler;
        }

        $middleware = $this->middlewares[$index];
        $next = $this->resolve($index + 1);

        return new class($middleware, $next) implements RequestHandlerInterface {
            public function __construct(
                private MiddlewareInterface $middleware,
                private RequestHandlerInterface $next,
            ) {}

            public function handle(ServerRequestInterface $request): ResponseInterface
            {
                return $this->middleware->process($request, $this->next);
            }
        };
    }
}
```

---

### Result / Either Pattern for Domain Errors
Avoid using heavy exceptions for expected domain branch failures.
```php
declare(strict_types=1);

namespace App\Domain\Shared;

/**
 * @template T
 * @template E
 */
final readonly class Result
{
    /**
     * @param T|null $value
     * @param E|null $error
     */
    private function __construct(
        public bool $isSuccess,
        private mixed $value = null,
        private mixed $error = null,
    ) {}

    /**
     * @template TVal
     * @param TVal $value
     * @return self<TVal, never>
     */
    public static function ok(mixed $value): self
    {
        return new self(isSuccess: true, value: $value);
    }

    /**
     * @template TErr
     * @param TErr $error
     * @return self<never, TErr>
     */
    public static function fail(mixed $error): self
    {
        return new self(isSuccess: false, error: $error);
    }

    /**
     * @return T
     */
    public function unwrap(): mixed
    {
        if (!$this->isSuccess) {
            throw new \RuntimeException('Attempted to unwrap a failed Result');
        }
        return $this->value;
    }

    /**
     * @return E
     */
    public function getError(): mixed
    {
        if ($this->isSuccess) {
            throw new \RuntimeException('Attempted to get error from successful Result');
        }
        return $this->error;
    }
}
```

---

## 5. Error Handling Patterns

### Converting PHP Errors, Warnings, and Notices to Exceptions
Configure error handlers at application bootstrap so warnings and notices do not fail silently.
```php
declare(strict_types=1);

namespace App\Bootstrap;

use ErrorException;

final class ErrorBootstrapper
{
    public static function register(): void
    {
        error_reporting(E_ALL);

        set_error_handler(
            static function (int $severity, string $message, string $file, int $line): bool {
                if (!(error_reporting() & $severity)) {
                    // Suppressed by @ operator
                    return false;
                }
                throw new ErrorException($message, 0, $severity, $file, $line);
            }
        );

        set_exception_handler(
            static function (\Throwable $exception): void {
                $payload = [
                    'error' => $exception->getMessage(),
                    'type'  => $exception::class,
                    'file'  => $exception->getFile(),
                    'line'  => $exception->getLine(),
                ];
                
                error_log(json_encode($payload, JSON_THROW_ON_ERROR));
                
                if (php_sapi_name() !== 'cli') {
                    http_response_code(500);
                    header('Content-Type: application/json; charset=UTF-8');
                    echo json_encode(['error' => 'Internal Server Error'], JSON_THROW_ON_ERROR);
                }
                exit(1);
            }
        );
    }
}
```

### Domain Exception Hierarchy
Structure exceptions by responsibility so callers can catch granular, predictable errors.
```php
declare(strict_types=1);

namespace App\Domain\Exception;

interface DomainExceptionInterface extends \Throwable {}

class DomainException extends \RuntimeException implements DomainExceptionInterface {}

final class EntityNotFoundException extends DomainException
{
    public static function forId(string $entityName, int|string $id): self
    {
        return new self(sprintf('%s with ID "%s" was not found.', $entityName, (string) $id), 404);
    }
}

final class BusinessRuleViolationException extends DomainException
{
    public static function insufficientBalance(float $requested, float $available): self
    {
        return new self(sprintf('Requested amount %0.2f exceeds available balance %0.2f.', $requested, $available), 422);
    }
}
```

---

## 6. Database Access Patterns (PDO)

### Production PDO Connection Factory
```php
declare(strict_types=1);

namespace App\Infrastructure\Database;

use PDO;
use SensitiveParameter;

final class PdoConnectionFactory
{
    public static function create(
        string $host,
        int $port,
        string $database,
        string $username,
        #[\SensitiveParameter] string $password,
        string $charset = 'utf8mb4',
    ): PDO {
        $dsn = sprintf('mysql:host=%s;port=%d;dbname=%s;charset=%s', $host, $port, $database, $charset);

        $options = [
            // Always throw PDOException on error
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            // Fetch associative arrays by default
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            // Turn off emulation mode for genuine prepared statements
            PDO::ATTR_EMULATE_PREPARES   => false,
            // Keep connection open or persistent only if tested
            PDO::ATTR_PERSISTENT         => false,
            // Stringify numbers off to maintain native scalar types
            PDO::ATTR_STRINGIFY_FETCHES  => false,
        ];

        return new PDO($dsn, $username, $password, $options);
    }
}
```

### Transaction Management Wrapper
Safely execute database operations within an atomic transaction.
```php
declare(strict_types=1);

namespace App\Infrastructure\Database;

use PDO;
use Throwable;

final readonly class TransactionManager
{
    public function __construct(private PDO $pdo) {}

    /**
     * @template T
     * @param callable(PDO): T $callback
     * @return T
     * @throws Throwable
     */
    public function transactional(callable $callback): mixed
    {
        if ($this->pdo->inTransaction()) {
            return $callback($this->pdo);
        }

        $this->pdo->beginTransaction();

        try {
            $result = $callback($this->pdo);
            $this->pdo->commit();
            return $result;
        } catch (Throwable $e) {
            $this->pdo->rollBack();
            throw $e;
        }
    }
}
```

### Memory-Efficient Streaming with Generators
Fetch millions of records using PDO unbuffered queries or generators to maintain constant low memory usage.
```php
declare(strict_types=1);

namespace App\Infrastructure\Database;

use Generator;
use PDO;

final readonly class RecordStreamer
{
    public function __construct(private PDO $pdo) {}

    /**
     * @param string $query
     * @param array<string, mixed> $params
     * @return Generator<int, array<string, mixed>>
     */
    public function stream(string $query, array $params = []): Generator
    {
        $stmt = $this->pdo->prepare($query);
        $stmt->execute($params);

        $index = 0;
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            yield $index++ => $row;
        }
    }
}
```
