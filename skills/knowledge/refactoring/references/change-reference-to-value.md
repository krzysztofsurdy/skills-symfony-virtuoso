## Overview

Change Reference to Value transforms a mutable, identity-based reference object into an immutable value object whose equality depends on its contents. Use this when objects are fundamentally defined by the data they carry rather than by which particular instance you are holding.

## Motivation

Object-oriented systems distinguish between two kinds of objects:

- **Reference objects**: Identity is paramount. Two objects containing identical data remain distinct entities.
- **Value objects**: Data is paramount. Two objects holding the same data are fully interchangeable.

Consider this refactoring when:

1. The object is compact and has no meaningful mutable state
2. Code throughout the system compares objects by their data rather than their identity
3. Multiple independent instances carry duplicate data
4. Identity-based semantics introduce confusion or hard-to-trace bugs
5. You require reliable, content-driven equality checks

## Mechanics

### Before Refactoring

1. Identify a reference object that should behave as a value
2. Verify it has few fields and no state that legitimately changes
3. Review every place the object is instantiated and compared

### Steps to Refactor

1. Lock down mutability by removing setters and declaring properties as final or readonly
2. Implement content-based equality (for example, an `equals()` method or PHP 8.1+ readonly semantics)
3. Provide hashing support if the object will live inside hash-based collections
4. Swap any identity comparisons (`===`) for equality method calls
5. Offer factory or constructor-based creation; remove mutation methods
6. Eliminate any leftover mutable operations

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

- **Reliable Equality**: Comparisons reflect actual data instead of object identity
- **Immutability Guarantees**: Preventing mutation eliminates an entire category of state-related bugs
- **Shareability and Caching**: Immutable value objects can be passed around and cached without risk
- **Expressive Semantics**: The code clearly conveys that two objects with matching data are equivalent
- **Language-Level Enforcement**: Readonly properties enforce immutability at compile time
- **Straightforward Testing**: Tests check data values without needing to track specific instances

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
