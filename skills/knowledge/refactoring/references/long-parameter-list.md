# Long Parameter List

## Overview

A method or function takes more than three or four parameters, turning call sites into puzzles and inviting mistakes. This smell commonly emerges when several algorithms are folded into a single method, or when callers must assemble data that the method could fetch on its own. As the parameter count climbs, the method becomes progressively harder to invoke correctly, test in isolation, and maintain over time.

## Why It's a Problem

- **Opaque Call Sites**: Callers must recall the correct sequence and meaning of each argument, particularly when multiple parameters share the same type
- **Test Setup Overhead**: Constructing test cases demands numerous arguments, many irrelevant to the behavior under test
- **Cascade of Changes**: Adding, removing, or reordering parameters forces updates at every call site
- **Hidden Constraints**: Dependencies and invariants among parameters stay invisible rather than being captured in a type
- **Tight Coupling**: Passing many primitive values ties the caller directly to the method's internal expectations

## Signs and Symptoms

- Methods that accept four or more parameters
- Multiple parameters of the same type that logically belong together
- Callers calculating values solely to pass them as arguments
- Developers routinely checking the signature to remember parameter order
- Identical parameter groupings recurring across several methods
- Parameters that are never used independently of one another

## Before/After

### Before: Long Parameter List

```php
<?php declare(strict_types=1);

class OrderProcessor
{
    public function processOrder(
        string $customerEmail,
        string $customerName,
        string $addressLine1,
        string $addressLine2,
        string $city,
        string $state,
        string $zipCode,
        string $country,
        float $subtotal,
        float $tax,
        float $shipping,
        array $items,
        bool $expressShipping,
        string $paymentMethod
    ): void {
        // Complex logic with many parameters
    }
}

// Calling code is unclear and error-prone
$processor = new OrderProcessor();
$processor->processOrder(
    'john@example.com',
    'John Doe',
    '123 Main St',
    'Apt 4',
    'Springfield',
    'IL',
    '62701',
    'USA',
    150.00,
    12.50,
    10.00,
    $items,
    true,
    'credit_card'
);
```

### After: Parameter Objects

```php
<?php declare(strict_types=1);

readonly class ShippingAddress
{
    public function __construct(
        public string $line1,
        public string $line2,
        public string $city,
        public string $state,
        public string $zipCode,
        public string $country,
    ) {}
}

readonly class OrderTotal
{
    public function __construct(
        public float $subtotal,
        public float $tax,
        public float $shipping,
    ) {}

    public function getGrandTotal(): float
    {
        return $this->subtotal + $this->tax + $this->shipping;
    }
}

enum ShippingMethod
{
    case Standard;
    case Express;
}

enum PaymentMethod
{
    case CreditCard;
    case PayPal;
    case BankTransfer;
}

readonly class OrderRequest
{
    public function __construct(
        public string $customerEmail,
        public string $customerName,
        public ShippingAddress $address,
        public OrderTotal $total,
        public array $items,
        public ShippingMethod $shippingMethod,
        public PaymentMethod $paymentMethod,
    ) {}
}

class OrderProcessor
{
    public function processOrder(OrderRequest $request): void
    {
        // Clear, maintainable code with explicit structure
        $this->validateOrder($request);
        $this->calculateTax($request);
        $this->processPayment($request);
    }
}

// Calling code is clear and type-safe
$address = new ShippingAddress(
    line1: '123 Main St',
    line2: 'Apt 4',
    city: 'Springfield',
    state: 'IL',
    zipCode: '62701',
    country: 'USA',
);

$total = new OrderTotal(
    subtotal: 150.00,
    tax: 12.50,
    shipping: 10.00,
);

$request = new OrderRequest(
    customerEmail: 'john@example.com',
    customerName: 'John Doe',
    address: $address,
    total: $total,
    items: $items,
    shippingMethod: ShippingMethod::Express,
    paymentMethod: PaymentMethod::CreditCard,
);

$processor = new OrderProcessor();
$processor->processOrder($request);
```

## Recommended Refactorings

### 1. Introduce Parameter Object
Consolidate related parameters into a single value object. Group data that naturally belongs together, reducing the parameter count while making the conceptual relationship explicit.

### 2. Replace Parameter with Method Call
When a parameter value is just the result of calling a method on another object, let the receiving method fetch it directly. This trims unnecessary arguments and loosens the coupling between caller and callee.

### 3. Preserve Whole Object
Rather than extracting individual fields from an object and passing them one by one, pass the entire object. This works well when the caller already holds a reference, though watch out for circular dependencies.

### 4. Use Enums for Options
Replace boolean flags and string-based choices with enums. This provides type safety and makes the intent immediately apparent at call sites.

### 5. Extract to Builder Pattern
For assembling complex objects with many optional parameters, a builder keeps call sites readable and avoids telescoping constructors.

Note that refactoring long parameter lists frequently uncovers previously hidden duplicate code, since the same parameter groupings tend to appear in multiple locations.

## Exceptions

When NOT to refactor:
- **Framework Requirements**: Some frameworks mandate specific method signatures
- **Public APIs**: Changing signatures breaks consumer code; add overloads or new methods instead
- **Performance Sensitivity**: Object wrapping introduces negligible overhead in most cases, but profile before deciding in hot paths
- **Deliberate Flexibility**: Some methods genuinely need many parameters for algorithmic control
- **Legacy Constraints**: When the refactoring would cascade across too large a surface area to be practical

## Related Smells

- **Data Clumps**: Parameters that invariably travel together and should be grouped into objects
- **Primitive Obsession**: Raw types standing in for value objects
- **Feature Envy**: A method extracting many values from another object (suggests the method belongs there instead)
- **Message Chains**: Deep object traversal to extract values (related to the Preserve Whole Object solution)
