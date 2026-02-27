## Overview

Change Reference to Value converts an identity-based, mutable reference object into an immutable value object whose equality is determined by its content. Apply this when objects are logically defined by their data rather than by which specific instance you hold.

## Motivation

Objects in object-oriented systems fall into two broad categories:

- **Reference objects**: Identity is what matters. Two objects with the same data are still distinct entities.
- **Value objects**: Content is what matters. Two objects holding the same data are interchangeable.

Consider this refactoring when:

1. The object is small and naturally immutable
2. Comparisons throughout the codebase are based on content, not identity
3. Many separate instances carry identical data
4. Identity-based semantics cause confusion or lead to subtle bugs
5. You need predictable, content-based equality checks

## Mechanics

### Before Refactoring

1. Locate a reference object that would be better treated as a value
2. Confirm it has a small number of fields and no meaningful mutable state
3. Audit every place the object is created and compared

### Steps to Refactor

1. Make the class immutable by removing setters and marking properties as final/readonly
2. Implement content-based equality (e.g., an `equals()` method or PHP 8.1+ readonly semantics)
3. Add hashing support if the object will be stored in hash-based collections
4. Replace any identity comparisons (`===`) with equality method calls
5. Provide factory or constructor-based creation; remove mutation methods
6. Eliminate any remaining mutable operations

## Before/After PHP 8.3+ Code

### Before: Reference Object

```php
class Money
{
    private string $currency;
    private float $amount;

    public function __construct(string $currency, float $amount)
    {
        $this->currency = $currency;
        $this->amount = $amount;
    }

    public function getCurrency(): string
    {
        return $this->currency;
    }

    public function setCurrency(string $currency): void
    {
        $this->currency = $currency;
    }

    public function getAmount(): float
    {
        return $this->amount;
    }

    public function setAmount(float $amount): void
    {
        $this->amount = $amount;
    }
}

// Usage with identity comparison
$wallet1 = new Money('USD', 100.00);
$wallet2 = new Money('USD', 100.00);

if ($wallet1 === $wallet2) {  // False - different objects
    echo "Same money";
}

if ($wallet1 == $wallet2) {  // False - no __equals implementation
    echo "Equivalent money";
}
```

### After: Value Object (PHP 8.3+)

```php
final readonly class Money
{
    public function __construct(
        public string $currency,
        public float $amount,
    ) {
        if ($amount < 0) {
            throw new InvalidArgumentException('Amount cannot be negative');
        }
    }

    public function equals(Money $other): bool
    {
        return $this->currency === $other->currency
            && $this->amount === $other->amount;
    }

    public function add(Money $other): Money
    {
        if ($this->currency !== $other->currency) {
            throw new InvalidArgumentException('Cannot add different currencies');
        }
        return new Money($this->currency, $this->amount + $other->amount);
    }

    public function __toString(): string
    {
        return sprintf('%s %.2f', $this->currency, $this->amount);
    }

    public function __hash(): string
    {
        return hash('sha256', $this->currency . '|' . $this->amount);
    }
}

// Usage with value comparison
$wallet1 = new Money('USD', 100.00);
$wallet2 = new Money('USD', 100.00);

if ($wallet1->equals($wallet2)) {  // True - same value
    echo "Equivalent money";
}

// Safe to use in collections
$moneySet = [$wallet1, $wallet2];  // Duplicates are identical values
```

### Alternative: PHP 8.1+ with enum or backed enum

```php
enum Currency: string
{
    case USD = 'USD';
    case EUR = 'EUR';
    case GBP = 'GBP';
}

final readonly class Money
{
    public function __construct(
        public Currency $currency,
        public float $amount,
    ) {}

    public function equals(Money $other): bool
    {
        return $this->currency === $other->currency
            && $this->amount === $other->amount;
    }
}
```

## Benefits

- **Predictable Equality**: Comparisons reflect data content rather than object identity
- **Safety through Immutability**: Ruling out mutation prevents a wide class of state-related bugs
- **Caching and Reuse**: Immutable value objects can be freely shared and cached
- **Clear Semantics**: The code communicates that two objects with the same data are equivalent
- **Compile-Time Guarantees**: Readonly properties enforce immutability at the language level
- **Simple Testing**: Tests verify data values without tracking specific object instances

## When NOT to Use

- The object has state that legitimately changes over its lifetime
- Object identity is central to the domain (entities like User or Order)
- The object holds references to other mutable objects
- You rely on polymorphic behavior through inheritance hierarchies
- The object participates in lifecycle management that requires tracking
- Object creation cost is significant and reuse via reference is important

## Related Refactorings

- **Replace Data Class with Object** (the opposite direction)
- **Extract Value Object** - Carve out immutable concerns into standalone value classes
- **Replace Type Code with Enum** - Use enums for value objects with a fixed set of options
- **Remove Setting Method** - A prerequisite step toward immutability
- **Introduce Parameter Object** - Bundle multiple parameters into a single value object
