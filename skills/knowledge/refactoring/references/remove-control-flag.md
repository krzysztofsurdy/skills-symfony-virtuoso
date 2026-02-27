# Remove Control Flag

## Overview

Remove Control Flag replaces boolean variables used to manage loop flow or early exits with direct control-flow statements such as `break`, `continue`, and `return`. These flag variables add indirection without adding clarity; the language already provides constructs purpose-built for controlling execution paths.

Control flags are a holdover from an era that valued single entry and single exit in every routine. Contemporary practice favors explicit flow control, which communicates intent more directly and keeps the code compact.

## Motivation

Control flags introduce several problems:

- **Obscured Intent**: The purpose of the boolean variable may not be immediately clear
- **Increased Complexity**: Extra variables and conditional checks clutter the code
- **Harder Maintenance**: Developers must track flag state across multiple code paths
- **Non-idiomatic Code**: Doesn't leverage language features designed for this purpose

Using `break`, `continue`, and `return` directly expresses programmer intent and eliminates boilerplate logic.

## Mechanics

The refactoring process involves three main steps:

1. **Identify** control flags: Find boolean variables used to exit loops or functions
2. **Replace** assignments: Replace flag assignments with appropriate flow control statements
3. **Remove**: Delete the flag variable and related conditional checks

## Before and After

### Example 1: Loop with Early Exit

**Before (with control flag):**

```php
<?php declare(strict_types=1);

function findUserByEmail(array $users, string $email): ?User
{
    $found = false;
    $user = null;

    foreach ($users as $currentUser) {
        if (!$found) {
            if ($currentUser->getEmail() === $email) {
                $user = $currentUser;
                $found = true;
            }
        }
    }

    return $user;
}
```

**After (with return statement):**

```php
<?php declare(strict_types=1);

function findUserByEmail(array $users, string $email): ?User
{
    foreach ($users as $user) {
        if ($user->getEmail() === $email) {
            return $user;
        }
    }

    return null;
}
```

### Example 2: Skipping Iterations

**Before (with control flag):**

```php
<?php declare(strict_types=1);

function processValidOrders(array $orders): array
{
    $results = [];

    foreach ($orders as $order) {
        $shouldProcess = true;

        if ($order->isCancelled()) {
            $shouldProcess = false;
        }

        if ($shouldProcess && $order->getTotal() <= 0) {
            $shouldProcess = false;
        }

        if ($shouldProcess) {
            $results[] = $this->processOrder($order);
        }
    }

    return $results;
}
```

**After (with continue statement):**

```php
<?php declare(strict_types=1);

function processValidOrders(array $orders): array
{
    $results = [];

    foreach ($orders as $order) {
        if ($order->isCancelled() || $order->getTotal() <= 0) {
            continue;
        }

        $results[] = $this->processOrder($order);
    }

    return $results;
}
```

### Example 3: Complex Validation

**Before (with control flag):**

```php
<?php declare(strict_types=1);

function validatePayment(Payment $payment): bool
{
    $isValid = true;

    if ($payment->getAmount() <= 0) {
        $isValid = false;
    }

    if ($isValid && !$payment->hasValidCard()) {
        $isValid = false;
    }

    if ($isValid && $payment->isExpired()) {
        $isValid = false;
    }

    return $isValid;
}
```

**After (with early return):**

```php
<?php declare(strict_types=1);

function validatePayment(Payment $payment): bool
{
    if ($payment->getAmount() <= 0) {
        return false;
    }

    if (!$payment->hasValidCard()) {
        return false;
    }

    if ($payment->isExpired()) {
        return false;
    }

    return true;
}
```

Alternatively, using match expressions (PHP 8.0+):

```php
<?php declare(strict_types=1);

function validatePayment(Payment $payment): bool
{
    return match (true) {
        $payment->getAmount() <= 0 => false,
        !$payment->hasValidCard() => false,
        $payment->isExpired() => false,
        default => true,
    };
}
```

## Benefits

- **Transparent Flow**: The execution path is visible at each branch without tracking auxiliary state
- **Fewer Moving Parts**: Removing flag variables shrinks the method's working set
- **Improved Efficiency**: Loops exit as soon as the answer is found instead of running to completion
- **Idiomatic Style**: Code uses language features as they were designed to be used
- **Simpler Tests**: Fewer conditional paths mean fewer scenarios to exercise

## When NOT to Use

Do **not** apply this refactoring when:

- **Multiple Exit Points Required**: If you genuinely need multiple flags to track different states (consider refactoring into separate methods instead)
- **Async Operations**: When flag manipulation is required across asynchronous boundaries
- **Complex State Machines**: If the logic represents a complex state machine (use proper state pattern instead)
- **Performance Critical**: In extremely tight loops where every variable matters (unlikely in modern PHP)

## Related Refactorings

- **Extract Method**: Extract complex conditions into separate, well-named methods
- **Replace Nested Conditionals with Guard Clauses**: Simplify nested if statements
- **Replace Conditional with Polymorphism**: Use object-oriented design for complex branching logic
- **Consolidate Duplicate Conditional Fragments**: Reduce code duplication in conditionals
