## Overview

Decompose Conditional takes a tangled conditional expression and breaks it apart into well-named methods. Instead of forcing readers to mentally parse compound boolean logic or lengthy if-else chains, each condition and its associated action gets a descriptive name that communicates intent directly.

## Motivation

### When to Apply

- **Dense boolean expressions**: Conditions composed of multiple `&&` and `||` operators that require careful reading
- **Lengthy if-else chains**: Multi-branch conditionals where each branch handles a different scenario
- **Repeated conditions**: The same compound expression appears in several places
- **Hidden business rules**: The purpose of a condition is not obvious from the raw expression
- **Hard-to-test logic**: Complex conditionals resist focused unit testing
- **Mixed responsibilities**: A single conditional handles validation, business rules, and side effects simultaneously
- **Cognitive strain**: Developers have to pause and think to understand what the condition checks

### Why It Matters

Well-named methods act as documentation that stays in sync with the code. Extracting conditions into named methods turns opaque boolean logic into a readable narrative, makes each piece independently testable, and localizes future changes to a single spot.

## Mechanics: Step-by-Step

1. **Find the complex condition**: Locate if-else statements or compound boolean expressions
2. **Extract the condition**: Move it into a new method that returns a boolean
3. **Choose a meaningful name**: The method name should describe the question being asked, not the implementation
4. **Substitute the method call**: Replace the inline condition with a call to the new method
5. **Extract branch bodies if needed**: If the code inside a branch is substantial, extract that into a named method too
6. **Confirm behavior is preserved**: Run all tests to verify nothing has changed
7. **Repeat**: Apply the same treatment to other complex conditionals in the codebase

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class UserValidator
{
    public function validateUserRegistration(User $user, string $email): bool
    {
        // Complex condition with mixed concerns
        if (strlen($email) > 5 && str_contains($email, '@') &&
            $user->getAge() >= 18 && $user->getAge() <= 120 &&
            !$this->userRepository->emailExists($email) &&
            $user->getCountry() !== 'BLOCKED') {

            $this->emailService->sendConfirmation($email);
            $this->logger->info("User registration validated");
            return true;
        }

        if ($user->getAge() < 18 || $user->getAge() > 120) {
            $this->logger->warning("Invalid age: " . $user->getAge());
            return false;
        }

        if (strlen($email) <= 5 || !str_contains($email, '@')) {
            $this->logger->warning("Invalid email format");
            return false;
        }

        return false;
    }
}
```

## After: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class UserValidator
{
    public function validateUserRegistration(User $user, string $email): bool
    {
        if (!$this->isValidEmail($email)) {
            $this->logger->warning("Invalid email format");
            return false;
        }

        if (!$this->isValidAge($user->getAge())) {
            $this->logger->warning("Invalid age: {$user->getAge()}");
            return false;
        }

        if (!$this->isRegistrationAllowed($user, $email)) {
            return false;
        }

        $this->emailService->sendConfirmation($email);
        $this->logger->info("User registration validated");
        return true;
    }

    private function isValidEmail(string $email): bool
    {
        return strlen($email) > 5 && str_contains($email, '@');
    }

    private function isValidAge(int $age): bool
    {
        return $age >= 18 && $age <= 120;
    }

    private function isRegistrationAllowed(User $user, string $email): bool
    {
        return !$this->userRepository->emailExists($email) &&
               $user->getCountry() !== 'BLOCKED';
    }
}
```

## Benefits

- **Self-Documenting Logic**: Method names explain the business rules without comments
- **Independent Testability**: Each extracted condition can be tested in isolation
- **Lower Cognitive Load**: Readers grasp the flow without decoding boolean algebra
- **Localized Changes**: Modifying a business rule affects only its dedicated method
- **Reuse Across the Codebase**: Extracted conditions can be called from other methods that need the same check
- **Composable Checks**: Small, focused predicates combine naturally into larger validations
- **Safer Refactoring**: Narrow, well-tested methods are easier to modify without side effects

## When NOT to Use

- **Trivial conditions**: A single, readable comparison like `if ($age > 18)` does not benefit from extraction
- **Single-use, clear conditions**: If a condition is used once and already reads naturally, extraction adds indirection without value
- **Hot loops**: In extremely performance-sensitive paths, the overhead of method calls may matter (though this is rarely a practical concern)
- **Already decomposed**: If conditions are already short and descriptive, further decomposition adds clutter
- **No business meaning**: Extracting a condition that has no meaningful name does not improve readability

## Related Refactorings

- **Extract Method**: Used for the branch body when it contains substantial logic
- **Replace Conditional with Polymorphism**: Appropriate when conditions distinguish between object types
- **Extract Variable**: Introduces a named variable as a lighter alternative to a full method extraction
- **Guard Clauses**: A specific form of decomposition for precondition checks
- **Introduce Explaining Variable**: An intermediate step before full decomposition
- **Replace Temp with Query**: Removes temporary variables that hold intermediate condition results

## Examples in Other Languages

### Java

**Before:**
```java
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
  charge = quantity * winterRate + winterServiceCharge;
}
else {
  charge = quantity * summerRate;
}
```

**After:**
```java
if (isSummer(date)) {
  charge = summerCharge(quantity);
}
else {
  charge = winterCharge(quantity);
}
```

### C#

**Before:**
```csharp
if (date < SUMMER_START || date > SUMMER_END)
{
  charge = quantity * winterRate + winterServiceCharge;
}
else
{
  charge = SummerCharge(quantity);
}
```

**After:**
```csharp
if (isSummer(date))
{
  charge = SummerCharge(quantity);
}
else
{
  charge = WinterCharge(quantity);
}
```

### Python

**Before:**
```python
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winterRate + winterServiceCharge
else:
    charge = quantity * summerRate
```

**After:**
```python
if isSummer(date):
    charge = summerCharge(quantity)
else:
    charge = winterCharge(quantity)
```

### TypeScript

**Before:**
```typescript
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
  charge = quantity * winterRate + winterServiceCharge;
}
else {
  charge = quantity * summerRate;
}
```

**After:**
```typescript
if (isSummer(date)) {
  charge = summerCharge(quantity);
}
else {
  charge = winterCharge(quantity);
}
```
