## Overview

Replace Parameter with Method Call trims method signatures by removing parameters whose values can be obtained internally. Instead of requiring the caller to compute and pass a value, the method fetches it on its own through a query call.

## Motivation

Lengthy parameter lists make methods harder to read and call correctly. This refactoring tackles that complexity by:

- Removing parameters that were added speculatively for hypothetical future use
- Cutting down the mental effort of tracking intermediate values across multiple call sites
- Producing shorter, more expressive method signatures
- Lowering the coupling between the calling code and the method's internals

## Mechanics

1. **Check independence**: Confirm that the value-retrieval logic does not depend on parameters of the method being refactored
2. **Extract if complex**: If the retrieval logic is non-trivial, move it into its own dedicated method first
3. **Substitute references**: Replace every use of the parameter inside the method with a call to the retrieval method
4. **Drop the parameter**: Remove the now-unused parameter from the method signature
5. **Fix call sites**: Delete the corresponding argument from every caller

## Before/After (PHP 8.3+)

**Before:**
```php
class Order
{
    private int $quantity;
    private float $basePrice;

    public function getPrice(float $discountPercentage): float
    {
        return $this->calculateFinalPrice($discountPercentage);
    }

    private function calculateFinalPrice(float $discount): float
    {
        $baseTotal = $this->quantity * $this->basePrice;
        return $baseTotal * (1 - $discount / 100);
    }
}

// Usage
$order = new Order();
$discount = $order->getDiscount();
$price = $order->getPrice($discount);
```

**After:**
```php
class Order
{
    private int $quantity;
    private float $basePrice;

    public function getPrice(): float
    {
        return $this->calculateFinalPrice();
    }

    private function calculateFinalPrice(): float
    {
        $baseTotal = $this->quantity * $this->basePrice;
        return $baseTotal * (1 - $this->getDiscount() / 100);
    }

    private function getDiscount(): float
    {
        // Query the discount value directly
        return 10.0;
    }
}

// Usage
$order = new Order();
$price = $order->getPrice();
```

## Benefits

- **Leaner signatures**: Fewer parameters mean methods are easier to understand and invoke
- **Lower coupling**: The method no longer relies on the caller to supply internally obtainable data
- **Stronger encapsulation**: The object retrieves its own information rather than depending on external computation
- **Cleaner call sites**: Calling code becomes more concise and focused
- **Localized changes**: Modifications to how a value is computed affect only the object that owns it

## When NOT to Use

- **Caller-dependent values**: If the value varies based on caller context and cannot be derived internally, the parameter is necessary
- **Multiple contexts need different inputs**: When the same method must produce different results depending on what the caller provides
- **Hot code paths**: Repeated internal queries may be slower than passing a precomputed value
- **Cross-object data**: When the value belongs to a different object's domain and should not be fetched here
- **Intentional flexibility**: If you expect to inject alternative values for testing or future variations

## Related Refactorings

- **Extract Method**: Apply when the retrieval logic is complex enough to warrant its own method
- **Add Parameter**: The inverse refactoring, used when you need to widen a method's flexibility
- **Simplify Method Calls**: The broader family of refactorings aimed at reducing parameter list complexity
- **Remove Parameter**: A closely related technique for eliminating parameters that are no longer referenced

## Examples in Other Languages

### Java

**Before:**
```java
int basePrice = quantity * itemPrice;
double seasonDiscount = this.getSeasonalDiscount();
double fees = this.getFees();
double finalPrice = discountedPrice(basePrice, seasonDiscount, fees);
```

**After:**
```java
int basePrice = quantity * itemPrice;
double finalPrice = discountedPrice(basePrice);
```

### C#

**Before:**
```csharp
int basePrice = quantity * itemPrice;
double seasonDiscount = this.GetSeasonalDiscount();
double fees = this.GetFees();
double finalPrice = DiscountedPrice(basePrice, seasonDiscount, fees);
```

**After:**
```csharp
int basePrice = quantity * itemPrice;
double finalPrice = DiscountedPrice(basePrice);
```

### Python

**Before:**
```python
basePrice = quantity * itemPrice
seasonalDiscount = self.getSeasonalDiscount()
fees = self.getFees()
finalPrice = discountedPrice(basePrice, seasonalDiscount, fees)
```

**After:**
```python
basePrice = quantity * itemPrice
finalPrice = discountedPrice(basePrice)
```

### TypeScript

**Before:**
```typescript
let basePrice = quantity * itemPrice;
const seasonDiscount = this.getSeasonalDiscount();
const fees = this.getFees();
const finalPrice = discountedPrice(basePrice, seasonDiscount, fees);
```

**After:**
```typescript
let basePrice = quantity * itemPrice;
let finalPrice = discountedPrice(basePrice);
```
