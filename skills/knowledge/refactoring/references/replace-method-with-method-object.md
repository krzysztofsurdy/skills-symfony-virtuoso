## Overview

Replace Method with Method Object extracts a complex method into its own dedicated class. The method's logic becomes the central operation of this new object, its parameters become constructor arguments, and its local variables become instance fields. This technique is especially helpful when a method has grown unwieldy due to many parameters, tangled logic, or heavily interdependent local variables.

## Motivation

### Problem
- **Unwieldy methods**: Methods packed with parameters and local variables become hard to follow
- **Low reusability**: Logic locked inside a single class cannot be extracted or tested on its own
- **Difficult decomposition**: Splitting the method into smaller pieces within the same class feels awkward
- **Testing friction**: Exercising specific branches of intricate logic means instantiating the entire host class
- **Bloated signatures**: Methods with long parameter lists are cumbersome to call and maintain

### Solution
Introduce a new class where:
- The method becomes a public operation (typically `__invoke()` or `execute()`)
- Parameters are received through the constructor
- Local variables are promoted to instance properties
- The original logic migrates into the class

## Mechanics

1. Create a new class with a descriptive name (e.g., `CalculateOrderTotal`, `GenerateReport`)
2. Accept all method parameters through the constructor
3. Promote local variables to instance properties
4. Move the method body into a `__invoke()` or `execute()` method
5. Replace the original method with an instantiation and invocation of the new class
6. Run the full test suite to confirm identical behavior
7. Decompose the new class into private helper methods as appropriate

## Before/After Examples

### Before: Complex Method with Multiple Parameters

```php
class OrderProcessor
{
    public function calculateTotal(
        Order $order,
        Customer $customer,
        string $couponCode = null
    ): float {
        $subtotal = 0;

        foreach ($order->getItems() as $item) {
            $subtotal += $item->getPrice() * $item->getQuantity();
        }

        $taxRate = $customer->getLocation() === 'US' ? 0.08 : 0;
        $tax = $subtotal * $taxRate;

        $discount = 0;
        if ($couponCode) {
            $coupon = new CouponService()->findByCode($couponCode);
            if ($coupon && $coupon->isValid()) {
                $discount = $coupon->getPercentage() * $subtotal / 100;
            }
        }

        $shipping = $subtotal > 100 ? 0 : 15;

        return $subtotal + $tax - $discount + $shipping;
    }
}
```

### After: Method Object Pattern

```php
// New dedicated class
class CalculateOrderTotal
{
    private float $subtotal = 0;
    private float $tax = 0;
    private float $discount = 0;
    private float $shipping = 0;

    public function __construct(
        private Order $order,
        private Customer $customer,
        private ?string $couponCode = null
    ) {}

    public function __invoke(): float
    {
        $this->calculateSubtotal();
        $this->calculateTax();
        $this->applyDiscount();
        $this->calculateShipping();

        return $this->subtotal + $this->tax - $this->discount + $this->shipping;
    }

    private function calculateSubtotal(): void
    {
        foreach ($this->order->getItems() as $item) {
            $this->subtotal += $item->getPrice() * $item->getQuantity();
        }
    }

    private function calculateTax(): void
    {
        $taxRate = $this->customer->getLocation() === 'US' ? 0.08 : 0;
        $this->tax = $this->subtotal * $taxRate;
    }

    private function applyDiscount(): void
    {
        if (!$this->couponCode) {
            return;
        }

        $coupon = (new CouponService())->findByCode($this->couponCode);
        if ($coupon?->isValid()) {
            $this->discount = $coupon->getPercentage() * $this->subtotal / 100;
        }
    }

    private function calculateShipping(): void
    {
        $this->shipping = $this->subtotal > 100 ? 0 : 15;
    }
}

// Usage in OrderProcessor
class OrderProcessor
{
    public function calculateTotal(
        Order $order,
        Customer $customer,
        string $couponCode = null
    ): float {
        return (new CalculateOrderTotal($order, $customer, $couponCode))();
    }
}
```

## Benefits

- **Readable structure**: Complex logic splits into named private methods that describe each step's purpose
- **Independent testability**: The method object can be instantiated and tested without the original host class
- **Clean decomposition**: Intricate logic breaks down into manageable pieces within a cohesive class
- **Portability**: The method object can be used from different contexts and callers
- **Single Responsibility**: Each class exists for exactly one reason
- **Easier inspection**: State lives in instance fields, making it straightforward to inspect during debugging
- **Callable syntax**: Using `__invoke()` makes the object callable, yielding elegant PHP 8.3+ usage

## When NOT to Use

- **Straightforward methods**: If the method is short and easy to understand, creating a whole class is overkill
- **Hot paths**: Object construction has negligible cost, but if called billions of times, weigh the trade-off
- **Truly one-off logic**: For genuinely unrepeated logic, the overhead of a dedicated class may not pay for itself
- **Simple parameter forwarding**: If the method just passes arguments without complex logic, extract a smaller helper instead
- **Conflicting architecture**: Do not introduce this pattern if the codebase follows a different architectural convention

## Related Refactorings

- **Extract Method**: Often the first refactoring to try when complex logic appears inside a method
- **Extract Class**: A broader variant that pulls out entire responsibilities rather than a single operation
- **Decompose Conditional**: Helpful for simplifying branching logic before promoting it to a method object
- **Introduce Parameter Object**: Pairs well with this technique to bundle related constructor arguments
- **Strategy Pattern**: Method objects frequently evolve into Strategy implementations with interchangeable variants

## Examples in Other Languages

### Java

**Before:**
```java
class Order {
  // ...
  public double price() {
    double primaryBasePrice;
    double secondaryBasePrice;
    double tertiaryBasePrice;
    // Perform long computation.
  }
}
```

**After:**
```java
class Order {
  // ...
  public double price() {
    return new PriceCalculator(this).compute();
  }
}

class PriceCalculator {
  private double primaryBasePrice;
  private double secondaryBasePrice;
  private double tertiaryBasePrice;

  public PriceCalculator(Order order) {
    // Copy relevant information from the
    // order object.
  }

  public double compute() {
    // Perform long computation.
  }
}
```

### C#

**Before:**
```csharp
public class Order
{
  // ...
  public double Price()
  {
    double primaryBasePrice;
    double secondaryBasePrice;
    double tertiaryBasePrice;
    // Perform long computation.
  }
}
```

**After:**
```csharp
public class Order
{
  // ...
  public double Price()
  {
    return new PriceCalculator(this).Compute();
  }
}

public class PriceCalculator
{
  private double primaryBasePrice;
  private double secondaryBasePrice;
  private double tertiaryBasePrice;

  public PriceCalculator(Order order)
  {
    // Copy relevant information from the
    // order object.
  }

  public double Compute()
  {
    // Perform long computation.
  }
}
```

### Python

**Before:**
```python
class Order:
    # ...
    def price(self):
        primaryBasePrice = 0
        secondaryBasePrice = 0
        tertiaryBasePrice = 0
        # Perform long computation.
```

**After:**
```python
class Order:
    # ...
    def price(self):
        return PriceCalculator(self).compute()


class PriceCalculator:
    def __init__(self, order):
        self._primaryBasePrice = 0
        self._secondaryBasePrice = 0
        self._tertiaryBasePrice = 0
        # Copy relevant information from the
        # order object.

    def compute(self):
        # Perform long computation.
```

### TypeScript

**Before:**
```typescript
class Order {
  // ...
  price(): number {
    let primaryBasePrice;
    let secondaryBasePrice;
    let tertiaryBasePrice;
    // Perform long computation.
  }
}
```

**After:**
```typescript
class Order {
  // ...
  price(): number {
    return new PriceCalculator(this).compute();
  }
}

class PriceCalculator {
  private _primaryBasePrice: number;
  private _secondaryBasePrice: number;
  private _tertiaryBasePrice: number;

  constructor(order: Order) {
    // Copy relevant information from the
    // order object.
  }

  compute(): number {
    // Perform long computation.
  }
}
```
