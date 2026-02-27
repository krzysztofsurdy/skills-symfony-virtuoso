## Overview

Replace Type Code with Class removes magic numbers and strings that represent distinct categories or statuses by converting them into enumeration types or dedicated classes. This refactoring strengthens type safety, improves code readability, and shifts validation from runtime conditionals to compile-time checks.

## Motivation

### When to Apply

- **Raw numeric or string codes**: Using integer codes (1, 2, 3) or string literals ('active', 'pending', 'inactive') to represent types
- **Repeated validation**: Checking whether a value matches the expected set of codes in multiple places
- **Scattered definitions**: Type code constants defined in different locations instead of a single authoritative source
- **Missing IDE assistance**: The IDE cannot offer autocompletion or safe renaming for plain strings or integers
- **Domain richness**: Different statuses or categories carry validation rules and associated behavior

### Why It Matters

Primitive type codes offer no protection against invalid values. Replacing them with enums or dedicated types gives you compile-time guarantees, eliminates illegal state transitions, enables IDE tooling, and makes the code's purpose clear through meaningful type names.

## Mechanics: Step-by-Step

1. **Catalog type codes**: Locate every magic number or string that represents a distinct category
2. **Define an enum or class**: PHP 8.1+ enums are the natural choice for straightforward type codes
3. **Enumerate all values**: Ensure every valid code has a corresponding enum case
4. **Replace primitive fields**: Change variables that store type codes to the new enum type
5. **Update signatures**: Switch method parameter and return types from int/string to the enum
6. **Strip manual validation**: Remove conditional checks that verify type code validity
7. **Attach behavior**: Migrate type-specific logic into methods on the enum or class
8. **Run the test suite**: Confirm that all transitions and validations still function correctly

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class User
{
    private int $status; // Magic number: 1=active, 2=inactive, 3=pending
    private string $role; // Magic string: 'admin', 'user', 'guest'

    public function __construct(int $status, string $role)
    {
        // Manual validation
        if (!in_array($status, [1, 2, 3], true)) {
            throw new InvalidArgumentException('Invalid status code: ' . $status);
        }
        if (!in_array($role, ['admin', 'user', 'guest'], true)) {
            throw new InvalidArgumentException('Invalid role: ' . $role);
        }

        $this->status = $status;
        $this->role = $role;
    }

    public function isActive(): bool
    {
        return $this->status === 1; // Magic number comparison
    }

    public function getStatusLabel(): string
    {
        return match($this->status) {
            1 => 'Active',
            2 => 'Inactive',
            3 => 'Pending',
            default => 'Unknown'
        };
    }

    public function canAccessAdmin(): bool
    {
        return $this->role === 'admin'; // String comparison
    }

    public function setStatus(int $status): void
    {
        if (!in_array($status, [1, 2, 3], true)) {
            throw new InvalidArgumentException('Invalid status');
        }
        $this->status = $status;
    }

    public function getStatus(): int
    {
        return $this->status; // Returns magic number
    }
}

// Usage scattered across codebase
$user = new User(1, 'admin');
if ($user->getStatus() === 1) {
    // Active user logic
}
$user->setStatus(2); // What does 2 mean?
```

## After: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

enum UserStatus: int
{
    case Active = 1;
    case Inactive = 2;
    case Pending = 3;

    public function label(): string
    {
        return match($this) {
            self::Active => 'Active',
            self::Inactive => 'Inactive',
            self::Pending => 'Pending',
        };
    }

    public function isActive(): bool
    {
        return $this === self::Active;
    }
}

enum UserRole: string
{
    case Admin = 'admin';
    case User = 'user';
    case Guest = 'guest';

    public function canAccessAdmin(): bool
    {
        return $this === self::Admin;
    }

    public function permissions(): array
    {
        return match($this) {
            self::Admin => ['read', 'write', 'delete'],
            self::User => ['read', 'write'],
            self::Guest => ['read'],
        };
    }
}

class User
{
    public function __construct(
        private UserStatus $status,
        private UserRole $role,
    ) {}

    public function isActive(): bool
    {
        return $this->status->isActive();
    }

    public function getStatusLabel(): string
    {
        return $this->status->label();
    }

    public function canAccessAdmin(): bool
    {
        return $this->role->canAccessAdmin();
    }

    public function setStatus(UserStatus $status): void
    {
        $this->status = $status; // Type-safe, no validation needed
    }

    public function getStatus(): UserStatus
    {
        return $this->status; // Returns meaningful enum type
    }

    public function getRole(): UserRole
    {
        return $this->role;
    }
}

// Usage is now clear and type-safe
$user = new User(UserStatus::Active, UserRole::Admin);
if ($user->getStatus() === UserStatus::Active) {
    // IDE knows exactly what we're checking
}
$user->setStatus(UserStatus::Pending); // Type-safe assignment
$permissions = $user->getRole()->permissions(); // IDE autocomplete available
```

## Benefits

- **Type safety**: The compiler and IDE prevent invalid type assignments at development time
- **Self-documenting**: Enum case names replace opaque numbers; intent is immediately obvious
- **IDE tooling**: Autocompletion, jump-to-definition, and rename support work out of the box
- **No manual validation**: The type system itself enforces that only valid values are used
- **Compile-time checking**: Invalid values are caught before the code ever runs
- **Encapsulated behavior**: Type-related logic lives directly on the enum methods
- **Fewer bugs**: It becomes impossible to accidentally assign an invalid code value
- **Centralized changes**: Modifying the set of allowed values requires editing only the enum definition

## When NOT to Use

- **Truly dynamic values**: Type codes originating from external APIs that change unpredictably
- **User-defined categories**: When end users can create new types at runtime
- **Huge numeric ranges**: Thousands of possible values are better served by a database lookup
- **Legacy integration**: When refactoring would force extensive downstream changes in external systems
- **Strict compatibility**: When third-party code mandates raw string or integer types

## Related Refactorings

- **Replace Data Value with Object**: For cases requiring richer behavior than a simple enum
- **Extract Class**: When type codes need their own associated data and methods
- **Replace Conditional with Polymorphism**: To replace type-based conditionals with polymorphic dispatch
- **Introduce Parameter Object**: For bundling related type codes into a single parameter
- **Self Encapsulate Field**: For adding validation to primitive type code fields before upgrading to an enum
