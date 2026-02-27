## Overview

The "Replace Nested Conditional with Guard Clauses" refactoring flattens deeply nested if-else trees into a linear sequence of guard clauses. A guard clause is an early return or throw that handles a special case before the main logic runs. This approach eliminates the "pyramid of doom" where each additional nesting level pushes code further to the right, making it progressively harder to read.

## Motivation

Deeply nested conditionals introduce several concrete problems:

- **Obscured intent**: The core logic gets buried under layers of indentation, forcing readers to mentally track multiple branches at once
- **Appearance of ad-hoc development**: Heavy nesting often signals that conditions were added reactively rather than designed deliberately
- **Mental burden**: Every nesting level demands that the reader maintain additional context, reducing comprehension speed
- **Harder testing**: Deeply branching code paths multiply the number of scenarios that need coverage
- **Greater defect risk**: Intricate conditional structures are fertile ground for off-by-one errors and overlooked edge cases

Guard clauses solve these issues by handling all boundary conditions at the top of the method, leaving the primary ("happy") path to flow unindented and uninterrupted.

## Mechanics

The refactoring proceeds through these steps:

1. **Spot guard conditions**: Identify branches that result in early returns, throws, or other exits
2. **Hoist to the top**: Move these guard clauses to the beginning of the method
3. **Flatten the structure**: Convert nested if-else trees into a sequence of independent if-statements
4. **Drop the else blocks**: Let guard clause returns eliminate the need for else branches
5. **Merge where possible**: Combine related guard conditions using logical operators when it improves clarity

## Before/After: PHP 8.3+ Code

### Before (Nested Conditionals)

```php
public function calculateSalary(Employee $employee): float
{
    if ($employee->isActive()) {
        if ($employee->getYearsOfService() > 5) {
            if ($employee->getDepartment() === 'Executive') {
                return $employee->getBaseSalary() * 1.2;
            } else {
                return $employee->getBaseSalary() * 1.1;
            }
        } else {
            return $employee->getBaseSalary();
        }
    } else {
        return 0;
    }
}
```

### After (Guard Clauses)

```php
public function calculateSalary(Employee $employee): float
{
    if (!$employee->isActive()) {
        return 0;
    }

    if ($employee->getYearsOfService() <= 5) {
        return $employee->getBaseSalary();
    }

    if ($employee->getDepartment() === 'Executive') {
        return $employee->getBaseSalary() * 1.2;
    }

    return $employee->getBaseSalary() * 1.1;
}
```

### Complex Example with Early Exits

```php
// Before
public function processOrder(Order $order, Customer $customer): void
{
    if ($order->isValid()) {
        if ($customer->hasValidPayment()) {
            if ($this->inventoryService->hasStock($order->getItems())) {
                $this->executePayment($order, $customer);
                $this->updateInventory($order->getItems());
                $this->sendConfirmation($customer);
            } else {
                throw new OutOfStockException();
            }
        } else {
            throw new PaymentException();
        }
    } else {
        throw new InvalidOrderException();
    }
}

// After
public function processOrder(Order $order, Customer $customer): void
{
    if (!$order->isValid()) {
        throw new InvalidOrderException();
    }

    if (!$customer->hasValidPayment()) {
        throw new PaymentException();
    }

    if (!$this->inventoryService->hasStock($order->getItems())) {
        throw new OutOfStockException();
    }

    $this->executePayment($order, $customer);
    $this->updateInventory($order->getItems());
    $this->sendConfirmation($customer);
}
```

## Benefits

- **Linear readability**: Code progresses top-to-bottom with minimal indentation
- **Visible preconditions**: Guard clauses make boundary handling explicit right at the start
- **Isolated test paths**: Each guard and the main path can be tested independently
- **Lower maintenance cost**: Future developers can grasp the method's logic quickly
- **Less mental overhead**: No need to mentally track which else branch corresponds to which if
- **Fewer temporary variables**: Eliminates intermediary result variables used only for conditional routing

## When NOT to Use

This refactoring may not fit when:

- **Tightly coupled conditions**: If conditions depend on each other's results, polymorphism may be more appropriate
- **Rich domain logic**: For substantial business rules, consider **Replace Conditional with Polymorphism** instead
- **Binary success/failure**: When there is exactly one success path and one failure path, a simple if-else is already clear
- **Performance-sensitive loops**: Early exits via exceptions carry overhead; use sparingly in tight iterations

## Related Refactorings

- **Decompose Conditional**: Extract complex boolean expressions into named methods to improve clarity
- **Replace Conditional with Polymorphism**: Use inheritance or interfaces when decision trees represent type-based behavior
- **Extract Method**: Move guard clause logic into dedicated helper methods for improved readability
- **Consolidate Duplicate Conditional Fragments**: Merge guard clauses that lead to the same outcome

## Examples in Other Languages

### Java

**Before:**
```java
public double getPayAmount() {
  double result;
  if (isDead){
    result = deadAmount();
  }
  else {
    if (isSeparated){
      result = separatedAmount();
    }
    else {
      if (isRetired){
        result = retiredAmount();
      }
      else{
        result = normalPayAmount();
      }
    }
  }
  return result;
}
```

**After:**
```java
public double getPayAmount() {
  if (isDead){
    return deadAmount();
  }
  if (isSeparated){
    return separatedAmount();
  }
  if (isRetired){
    return retiredAmount();
  }
  return normalPayAmount();
}
```

### C#

**Before:**
```csharp
public double GetPayAmount()
{
  double result;

  if (isDead)
  {
    result = DeadAmount();
  }
  else
  {
    if (isSeparated)
    {
      result = SeparatedAmount();
    }
    else
    {
      if (isRetired)
      {
        result = RetiredAmount();
      }
      else
      {
        result = NormalPayAmount();
      }
    }
  }

  return result;
}
```

**After:**
```csharp
public double GetPayAmount()
{
  if (isDead)
  {
    return DeadAmount();
  }
  if (isSeparated)
  {
    return SeparatedAmount();
  }
  if (isRetired)
  {
    return RetiredAmount();
  }
  return NormalPayAmount();
}
```

### Python

**Before:**
```python
def getPayAmount(self):
    if self.isDead:
        result = deadAmount()
    else:
        if self.isSeparated:
            result = separatedAmount()
        else:
            if self.isRetired:
                result = retiredAmount()
            else:
                result = normalPayAmount()
    return result
```

**After:**
```python
def getPayAmount(self):
    if self.isDead:
        return deadAmount()
    if self.isSeparated:
        return separatedAmount()
    if self.isRetired:
        return retiredAmount()
    return normalPayAmount()
```

### TypeScript

**Before:**
```typescript
getPayAmount(): number {
  let result: number;
  if (isDead){
    result = deadAmount();
  }
  else {
    if (isSeparated){
      result = separatedAmount();
    }
    else {
      if (isRetired){
        result = retiredAmount();
      }
      else{
        result = normalPayAmount();
      }
    }
  }
  return result;
}
```

**After:**
```typescript
getPayAmount(): number {
  if (isDead){
    return deadAmount();
  }
  if (isSeparated){
    return separatedAmount();
  }
  if (isRetired){
    return retiredAmount();
  }
  return normalPayAmount();
}
```
