## Overview

Preserve Whole Object passes an entire object as a method argument instead of pulling individual values out of it first. When a caller extracts several fields from an object only to hand them to another method, passing the object itself simplifies the call site and keeps the extraction logic in one place.

Instead of:
```php
$low = $daysTempRange->getLow();
$high = $daysTempRange->getHigh();
$withinPlan = $plan->withinRange($low, $high);
```

We pass the whole object:
```php
$withinPlan = $plan->withinRange($daysTempRange);
```

## Motivation

Extracting multiple values from an object at every call site is repetitive and fragile. If the receiving method later needs an additional piece of data, every caller must be updated to extract and pass the new value. By handing over the whole object, the receiving method can reach for whatever it needs internally, and callers remain untouched when requirements evolve.

Key motivations include:
- **Reduce boilerplate**: Eliminate repetitive extraction of values before method calls
- **Improve maintainability**: Changes to what data a method needs only require updates in one place
- **Simplify call sites**: Method calls become cleaner and more readable

## Mechanics

1. **Identify the pattern**: Find methods receiving multiple values extracted from the same object
2. **Add new parameter**: Create a new method parameter accepting the whole object
3. **Update method body**: Replace value parameters with appropriate method calls on the object
4. **Update call sites**: Replace extracted value arguments with the whole object
5. **Remove old parameters**: Delete the now-unused individual value parameters
6. **Test**: Ensure all call sites work correctly with the change

## Before/After PHP 8.3+ Code

### Before
```php
class Account
{
    public function withinCreditLimit(int $minBalance, int $maxBalance): bool
    {
        return $this->balance >= $minBalance && $this->balance <= $maxBalance;
    }
}

class Client
{
    public function checkCredit(): void
    {
        $account = new Account();
        $limit = new CreditLimit(1000, 5000);

        // Extracting values before passing them
        $min = $limit->getMinimum();
        $max = $limit->getMaximum();

        if ($account->withinCreditLimit($min, $max)) {
            echo "Credit OK\n";
        }
    }
}
```

### After
```php
class CreditLimit
{
    public function __construct(
        private readonly int $minimum,
        private readonly int $maximum,
    ) {}

    public function getMinimum(): int
    {
        return $this->minimum;
    }

    public function getMaximum(): int
    {
        return $this->maximum;
    }
}

class Account
{
    public function __construct(
        private readonly int $balance = 2500,
    ) {}

    // Pass the whole object instead of individual values
    public function withinCreditLimit(CreditLimit $limit): bool
    {
        return $this->balance >= $limit->getMinimum()
            && $this->balance <= $limit->getMaximum();
    }
}

class Client
{
    public function checkCredit(): void
    {
        $account = new Account();
        $limit = new CreditLimit(1000, 5000);

        // Cleaner call site - pass whole object
        if ($account->withinCreditLimit($limit)) {
            echo "Credit OK\n";
        }
    }
}
```

## Benefits

- **Shorter Parameter Lists**: Method signatures become concise and self-explanatory
- **Resilient to Change**: The receiving method can access additional data without altering callers
- **Less Duplication**: Extraction logic lives inside the method, not at every call site
- **Stronger Abstractions**: Parameters express domain concepts rather than raw primitives
- **Simpler Call Sites**: Callers pass one object instead of juggling several extracted values

## When NOT to Use

- **Domain Boundary Crossing**: When passing data across architectural boundaries (e.g., API responses), passing the whole object may expose internal structure
- **Multiple Source Objects**: If values come from different objects, combining them into one artificial object may violate single responsibility
- **Primitive-Only Methods**: Methods expecting only simple types may become overly coupled to specific object structures
- **Primitive Obsession Anti-pattern**: Don't create wrapper objects just to avoid primitive parameters
- **Data Transfer Objects**: For DTOs or value objects passed across services, individual properties may be more appropriate

## Related Refactorings

- **Introduce Parameter Object**: Creates a new object to group related parameters, often used before Preserve Whole Object
- **Extract Class**: Helps identify cohesive data that should be passed together
- **Encapsulate Query**: Focuses on hiding data access logic within objects
- **Replace Parameter with Query**: Removes parameters by querying for values internally

## Examples in Other Languages

### Java

**Before:**
```java
int low = daysTempRange.getLow();
int high = daysTempRange.getHigh();
boolean withinPlan = plan.withinRange(low, high);
```

**After:**
```java
boolean withinPlan = plan.withinRange(daysTempRange);
```

### C#

**Before:**
```csharp
int low = daysTempRange.GetLow();
int high = daysTempRange.GetHigh();
bool withinPlan = plan.WithinRange(low, high);
```

**After:**
```csharp
bool withinPlan = plan.WithinRange(daysTempRange);
```

### Python

**Before:**
```python
low = daysTempRange.getLow()
high = daysTempRange.getHigh()
withinPlan = plan.withinRange(low, high)
```

**After:**
```python
withinPlan = plan.withinRange(daysTempRange)
```

### TypeScript

**Before:**
```typescript
let low = daysTempRange.getLow();
let high = daysTempRange.getHigh();
let withinPlan = plan.withinRange(low, high);
```

**After:**
```typescript
let withinPlan = plan.withinRange(daysTempRange);
```
