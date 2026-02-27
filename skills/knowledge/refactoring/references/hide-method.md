## Overview

Hide Method narrows the visibility of a method that no external class uses. When a method serves only as an internal implementation detail, making it private or protected shrinks the public surface of the class and signals its true role.

## Motivation

As a class evolves, methods that were initially public may lose their external callers. Leaving them public exposes implementation details and bloats the interface that consumers must understand. Restricting visibility:

- Shrinks the public API, making the class easier to learn and use
- Shields internals from accidental or inappropriate external calls
- Increases freedom to refactor without worrying about breaking dependents
- Makes the intended contract of the class unmistakable

## Mechanics

1. **Find candidates**: Use static analysis or IDE tooling to locate public methods with no external callers that are not part of an interface or abstract contract
2. **Confirm with tests**: Run the test suite to verify no external code relies on the method
3. **Reduce visibility**: Change the access modifier from public to private (or protected if subclasses need it)
4. **Run tests again**: Ensure everything still passes

## Before/After (PHP 8.3+)

### Before
```php
class UserRepository
{
    public function findByEmail(string $email): ?User
    {
        return $this->validateAndFetch($email);
    }

    // Only used internally, but public
    public function validateAndFetch(string $email): ?User
    {
        $this->validateEmail($email);
        return $this->query('SELECT * FROM users WHERE email = ?', [$email])->first();
    }

    public function validateEmail(string $email): void
    {
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email format');
        }
    }

    private function query(string $sql, array $params = []): Collection
    {
        // Database query logic
        return new Collection();
    }
}

// External usage
$repo = new UserRepository();
$user = $repo->findByEmail('user@example.com');
// $repo->validateAndFetch(); // This shouldn't be called directly
```

### After
```php
class UserRepository
{
    public function findByEmail(string $email): ?User
    {
        return $this->validateAndFetch($email);
    }

    // Now private - implementation detail
    private function validateAndFetch(string $email): ?User
    {
        $this->validateEmail($email);
        return $this->query('SELECT * FROM users WHERE email = ?', [$email])->first();
    }

    private function validateEmail(string $email): void
    {
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email format');
        }
    }

    private function query(string $sql, array $params = []): Collection
    {
        // Database query logic
        return new Collection();
    }
}

// External usage - unchanged and cleaner
$repo = new UserRepository();
$user = $repo->findByEmail('user@example.com');
```

## Benefits

- **Simpler Maintenance**: Private methods can be renamed or restructured without affecting external code
- **Obvious Contract**: The public interface shows exactly what the class is designed to do
- **Lower Coupling**: Fewer public methods means fewer hooks for external code to latch onto
- **Stronger Encapsulation**: Internal implementation stays hidden from consumers
- **Better IDE Experience**: Autocomplete lists only the methods that matter

## When NOT to Use

- **Interface contracts**: Methods that fulfill an interface or abstract declaration must stay public
- **Template Method pattern**: Override hooks intended for subclasses should be protected, not private
- **External dependencies**: If legacy or third-party code depends on the method, use protected as a transition step
- **Framework requirements**: Some frameworks rely on method visibility for reflection, proxying, or event dispatching

## Related Refactorings

- **Extract Method**: Often creates methods that should then be hidden
- **Remove Dead Code**: Goes further by removing methods that have no callers at all
- **Encapsulate Field**: Applies the same visibility principle to class fields
- **Move Method**: Relocates a private method to a class where it fits better
