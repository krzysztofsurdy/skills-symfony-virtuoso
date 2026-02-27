# Singleton Pattern

## Overview

The Singleton pattern is a creational design pattern that restricts a class to exactly one instance while exposing a well-known access point for it. It merges instantiation control with global reachability, guaranteeing that a single object of a given class exists for the entire lifetime of the application.

## Intent

- Guarantee that only one instance of a class is ever created
- Expose a single, globally accessible entry point to that instance
- Centralize the management of a shared resource behind controlled instantiation
- Defer creation of expensive resources until the moment they are first requested
- Block uncontrolled proliferation of duplicate instances

## Problem & Solution

### Problem

Certain application resources must exist as a single, shared object:

1. **Uncontrolled Instantiation**: Without safeguards, any part of the codebase can spin up new instances, leading to conflicting state
2. **Resource Waste**: Duplicating expensive objects like database connections or logger instances burns memory and handles for no benefit
3. **State Inconsistency**: When different modules hold separate instances, their internal state drifts apart, causing subtle synchronization bugs
4. **Scattered Access**: Without a centralized accessor, code that needs the shared resource must thread it through constructors and method signatures everywhere

### Solution

Design the class so it manages its own instantiation:
1. Make the constructor private so external code cannot call `new`
2. Store a static reference to the sole instance inside the class itself
3. Provide a public static method that returns this reference, creating it on first call
4. Optionally use lazy initialization to defer construction until first access

## Structure

```
Client Code
    ↓
    getInstance() (static method)
    ↓
Singleton
├── static instance: Singleton
├── private constructor
└── static getInstance(): Singleton
```

## When to Use

- **Logging Frameworks**: A single logger shared by every component in the system
- **Database Connections**: One connection pool or primary connection managed centrally
- **Configuration Managers**: Application-wide settings served from a single authoritative source
- **Caching Systems**: A unified cache that all consumers read from and write to
- **Session Managers**: Centralized session tracking across the request lifecycle
- **Thread Pools/Executors**: One pool governing all asynchronous task scheduling
- **Resource Pools**: Controlled allocation of scarce resources like file handles or network sockets

## Implementation

### PHP 8.3+ Example: Database Connection Singleton

```php
<?php
declare(strict_types=1);

readonly class DatabaseConnection {
    private static ?self $instance = null;
    private PDO $connection;

    // Private constructor prevents external instantiation
    private function __construct() {
        $this->connection = new PDO(
            'mysql:host=localhost;dbname=app',
            'user',
            'password'
        );
    }

    // Global access point to the single instance
    public static function getInstance(): self {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    // Prevent cloning
    private function __clone(): void {}

    // Prevent unserialization
    public function __wakeup(): void {
        throw new Error('Cannot unserialize a Singleton instance');
    }

    public function query(string $sql): array {
        return $this->connection->query($sql)->fetchAll(PDO::FETCH_ASSOC);
    }

    public function execute(string $sql, array $params = []): bool {
        $stmt = $this->connection->prepare($sql);
        return $stmt->execute($params);
    }
}

// Usage
$db1 = DatabaseConnection::getInstance();
$db2 = DatabaseConnection::getInstance();
// $db1 === $db2 (same instance)

$results = $db1->query('SELECT * FROM users');
```

### Logger Singleton with Static Factory

```php
<?php
declare(strict_types=1);

readonly class Logger {
    private static ?self $instance = null;
    private string $logFile;

    private function __construct() {
        $this->logFile = dirname(__DIR__) . '/logs/app.log';
        if (!is_dir(dirname($this->logFile))) {
            mkdir(dirname($this->logFile), 0755, true);
        }
    }

    public static function getInstance(): self {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __clone(): void {}
    public function __wakeup(): void {
        throw new Error('Cannot unserialize Logger');
    }

    public function log(string $message, string $level = 'INFO'): void {
        $timestamp = date('Y-m-d H:i:s');
        $logEntry = "[$timestamp] $level: $message\n";
        error_log($logEntry, 3, $this->logFile);
    }

    public function info(string $message): void {
        $this->log($message, 'INFO');
    }

    public function error(string $message): void {
        $this->log($message, 'ERROR');
    }

    public function warning(string $message): void {
        $this->log($message, 'WARNING');
    }
}

// Usage across the application
Logger::getInstance()->info('Application started');
Logger::getInstance()->error('An error occurred');
```

### Thread-Safe Singleton with Early Initialization

```php
<?php
declare(strict_types=1);

readonly class ConfigurationManager {
    private static self $instance;
    private array $config;

    private function __construct() {
        $this->config = $this->loadConfiguration();
    }

    // Static initializer (eager singleton)
    public static function init(): void {
        if (!isset(self::$instance)) {
            self::$instance = new self();
        }
    }

    public static function getInstance(): self {
        if (!isset(self::$instance)) {
            self::$init();
        }
        return self::$instance;
    }

    private function __clone(): void {}
    public function __wakeup(): void {
        throw new Error('Cannot unserialize ConfigurationManager');
    }

    private function loadConfiguration(): array {
        return require dirname(__DIR__) . '/config/app.php';
    }

    public function get(string $key, mixed $default = null): mixed {
        return $this->config[$key] ?? $default;
    }

    public function set(string $key, mixed $value): void {
        $this->config[$key] = $value;
    }

    public function all(): array {
        return $this->config;
    }
}

// Initialization
ConfigurationManager::init();

// Usage
$dbHost = ConfigurationManager::getInstance()->get('database.host');
```

## Real-World Analogies

**Government**: A nation has one government serving as the central authority. Citizens don't create alternative governments; they interact with the one that already exists through official channels.

**Company CEO**: An organization typically operates under a single chief executive. All strategic decisions funnel through that one person rather than through competing leadership.

**Printer Spooler**: An operating system runs one print spooler that queues jobs from every application. Programs submit work to the shared spooler rather than each spawning its own.

**Bank Account Registry**: A financial institution maintains one master ledger of accounts. Every transaction references this single registry to ensure consistent balances.

## Pros and Cons

### Advantages
- **Controlled Instance Count**: Guarantees exactly one object, simplifying shared-resource management
- **Convenient Global Access**: Provides a well-known entry point without threading references everywhere
- **Lazy Initialization**: The instance is created only when it is first requested
- **Thread Safety**: Can be implemented with synchronization primitives for concurrent environments
- **Centralized Control**: A single point of authority over instance creation and lifecycle
- **Memory Efficiency**: Only one instance occupies memory, no matter how many consumers exist

### Disadvantages
- **Global State**: Introduces hidden global state, complicating testing and debugging
- **Implicit Dependencies**: Consumers depend on the singleton without making that dependency visible in signatures
- **Testability Barriers**: Hard to substitute with mocks or stubs unless the design anticipates it
- **Concurrency Pitfalls**: Requires careful locking in multi-threaded contexts to avoid race conditions
- **Mixed Responsibilities**: The class manages both its domain logic and its own lifecycle
- **Tight Coupling**: Client code becomes bound to the specific singleton class rather than an abstraction

## Relations with Other Patterns

- **Facade**: Facades frequently use singletons to present a unified interface to subsystems
- **Factory Method**: A factory method can return a singleton as the sole product instance
- **Abstract Factory**: Concrete factory classes are often implemented as singletons
- **Observer**: Singleton registries commonly manage lists of registered observers
- **Service Locator**: This anti-pattern typically relies on a singleton to locate and return services
- **Dependency Injection**: The modern preferred alternative, injecting the single instance through constructors instead of accessing it globally

## Examples in Other Languages

### Java

```java
public class Singleton {
    private Singleton() {}

    private static class SingletonHolder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return SingletonHolder.INSTANCE;
    }
}
```

### C++

**Before: manual global pointer management**

```cpp
class GlobalClass {
    int m_value;
  public:
    GlobalClass(int v = 0) {
        m_value = v;
    }
    int get_value() {
        return m_value;
    }
    void set_value(int v) {
        m_value = v;
    }
};

GlobalClass *global_ptr = 0;

void foo(void) {
  if (!global_ptr)
    global_ptr = new GlobalClass;
  global_ptr->set_value(1);
  cout << "foo: global_ptr is " << global_ptr->get_value() << '\n';
}

void bar(void) {
  if (!global_ptr)
    global_ptr = new GlobalClass;
  global_ptr->set_value(2);
  cout << "bar: global_ptr is " << global_ptr->get_value() << '\n';
}

int main() {
  if (!global_ptr)
    global_ptr = new GlobalClass;
  cout << "main: global_ptr is " << global_ptr->get_value() << '\n';
  foo();
  bar();
}
```

**After: Singleton pattern with controlled access**

```cpp
class GlobalClass {
    int m_value;
    static GlobalClass *s_instance;
    GlobalClass(int v = 0) {
        m_value = v;
    }
  public:
    int get_value() {
        return m_value;
    }
    void set_value(int v) {
        m_value = v;
    }
    static GlobalClass *instance() {
        if (!s_instance)
          s_instance = new GlobalClass;
        return s_instance;
    }
};

GlobalClass *GlobalClass::s_instance = 0;

void foo(void) {
  GlobalClass::instance()->set_value(1);
  cout << "foo: global_ptr is " << GlobalClass::instance()->get_value() << '\n';
}

void bar(void) {
  GlobalClass::instance()->set_value(2);
  cout << "bar: global_ptr is " << GlobalClass::instance()->get_value() << '\n';
}

int main() {
  cout << "main: global_ptr is " << GlobalClass::instance()->get_value() << '\n';
  foo();
  bar();
}
```

### Python

```python
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class MyClass(metaclass=Singleton):
    """
    Example class.
    """
    pass


def main():
    m1 = MyClass()
    m2 = MyClass()
    assert m1 is m2


if __name__ == "__main__":
    main()
```
