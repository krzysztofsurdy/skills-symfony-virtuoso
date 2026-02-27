## Overview

Parameterize Method merges several methods that do nearly the same thing into one method governed by a parameter. When multiple methods share the same structure but differ only in a literal value or a small constant, introducing a parameter to capture that difference removes the duplication and yields a single, flexible entry point.

## Motivation

Codebases accumulate look-alike methods that vary in only a constant or threshold. This repetition leads to:

- **Multiplied maintenance**: Every fix or enhancement must be applied across all variants
- **Divergence risk**: Over time the copies drift apart, introducing subtle inconsistencies
- **Difficult extension**: Each new variant demands yet another near-duplicate method

Replacing the set of methods with one parameterized version gives you a single source of truth, a smaller API surface, and a straightforward path to supporting additional variants.

## Mechanics

The refactoring process involves three main steps:

1. **Identify common code**: Analyze similar methods to find their common logic
2. **Extract to new method**: Create a new method with a parameter representing the differing values
3. **Update call sites**: Replace calls to the old methods with calls to the new parameterized method, then delete the old methods

## Before/After Example (PHP 8.3+)

### Before

```php
class DataProcessor
{
    public function getSalesPrice(Product $product): float
    {
        return $product->getBasePrice() * 0.9;
    }

    public function getPurchasePrice(Product $product): float
    {
        return $product->getBasePrice() * 1.1;
    }

    public function getTransferPrice(Product $product): float
    {
        return $product->getBasePrice() * 1.05;
    }
}

// Usage
$processor = new DataProcessor();
$salePrice = $processor->getSalesPrice($product);
$purchasePrice = $processor->getPurchasePrice($product);
$transferPrice = $processor->getTransferPrice($product);
```

### After

```php
class DataProcessor
{
    private const MULTIPLIERS = [
        'sale' => 0.9,
        'purchase' => 1.1,
        'transfer' => 1.05,
    ];

    public function getPrice(Product $product, string $type): float
    {
        $multiplier = self::MULTIPLIERS[$type]
            ?? throw new InvalidArgumentException("Unknown price type: $type");

        return $product->getBasePrice() * $multiplier;
    }
}

// Usage
$processor = new DataProcessor();
$salePrice = $processor->getPrice($product, 'sale');
$purchasePrice = $processor->getPrice($product, 'purchase');
$transferPrice = $processor->getPrice($product, 'transfer');
```

## Benefits

- **Single source of truth**: Identical logic lives in one place, eliminating drift between copies
- **Lower maintenance cost**: Bug fixes and enhancements apply once
- **Easy extension**: Adding a new variant is a configuration change, not a new method
- **Cleaner API**: Callers see one well-named method rather than a family of near-duplicates
- **Simpler testing**: One method with parameterized test cases replaces many individual test methods

## When NOT to Use

- **Excessive complexity**: If the conditional logic becomes convoluted, the refactoring is counterproductive
- **Fundamentally different operations**: Methods with similar patterns but truly distinct purposes should remain separate
- **Performance-critical code**: Parameter checking might introduce unnecessary overhead in hot paths
- **Unclear intent**: When parameterization obscures what the method does rather than clarifying it

Sometimes this refactoring can be taken too far, resulting in long, complicated methods instead of multiple simpler ones. If conditional logic becomes too complex, consider the inverse refactoring: Replace Parameter with Explicit Methods.

## Related Refactorings

- **Extract Method**: Identify common code patterns before parameterizing
- **Replace Parameter with Explicit Methods**: Reverse operation when conditional logic becomes too complex
- **Remove Parameter**: Simplify methods by eliminating unused parameters
- **Introduce Parameter Object**: When multiple related parameters accumulate, group them into an object
