# Replace Parameter with Explicit Methods

## Overview

This refactoring breaks a single parameter-driven method into multiple dedicated methods, one per behavior variant. Rather than accepting a parameter that steers internal branching logic, each variant gets its own clearly named method. The result is a set of focused, single-purpose operations that replace one method doing many things based on conditional checks.

## Motivation

Parameter-driven methods become problematic when:

- **Readability degrades** - Calls like `setValue("height", 100)` force the reader to know what "height" means in context
- **Methods bloat** - Every new parameter variant introduces another branch, inflating cyclomatic complexity
- **Maintenance risk grows** - Altering one variant's logic can accidentally break others sharing the same method body
- **Variants are stable** - When the set of parameter values rarely changes, individual methods are a better fit

The refactoring is most worthwhile when each variant carries meaningful, non-trivial logic of its own.

## Mechanics

The process consists of four steps:

1. **Define explicit methods** - Create a separate method with a descriptive name for each parameter value variant
2. **Migrate logic** - Move each conditional branch's body into the corresponding new method
3. **Redirect callers** - Change every call site to invoke the appropriate explicit method instead
4. **Delete the original** - Remove the parameter-driven method once no callers remain

## Before/After Examples

### Example 1: Simple Case (PHP 8.3+)

**Before:**
```php
class Rectangle
{
    private float $width = 0;
    private float $height = 0;

    public function setValue(string $name, float $value): void
    {
        match ($name) {
            'height' => $this->height = $value,
            'width' => $this->width = $value,
            default => throw new InvalidArgumentException("Unknown dimension: {$name}"),
        };
    }
}

// Usage
$rect = new Rectangle();
$rect->setValue('height', 100);
$rect->setValue('width', 50);
```

**After:**
```php
class Rectangle
{
    private float $width = 0;
    private float $height = 0;

    public function setHeight(float $value): void
    {
        $this->height = $value;
    }

    public function setWidth(float $value): void
    {
        $this->width = $value;
    }
}

// Usage
$rect = new Rectangle();
$rect->setHeight(100);
$rect->setWidth(50);
```

### Example 2: Complex Logic (PHP 8.3+)

**Before:**
```php
class Employee
{
    public function getDaysOff(string $type): int
    {
        return match ($type) {
            'annual' => $this->calculateAnnualDaysOff(),
            'sick' => $this->calculateSickDaysOff(),
            'parental' => $this->calculateParentalDaysOff(),
            default => 0,
        };
    }

    private function calculateAnnualDaysOff(): int
    {
        // Complex calculation based on tenure, location, etc.
        return $this->yearsOfService * 2 + 5;
    }

    private function calculateSickDaysOff(): int
    {
        // Country-specific rules
        return match ($this->country) {
            'US' => 5,
            'EU' => 10,
            default => 0,
        };
    }

    private function calculateParentalDaysOff(): int
    {
        // Complex calculation with gender and local laws
        return $this->gender === 'F' ? 180 : 90;
    }
}

// Usage
$employee = new Employee();
$annual = $employee->getDaysOff('annual');
$sick = $employee->getDaysOff('sick');
```

**After:**
```php
class Employee
{
    public function getAnnualDaysOff(): int
    {
        return $this->yearsOfService * 2 + 5;
    }

    public function getSickDaysOff(): int
    {
        return match ($this->country) {
            'US' => 5,
            'EU' => 10,
            default => 0,
        };
    }

    public function getParentalDaysOff(): int
    {
        return $this->gender === 'F' ? 180 : 90;
    }
}

// Usage
$employee = new Employee();
$annual = $employee->getAnnualDaysOff();
$sick = $employee->getSickDaysOff();
```

## Benefits

- **Self-documenting code** - Names like `setHeight()` convey intent instantly without needing comments
- **Type safety** - Each method can declare the exact parameter types and counts it requires
- **IDE support** - Autocompletion and inline parameter hints work naturally with distinct methods
- **Easier testing** - Individual methods can be exercised in isolation
- **Lower complexity** - Conditional branching within a single method body disappears entirely
- **Better refactoring** - Explicit methods are simpler to optimize or override in subclasses

## When NOT to Use

Avoid this refactoring when:

- **Variants change frequently** - If new parameter values are added regularly, maintaining many methods becomes tedious
- **Few variants exist** - A method with only one or two conditional branches may not warrant splitting
- **Parameters are dynamic** - When values originate from user input or runtime configuration, a parameterized approach is necessary
- **Generic APIs** - Framework-level methods designed to accept open-ended parameters should stay parameter-driven

## Related Refactorings

- **Parameterize Method** - The inverse refactoring; merges several similar methods into one that takes a parameter
- **Replace Conditional with Polymorphism** - When variants map to distinct types, use inheritance or interfaces
- **Extract Method** - Frequently applied first to pull conditional branches into helper methods
- **Remove Middle Man** - The counterpoint when explicit methods devolve into trivial pass-through wrappers

## Examples in Other Languages

### Java

**Before:**
```java
void setValue(String name, int value) {
  if (name.equals("height")) {
    height = value;
    return;
  }
  if (name.equals("width")) {
    width = value;
    return;
  }
  Assert.shouldNeverReachHere();
}
```

**After:**
```java
void setHeight(int arg) {
  height = arg;
}
void setWidth(int arg) {
  width = arg;
}
```

### C#

**Before:**
```csharp
void SetValue(string name, int value)
{
  if (name.Equals("height"))
  {
    height = value;
    return;
  }
  if (name.Equals("width"))
  {
    width = value;
    return;
  }
  Assert.Fail();
}
```

**After:**
```csharp
void SetHeight(int arg)
{
  height = arg;
}
void SetWidth(int arg)
{
  width = arg;
}
```

### Python

**Before:**
```python
def output(self, name):
    if name == "banner"
        # Print the banner.
        # ...
    if name == "info"
        # Print the info.
        # ...
```

**After:**
```python
def outputBanner(self):
    # Print the banner.
    # ...

def outputInfo(self):
    # Print the info.
    # ...
```

### TypeScript

**Before:**
```typescript
setValue(name: string, value: number): void {
  if (name.equals("height")) {
    height = value;
    return;
  }
  if (name.equals("width")) {
    width = value;
    return;
  }
}
```

**After:**
```typescript
setHeight(arg: number): void {
  height = arg;
}
setWidth(arg: number): number {
  width = arg;
}
```
