## Overview

Move Method transfers a method from one class to another where it fits more naturally. When a method depends more heavily on the data or behavior of a different class than the one housing it, relocating the method brings it closer to its actual collaborators, tightening cohesion and loosening inter-class dependencies.

## Motivation

As codebases evolve, methods drift away from the data they operate on. Indicators that a method belongs elsewhere include:

- The method reads or writes fields of another class more than its own
- Most callers belong to a different class
- The method introduces unnecessary coupling between otherwise independent classes
- Keeping it in place violates the Single Responsibility Principle

Relocating the method to the class it interacts with most directly:

- Aligns behavior with the data it manipulates
- Cuts down on cross-class message traffic
- Strengthens encapsulation within each class
- Makes the code easier to navigate and reason about

## Mechanics

1. **Analyze dependencies**: Examine which class members and parameters the method uses
2. **Check visibility**: Ensure the method can be safely moved (check access permissions)
3. **Handle references**: Identify all places where the method is called
4. **Create in target class**: Define the method in the destination class with appropriate signature
5. **Update calls**: Replace calls from the source class with calls to the target class
6. **Remove original**: Delete the method from the source class
7. **Test thoroughly**: Ensure all functionality remains intact

## Before/After: PHP 8.3+ Example

### Before: Method in Wrong Class

```php
class Account
{
    private float $balance;
    private AccountType $type;

    public function __construct(float $balance, AccountType $type)
    {
        $this->balance = $balance;
        $this->type = $type;
    }

    // This method belongs in AccountType, not Account
    public function getInterestRate(): float
    {
        return match ($this->type->getName()) {
            'savings' => 0.05,
            'checking' => 0.01,
            'money_market' => 0.08,
            default => 0.0,
        };
    }

    public function calculateInterest(): float
    {
        return $this->balance * $this->getInterestRate();
    }
}

class AccountType
{
    private string $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }
}
```

### After: Method Moved to Target Class

```php
class Account
{
    private float $balance;
    private AccountType $type;

    public function __construct(float $balance, AccountType $type)
    {
        $this->balance = $balance;
        $this->type = $type;
    }

    public function calculateInterest(): float
    {
        return $this->balance * $this->type->getInterestRate();
    }
}

class AccountType
{
    private string $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    // Method moved here - it belongs with the data it uses
    public function getInterestRate(): float
    {
        return match ($this->name) {
            'savings' => 0.05,
            'checking' => 0.01,
            'money_market' => 0.08,
            default => 0.0,
        };
    }
}
```

### Advanced Example: Moving Complex Methods

```php
// Before: Complex validation in PaymentProcessor that belongs in Payment
class PaymentProcessor
{
    public function validatePayment(Payment $payment): bool
    {
        if ($payment->getAmount() <= 0) {
            return false;
        }
        if (empty($payment->getReference())) {
            return false;
        }
        if ($payment->getDate() > new DateTime()) {
            return false;
        }
        return true;
    }
}

// After: Validation moved to Payment class
class Payment
{
    private float $amount;
    private string $reference;
    private DateTime $date;

    public function isValid(): bool
    {
        if ($this->amount <= 0) {
            return false;
        }
        if (empty($this->reference)) {
            return false;
        }
        if ($this->date > new DateTime()) {
            return false;
        }
        return true;
    }
}

class PaymentProcessor
{
    public function process(Payment $payment): bool
    {
        return $payment->isValid();
    }
}
```

## Benefits

- **Stronger Encapsulation**: Methods sit alongside the data they depend on
- **Looser Coupling**: Classes become more self-contained and focused
- **Improved Navigability**: Related logic is easier to locate when it lives next to its data
- **Localized Changes**: Modifications to related functionality stay within a single class
- **Well-Defined Responsibilities**: Each class takes ownership of a coherent set of operations
- **Cleaner Public Interfaces**: APIs reflect genuine dependencies rather than historical accidents

## When NOT to Use

- When the method needs access to private members of the source class that can't be exposed
- When moving would create circular dependencies between classes
- When the method is part of a public API heavily used by external code
- When the target class is in a different layer of the application (violates layering)
- When the method logic is generic and truly belongs in a utility or base class

## Related Refactorings

- **Extract Method**: Break down complex methods before moving them
- **Extract Class**: If a class has too many responsibilities, extract a new class and move methods to it
- **Introduce Parameter Object**: When moving a method requires passing multiple parameters
- **Hide Delegate**: Reverse operation when you want to preserve the original interface
- **Replace Temp with Query**: Often used alongside moving methods to simplify data flow
