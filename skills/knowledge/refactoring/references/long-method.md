# Long Method Code Smell

## Overview

A Long Method is a code smell indicating that a method has accumulated far more logic than it should contain -- generally anything beyond ten lines deserves scrutiny. Methods tend to grow organically as developers add "just one more thing," and over time they become dense, tangled, and resistant to change. The longer a method gets, the harder it is to name accurately, test thoroughly, and reason about confidently.

## Why It's a Problem

- **Hard to Read**: Dense methods force readers to hold too much context in their head at once
- **Difficult to Reuse**: When logic is tangled together inside a single method, individual pieces cannot be extracted for use elsewhere
- **Painful to Test**: Each additional responsibility in a method multiplies the number of test scenarios required
- **Duplication Hides in Plain Sight**: Repeated patterns buried inside long methods are easy to miss, leading to inconsistent fixes
- **Optimization Blind Spots**: Real performance bottlenecks get lost among irrelevant code
- **Risky to Modify**: Touching one part of a long method risks breaking unrelated behavior in the same block

## Signs and Symptoms

- Methods stretching beyond 10-20 lines
- Deeply nested control structures (loops inside conditionals inside loops)
- Temporary local variables used only as intermediate holders
- A single method juggling multiple unrelated tasks
- The method name would need "and" or "or" to describe what it does accurately
- Large conditional branches managing different execution paths
- Complex logic embedded directly inside loop bodies

## Before/After Examples

### Before: Long, Monolithic Method

```php
declare(strict_types=1);

class OrderProcessor
{
    public function processOrder(array $orderData): array
    {
        $total = 0;
        $taxRate = 0.1;
        $discounts = [];

        foreach ($orderData['items'] as $item) {
            $price = $item['price'] * $item['quantity'];
            if ($item['quantity'] > 10) {
                $price *= 0.9;
                $discounts[] = $item['id'];
            }
            $total += $price;
        }

        $tax = $total * $taxRate;
        $total += $tax;

        if ($orderData['customer']['membership'] === 'gold') {
            $total *= 0.95;
        }

        if ($total > 1000) {
            $shippingCost = 0;
        } elseif ($total > 500) {
            $shippingCost = 5;
        } else {
            $shippingCost = 10;
        }

        $total += $shippingCost;

        return [
            'total' => $total,
            'tax' => $tax,
            'shipping' => $shippingCost,
            'discounts' => $discounts,
        ];
    }
}
```

### After: Refactored Methods

```php
declare(strict_types=1);

enum CustomerMembership: string
{
    case Standard = 'standard';
    case Gold = 'gold';
    case Platinum = 'platinum';
}

readonly class OrderItem
{
    public function __construct(
        public string $id,
        public float $price,
        public int $quantity,
    ) {}
}

readonly class OrderResult
{
    public function __construct(
        public float $total,
        public float $tax,
        public float $shipping,
        public array $appliedDiscounts = [],
    ) {}
}

class OrderProcessor
{
    private const BULK_DISCOUNT_THRESHOLD = 10;
    private const BULK_DISCOUNT_RATE = 0.9;
    private const TAX_RATE = 0.1;
    private const GOLD_MEMBER_DISCOUNT = 0.95;

    public function processOrder(array $orderData): OrderResult
    {
        $subtotal = $this->calculateSubtotal($orderData['items']);
        $tax = $this->calculateTax($subtotal);
        $memberDiscount = $this->applyMembershipDiscount($subtotal + $tax, $orderData['customer']);
        $shipping = $this->calculateShipping($memberDiscount);

        $discountedTotal = $this->applyMembershipDiscount($subtotal + $tax, $orderData['customer']);

        return new OrderResult(
            total: $discountedTotal + $shipping,
            tax: $tax,
            shipping: $shipping,
        );
    }

    private function calculateSubtotal(array $items): float
    {
        $subtotal = 0;
        foreach ($items as $item) {
            $subtotal += $this->calculateItemPrice($item);
        }
        return $subtotal;
    }

    private function calculateItemPrice(array $item): float
    {
        $price = $item['price'] * $item['quantity'];
        return $item['quantity'] >= self::BULK_DISCOUNT_THRESHOLD
            ? $price * self::BULK_DISCOUNT_RATE
            : $price;
    }

    private function calculateTax(float $subtotal): float
    {
        return $subtotal * self::TAX_RATE;
    }

    private function applyMembershipDiscount(float $amount, array $customer): float
    {
        $membership = CustomerMembership::from($customer['membership']);
        return $membership === CustomerMembership::Gold
            ? $amount * self::GOLD_MEMBER_DISCOUNT
            : $amount;
    }

    private function calculateShipping(float $subtotal): float
    {
        return match (true) {
            $subtotal > 1000 => 0,
            $subtotal > 500 => 5,
            default => 10,
        };
    }
}
```

## Recommended Refactorings

1. **Extract Method**: The go-to technique. Identify logical blocks within the method and pull them into their own well-named methods, each focused on a single task.

2. **Replace Temp with Query**: Eliminate temporary local variables by converting them into method calls that compute the value when needed. This removes obstacles to further extraction.

3. **Introduce Parameter Object**: When a method juggles many parameters or passes groups of values together, bundle them into a dedicated object. This also works well with **Preserve Whole Object** -- pass the source object rather than extracting individual fields.

4. **Replace Method with Method Object**: A last-resort technique for when local variable entanglement makes extraction impossible. Move the entire method into its own class where local variables become fields.

5. **Decompose Conditional**: Pull complex conditional logic into descriptive named methods, making the branching structure self-documenting.

6. **Use Enums and Readonly Classes**: Take advantage of PHP 8.1+ features to build self-describing, immutable data structures that reduce the need for inline logic.

Note that shorter methods have negligible performance overhead from additional calls -- modern runtimes optimize this well, and the readability gains far outweigh any micro-cost.

## Exceptions

- **Procedural Scripts**: Straightforward scripts performing sequential operations may legitimately run longer without being problematic.
- **Algorithmic Methods**: Complex mathematical or scientific computations sometimes need more lines; if they are well-organized with helper methods, this is acceptable.
- **Legacy Constraints**: External dependencies may prevent certain refactorings; focus effort where the payoff is greatest.

## Related Smells

- **Duplicate Code**: Often lurks inside long methods; breaking them apart exposes the repetition
- **Feature Envy**: Long methods frequently reach into other objects' data excessively
- **Primitive Obsession**: Overuse of raw types instead of objects; Introduce Parameter Object is a shared remedy
- **Data Clumps**: Groups of variables that travel together are strong candidates for Parameter Object extraction
