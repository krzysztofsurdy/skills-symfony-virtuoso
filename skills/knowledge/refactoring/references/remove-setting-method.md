# Remove Setting Method

## Overview

Remove Setting Method deletes setter methods for fields whose values should be established at construction time and never changed afterward. By eliminating the setter, the class communicates that the field is fixed once the object is created, preventing accidental or unauthorized mutations later in the object's lifecycle.

## Motivation

A setter method that exists but should never be called after initialization creates a misleading API. Its presence signals that the field is mutable, encouraging code that modifies the value at arbitrary points. This leads to:

- Unintended state changes that violate the object's design assumptions
- Ambiguity about whether a field is meant to be stable or fluid
- Harder-to-trace bugs when distant code alters a supposedly fixed value
- A gap between the API's promise and the object's actual contract

Removing the setter and initializing the field through the constructor makes immutability explicit and enforceable.

## Mechanics

1. **Identify immutable fields** - Locate fields that should never change after object construction
2. **Update the constructor** - Ensure the constructor accepts parameters for initializing these fields
3. **Find setter invocations** - Search for all calls to the setter method throughout the codebase
4. **Replace setter calls** - Move initialization to the constructor call instead
5. **Remove the setter** - Delete the setter method definition
6. **Verify immutability** - Confirm no other code attempts to modify these fields

## Before/After Example

### Before (PHP 8.3+)

```php
class Account
{
    private string $accountNumber;
    private string $accountHolder;
    private float $balance = 0.0;

    public function __construct()
    {
    }

    public function setAccountNumber(string $number): void
    {
        $this->accountNumber = $number;
    }

    public function setAccountHolder(string $holder): void
    {
        $this->accountHolder = $holder;
    }

    public function getAccountNumber(): string
    {
        return $this->accountNumber;
    }

    public function getAccountHolder(): string
    {
        return $this->accountHolder;
    }

    public function getBalance(): float
    {
        return $this->balance;
    }
}

// Usage
$account = new Account();
$account->setAccountNumber('ACC-12345');
$account->setAccountHolder('John Doe');
```

### After (PHP 8.3+)

```php
class Account
{
    public function __construct(
        private readonly string $accountNumber,
        private readonly string $accountHolder,
        private float $balance = 0.0,
    ) {
    }

    public function getAccountNumber(): string
    {
        return $this->accountNumber;
    }

    public function getAccountHolder(): string
    {
        return $this->accountHolder;
    }

    public function getBalance(): float
    {
        return $this->balance;
    }
}

// Usage
$account = new Account('ACC-12345', 'John Doe');
```

## Benefits

- **Guaranteed stability** - `readonly` properties make post-construction mutation impossible at the language level
- **Explicit dependencies** - Required constructor parameters declare what the object needs upfront
- **Smaller API** - Fewer methods to learn, test, and maintain
- **Trustworthy contracts** - Callers know the object will not change out from under them
- **Simplified reasoning** - Immutable state eliminates an entire class of temporal bugs
- **Modern PHP alignment** - Takes advantage of constructor promotion and the `readonly` modifier

## When NOT to Use

- **Legitimate mutability needed** - If the field's value legitimately needs to change, keep the setter
- **Optional initialization** - If the field is truly optional and might be set later, a setter may be appropriate
- **Framework requirements** - Some frameworks require setter methods for serialization or data mapping
- **Lazy initialization** - If values are calculated on first access, setters may still be useful
- **Object evolution** - If the object is meant to evolve through multiple state changes, setters serve a purpose

## Related Refactorings

- **Introduce Parameter Object** - Group multiple constructor parameters into dedicated objects
- **Change Reference to Value** - Often paired with this refactoring for immutable value objects
- **Replace Constructor with Factory Method** - Provides alternative initialization patterns
- **Introduce Builder** - For complex objects with many optional initialization parameters
