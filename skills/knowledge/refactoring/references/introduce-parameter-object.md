# Introduce Parameter Object

## Overview

Introduce Parameter Object bundles a recurring group of parameters into a dedicated object. When the same cluster of arguments appears across multiple method signatures, replacing them with a single object reduces duplication, clarifies intent, and opens the door for moving related behavior into the new class.

## Motivation

**The Problem**: Identical groups of parameters repeated across method signatures are a form of data clumping. Long parameter lists are hard to read, easy to misorder, and painful to extend.

**The Solution**: Create a small, typically immutable class that holds the related values. Pass one object instead of many primitives. This:

- Replaces a long parameter list with a single, meaningful argument
- Makes the method signature self-documenting through the object's class name
- Centralizes validation logic that was previously duplicated at every call site
- Provides a natural home for methods that operate on the grouped data

## Mechanics

1. **Define a new class** to represent the parameter group (typically readonly/immutable)
2. **Add the new parameter** to the method signature alongside the existing ones
3. **Migrate parameters one by one** into the object, updating callers as you go
4. **Run tests after each step** to catch breakage early
5. **Move related behavior** into the parameter object if it makes sense (validation, formatting, etc.)

## Before & After: PHP 8.3+ Code

### Before: Multiple Parameters

```php
class OrderService
{
    public function createOrder(
        string $customerName,
        string $customerEmail,
        string $customerPhone,
        string $address,
        string $city,
        string $zipCode
    ): Order {
        // Validation repeated across methods
        if (empty($customerName)) {
            throw new InvalidArgumentException('Name required');
        }

        // Create order...
        return new Order(
            $customerName,
            $customerEmail,
            $customerPhone,
            $address,
            $city,
            $zipCode
        );
    }

    public function validateCustomer(
        string $customerName,
        string $customerEmail,
        string $customerPhone
    ): bool {
        return !empty($customerName) && filter_var($customerEmail, FILTER_VALIDATE_EMAIL);
    }
}
```

### After: Parameter Object

```php
readonly class CustomerInfo
{
    public function __construct(
        public string $name,
        public string $email,
        public string $phone,
    ) {
        if (empty($name)) {
            throw new InvalidArgumentException('Name required');
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email');
        }
    }

    public function isValid(): bool
    {
        return !empty($this->name) && filter_var($this->email, FILTER_VALIDATE_EMAIL);
    }
}

readonly class Address
{
    public function __construct(
        public string $street,
        public string $city,
        public string $zipCode,
    ) {}
}

class OrderService
{
    public function createOrder(
        CustomerInfo $customer,
        Address $address
    ): Order {
        return new Order($customer, $address);
    }

    public function validateCustomer(CustomerInfo $customer): bool
    {
        return $customer->isValid();
    }
}
```

## Benefits

- **Readable Signatures**: A single named parameter communicates the group's purpose at a glance
- **Eliminated Duplication**: The same parameter cluster appears in one class definition, not in every method
- **Easier Extension**: Adding a field to the group requires changing only the class, not every caller
- **Centralized Validation**: Constraints are enforced once in the constructor, not scattered across call sites
- **Stronger Types**: An object provides richer type information than a list of primitives
- **Behavior Magnet**: The parameter object naturally attracts related methods (formatting, comparison, etc.)

## When NOT to Use

- Parameters that appear together by coincidence, not because they represent a coherent concept
- The grouped parameters would be used in only one or two places
- The additional class adds complexity without measurable benefit
- The API is simple, stable, and unlikely to change
- Existing domain models already encapsulate the data better

## Related Refactorings

- **Replace Parameter with Query**: Simplify signatures by computing values instead of passing them
- **Extract Class**: Split a parameter object that grows too large
- **Move Method**: Relocate validation and formatting logic into the parameter object
- **Remove Parameter**: Drop parameters that the parameter object makes unnecessary
- **Preserve Whole Object**: Pass an existing object rather than pulling fields out of it
