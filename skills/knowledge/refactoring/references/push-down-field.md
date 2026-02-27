# Push Down Field

## Overview

Push Down Field moves a field from a superclass into the specific subclasses that actually use it. When a field declared at the parent level is relevant to only some children, relocating it narrows the parent's scope and ensures each class holds only the state it genuinely needs.

## Motivation

Fields sometimes land in a parent class during early design or optimistic planning, then remain there even after only a subset of subclasses turns out to need them. A field that sits unused in most children clutters the parent interface, introduces misleading state, and couples unrelated parts of the hierarchy. Moving it down to the subclasses that depend on it:

- Removes unnecessary baggage from classes that never touch the field
- Makes each class's responsibilities immediately visible from its declaration
- Trims the parent's surface area to genuinely shared concerns

## Mechanics

The refactoring process is straightforward:

1. Declare the field in all subclasses that use it
2. Remove the field from the superclass
3. Update any methods that reference the field

## Before/After Example

### Before (PHP 8.3+)

```php
abstract class Vehicle
{
    protected string $cargoCapacity;

    public function getCargoCapacity(): string
    {
        return $this->cargoCapacity;
    }
}

class Truck extends Vehicle
{
    public function loadCargo(string $cargo): void
    {
        // Uses cargoCapacity
    }
}

class Car extends Vehicle
{
    // Does not use cargoCapacity
}

class Bicycle extends Vehicle
{
    // Does not use cargoCapacity
}
```

### After (PHP 8.3+)

```php
abstract class Vehicle
{
    // cargoCapacity removed
}

class Truck extends Vehicle
{
    protected string $cargoCapacity;

    public function getCargoCapacity(): string
    {
        return $this->cargoCapacity;
    }

    public function loadCargo(string $cargo): void
    {
        // Uses cargoCapacity
    }
}

class Car extends Vehicle
{
    // No unnecessary cargoCapacity
}

class Bicycle extends Vehicle
{
    // No unnecessary cargoCapacity
}
```

## Benefits

- **Tighter Cohesion**: Each class holds only the state it works with, making its purpose self-evident
- **Lighter Parent**: The superclass no longer carries fields that some children ignore
- **Explicit Dependencies**: It is immediately clear which subclasses rely on a given field
- **Independent Evolution**: Subclasses can change field types or access patterns without affecting siblings
- **Focused Contracts**: The parent's interface reflects only genuinely shared behavior

## When NOT to Use

- When the field is actually used by all or most subclasses (it belongs in the parent)
- When the field represents core state that all subclasses need (consider the class hierarchy design)
- When you haven't identified which subclasses actually use the field
- When removing from parent would break existing client code that expects the field

## Related Refactorings

- **Pull Up Field** (opposite): Move a field from subclasses to the parent class
- **Push Down Method**: Move methods that are only used by specific subclasses
- **Extract Subclass**: Create new subclasses to hold specific fields and methods
- **Refused Bequest**: Addresses the code smell where subclasses don't use parent functionality

## Examples in Other Languages

### Java

**Before:**

```java
class Employee {
    String quota;
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```

**After:**

```java
class Employee {
}

class Salesman extends Employee {
    String quota;
}

class Engineer extends Employee {
}
```

### C#

**Before:**

```csharp
class Employee
{
    string quota;
}

class Salesman : Employee
{
}

class Engineer : Employee
{
}
```

**After:**

```csharp
class Employee
{
}

class Salesman : Employee
{
    string quota;
}

class Engineer : Employee
{
}
```

### Python

**Before:**

```python
class Employee:
    def __init__(self):
        self.quota = None

class Salesman(Employee):
    pass

class Engineer(Employee):
    pass
```

**After:**

```python
class Employee:
    pass

class Salesman(Employee):
    def __init__(self):
        super().__init__()
        self.quota = None

class Engineer(Employee):
    pass
```

### TypeScript

**Before:**

```typescript
class Employee {
    quota: string;
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```

**After:**

```typescript
class Employee {
}

class Salesman extends Employee {
    quota: string;
}

class Engineer extends Employee {
}
```
