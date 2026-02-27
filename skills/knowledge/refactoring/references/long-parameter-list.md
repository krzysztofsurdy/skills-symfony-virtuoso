# Long Parameter List

## Overview

A method or function accepts more than three or four parameters, making call sites confusing and error-prone. This smell frequently surfaces when multiple algorithms are consolidated into one method, or when callers are forced to assemble data that the method could retrieve on its own. As parameters accumulate, the method becomes increasingly difficult to call correctly, test in isolation, and maintain over time.

## Why It's a Problem

- **Confusing Call Sites**: Callers must remember the correct order and meaning of each argument, especially when multiple parameters share the same type
- **Testing Friction**: Setting up test cases requires constructing numerous arguments, often with values irrelevant to the behavior under test
- **Ripple Effects**: Adding, removing, or reordering parameters forces changes at every call site
- **Implicit Relationships**: Constraints and dependencies between parameters remain hidden rather than being captured in a type
- **Tight Coupling**: Passing many primitive values binds the caller directly to the method's internal expectations

## Signs and Symptoms

- Methods accepting four or more parameters
- Multiple parameters of the same type that could be logically grouped
- Callers computing values solely to pass them as arguments
- Developers frequently checking the signature to recall parameter order
- The same parameter combinations appearing across several methods
- Parameters that are never used independently of each other

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
Bundle related parameters into a single value object. Group data that naturally belongs together, cutting down the parameter count while making the conceptual relationship explicit.

### 2. Replace Parameter with Method Call
When a parameter value is simply the result of calling a method on another object, have the receiving method retrieve it directly. This eliminates unnecessary arguments and reduces coupling between caller and callee.

### 3. Preserve Whole Object
Instead of extracting individual fields from an object and passing them separately, pass the entire object. This works well when the caller already holds a reference, though be mindful of introducing circular dependencies.

### 4. Use Enums for Options
Swap boolean flags and string-based choices for enums. This gives call sites type safety and makes the intent immediately clear.

### 5. Extract to Builder Pattern
For constructing complex objects with many optional parameters, a builder makes call sites readable and avoids telescoping constructors.

Note that refactoring long parameter lists often exposes previously hidden duplicate code, since the same parameter groupings tend to appear in multiple places.

## Exceptions

When NOT to refactor:
- **Framework Requirements**: Some frameworks enforce specific method signatures
- **Public APIs**: Changing signatures breaks consumer code; introduce overloads or new methods instead
- **Performance Sensitivity**: Object wrapping adds negligible overhead in most cases, but profile before deciding in hot paths
- **Intentional Flexibility**: Some methods genuinely require many parameters for algorithmic control
- **Legacy Constraints**: When the refactoring would cascade across too large a surface area to be practical

## Related Smells

- **Data Clumps**: Parameters that always travel together and should be grouped into objects
- **Primitive Obsession**: Raw types standing in for value objects
- **Feature Envy**: A method pulling many values from another object (suggests the method belongs there instead)
- **Message Chains**: Deep object traversal to extract values (related to the Preserve Whole Object solution)
