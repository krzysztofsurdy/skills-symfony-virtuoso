## Overview

Replace Temp with Query swaps temporary variables that hold intermediate computation results for method calls that perform those computations on demand. The calculation logic moves into its own method, and every place that previously read the variable now calls that method instead.

Rather than storing a computed value in a local variable, you define a method that produces the result and invoke it wherever the value is needed.

## Motivation

Temporary variables introduce several issues:

- **Trapped scope**: Variables are visible only within the declaring method, preventing reuse elsewhere
- **Cognitive weight**: Each additional temp adds one more thing a reader must track while understanding the method
- **Repeated logic**: The same calculation may be duplicated in other methods with no shared implementation
- **Untestable logic**: Calculations buried in local variables cannot be unit tested independently
- **Long methods**: Methods stuffed with temporaries are a common indicator that logic should be extracted

Replacing temps with query methods yields:

- **Clear separation of concerns**: Each method encapsulates a single computation
- **Independent testability**: Extracted methods can be verified in isolation
- **Reuse**: Other methods within the class can call the same query
- **Self-documenting code**: Method names describe what is being calculated

## Mechanics

1. **Find the temporary variable** that stores a calculated result
2. **Create a method** that returns the same calculated result
3. **Transfer the calculation** into the new method body
4. **Replace all reads** of the temporary variable with calls to the new method
5. **Delete the variable declaration**
6. **Set visibility** to private if the method is only needed within the class

## Before/After PHP 8.3+ Code Examples

### Before: Using Temporary Variables

```php
<?php

class Order
{
    private float $quantity;
    private float $itemPrice;
    private float $basePrice;

    public function __construct(float $quantity, float $itemPrice, float $basePrice)
    {
        $this->quantity = $quantity;
        $this->itemPrice = $itemPrice;
        $this->basePrice = $basePrice;
    }

    public function getPrice(): float
    {
        // Temporary variable for base price calculation
        $basePrice = $this->quantity * $this->itemPrice;

        // Temporary variable for discount
        $discountFactor = $this->getDiscountFactor($basePrice);

        // Use of temporary variables
        return $basePrice - ($basePrice * $discountFactor);
    }

    private function getDiscountFactor(float $price): float
    {
        if ($price > 1000) {
            return 0.15;
        } elseif ($price > 500) {
            return 0.10;
        }
        return 0.05;
    }
}

// Client code
$order = new Order(quantity: 100, itemPrice: 15.0, basePrice: 0);
$totalPrice = $order->getPrice();
```

### After: Using Query Methods

```php
<?php

class Order
{
    private float $quantity;
    private float $itemPrice;
    private float $basePrice;

    public function __construct(float $quantity, float $itemPrice, float $basePrice)
    {
        $this->quantity = $quantity;
        $this->itemPrice = $itemPrice;
        $this->basePrice = $basePrice;
    }

    public function getPrice(): float
    {
        // Direct method calls instead of temporary variables
        return $this->getBasePrice() - $this->getDiscount();
    }

    private function getBasePrice(): float
    {
        return $this->quantity * $this->itemPrice;
    }

    private function getDiscount(): float
    {
        return $this->getBasePrice() * $this->getDiscountFactor();
    }

    private function getDiscountFactor(): float
    {
        return match (true) {
            $this->getBasePrice() > 1000 => 0.15,
            $this->getBasePrice() > 500 => 0.10,
            default => 0.05,
        };
    }
}

// Client code
$order = new Order(quantity: 100, itemPrice: 15.0, basePrice: 0);
$totalPrice = $order->getPrice();
```

### Complex Example with Multiple Temporaries

**Before:**
```php
<?php

class Invoice
{
    private array $items = [];

    public function getTotalWithTax(): float
    {
        $subtotal = 0;

        foreach ($this->items as $item) {
            $subtotal += $item['price'] * $item['quantity'];
        }

        $taxRate = $this->calculateTaxRate();
        $tax = $subtotal * $taxRate;

        return $subtotal + $tax;
    }

    private function calculateTaxRate(): float
    {
        // Tax calculation logic
        return 0.19;
    }
}
```

**After:**
```php
<?php

class Invoice
{
    private array $items = [];

    public function getTotalWithTax(): float
    {
        return $this->getSubtotal() + $this->getTax();
    }

    private function getSubtotal(): float
    {
        return array_reduce(
            $this->items,
            fn ($carry, $item) => $carry + ($item['price'] * $item['quantity']),
            0
        );
    }

    private function getTax(): float
    {
        return $this->getSubtotal() * $this->getTaxRate();
    }

    private function getTaxRate(): float
    {
        return 0.19;
    }
}
```

## Benefits

- **Readable intent**: Method names act as inline documentation, making each computation's purpose clear
- **Centralized changes**: Adjusting calculation logic requires editing only one method
- **Isolated testing**: Extracted query methods can be unit tested on their own
- **Cross-method reuse**: Other methods in the class can invoke the same queries
- **Shorter methods**: Moving calculations out makes the host method more concise
- **Focused responsibility**: Each method handles exactly one concern
- **Unlocks further refactoring**: Opens doors for Extract Class or Move Method down the line

## When NOT to Use

- **Performance-sensitive code**: Repeated method calls may be measurably slower than a cached local variable (consider memoization as a compromise)
- **Trivial single-use expressions**: For very simple, one-off calculations, a temp may be more straightforward
- **Tight loops**: Method call overhead in hot loops can accumulate
- **Complex conditionals**: Sometimes a well-named temporary variable makes a multi-clause conditional easier to follow than nested method calls

In these scenarios, you might keep the temp but still extract the method for clarity, or add memoization to avoid redundant computation.

## Related Refactorings

- **Extract Method**: The complementary technique that creates the query method itself
- **Introduce Parameter Object**: When many temporaries exist, bundling them into a value object may be more appropriate
- **Introduce Variable**: Use a descriptive temp to simplify a complex expression before deciding whether to extract a method
- **Cache Query Result**: Memoize the result of expensive query methods to preserve performance
- **Remove Middle Man**: Avoid over-extracting queries that simply delegate to another method

## Examples in Other Languages

### Java

**Before:**
```java
double calculateTotal() {
  double basePrice = quantity * itemPrice;
  if (basePrice > 1000) {
    return basePrice * 0.95;
  }
  else {
    return basePrice * 0.98;
  }
}
```

**After:**
```java
double calculateTotal() {
  if (basePrice() > 1000) {
    return basePrice() * 0.95;
  }
  else {
    return basePrice() * 0.98;
  }
}
double basePrice() {
  return quantity * itemPrice;
}
```

### C#

**Before:**
```csharp
double CalculateTotal()
{
  double basePrice = quantity * itemPrice;

  if (basePrice > 1000)
  {
    return basePrice * 0.95;
  }
  else
  {
    return basePrice * 0.98;
  }
}
```

**After:**
```csharp
double CalculateTotal()
{
  if (BasePrice() > 1000)
  {
    return BasePrice() * 0.95;
  }
  else
  {
    return BasePrice() * 0.98;
  }
}
double BasePrice()
{
  return quantity * itemPrice;
}
```

### Python

**Before:**
```python
def calculateTotal():
    basePrice = quantity * itemPrice
    if basePrice > 1000:
        return basePrice * 0.95
    else:
        return basePrice * 0.98
```

**After:**
```python
def calculateTotal():
    if basePrice() > 1000:
        return basePrice() * 0.95
    else:
        return basePrice() * 0.98

def basePrice():
    return quantity * itemPrice
```

### TypeScript

**Before:**
```typescript
calculateTotal(): number {
  let basePrice = quantity * itemPrice;
  if (basePrice > 1000) {
    return basePrice * 0.95;
  }
  else {
    return basePrice * 0.98;
  }
}
```

**After:**
```typescript
calculateTotal(): number {
  if (basePrice() > 1000) {
    return basePrice() * 0.95;
  }
  else {
    return basePrice() * 0.98;
  }
}
basePrice(): number {
  return quantity * itemPrice;
}
```
