# Push Down Method

## Overview

Push Down Method relocates a method from a superclass into the specific subclass or subclasses that actually call it. When a parent class carries behavior that only a fraction of its children require, pushing the method down removes irrelevant operations from the parent and keeps each class focused on what it genuinely does.

## Motivation

Apply Push Down Method when:

- A method was designed for general use but turns out to be relevant to only one or a few subclasses
- Hierarchy evolution or feature removal has left a method orphaned in the parent
- The parent exposes behavior that does not apply to all descendants
- Subclasses inherit methods they never invoke, producing a refused-bequest smell

## Mechanics

The refactoring process follows these straightforward steps:

1. **Declare the method in the target subclass** - Add the method signature and implementation to the subclass that actually needs it
2. **Remove the method from the superclass** - Delete the original method from the parent class
3. **Update all references** - Ensure all calls to the method go through the subclass where it now resides
4. **Verify type safety** - Check that all usages occur within the intended subclass or through proper type narrowing

## Before/After (PHP 8.3+)

### Before

```php
abstract class Vehicle
{
    protected string $model;
    protected float $price;

    public function __construct(string $model, float $price)
    {
        $this->model = $model;
        $this->price = $price;
    }

    /**
     * Only used by Car subclass, not by Motorcycle
     */
    public function getNumberOfDoors(): int
    {
        return 4;
    }

    abstract public function getMaxSpeed(): float;
}

final class Car extends Vehicle
{
    public function getMaxSpeed(): float
    {
        return 200.0;
    }
}

final class Motorcycle extends Vehicle
{
    public function getMaxSpeed(): float
    {
        return 220.0;
    }
}
```

### After

```php
abstract class Vehicle
{
    protected string $model;
    protected float $price;

    public function __construct(string $model, float $price)
    {
        $this->model = $model;
        $this->price = $price;
    }

    abstract public function getMaxSpeed(): float;
}

final class Car extends Vehicle
{
    public function getMaxSpeed(): float
    {
        return 200.0;
    }

    public function getNumberOfDoors(): int
    {
        return 4;
    }
}

final class Motorcycle extends Vehicle
{
    public function getMaxSpeed(): float
    {
        return 220.0;
    }
}
```

## Benefits

- **Focused parent class**: The superclass exposes only behavior common to all children
- **Cleaner abstractions**: Irrelevant methods no longer appear on unrelated subclasses
- **Less confusion**: Developers are not puzzled by inherited methods that have no meaning for certain classes
- **Precise encapsulation**: Each class publishes exactly the interface it supports
- **Localized impact**: Future changes to the method affect only the subclass that owns it

## When NOT to Use

- **Avoid premature optimization** - Don't push down methods based on speculation about future usage
- **Don't create duplication** - If multiple unrelated subclasses need the method, consider keeping it in the parent class instead
- **Template Method pattern** - When a parent class method defines a skeleton that subclasses customize, keep it in the parent
- **Polymorphic behavior** - If the method is part of a polymorphic contract, pushing it down breaks the Liskov Substitution Principle
- **Shared functionality** - When several subclasses genuinely share the method, duplication introduces maintenance burden

## Related Refactorings

- **Pull Up Method** - The inverse operation; moves methods from subclasses to the parent class
- **Push Down Field** - Similar concept applied to fields instead of methods
- **Extract Subclass** - Often paired with Push Down Method to create specialized subclasses
- **Replace Type Code with Subclasses** - May involve pushing down methods to create type-specific behavior

## Examples in Other Languages

### Java

**Before:**

```java
class Employee {
    int getQuota() {
        // ...
    }
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
    int getQuota() {
        // ...
    }
}

class Engineer extends Employee {
}
```

### C#

**Before:**

```csharp
class Employee
{
    int GetQuota()
    {
        // ...
    }
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
    int GetQuota()
    {
        // ...
    }
}

class Engineer : Employee
{
}
```

### Python

**Before:**

```python
class Employee:
    def get_quota(self) -> int:
        # ...

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
    def get_quota(self) -> int:
        # ...

class Engineer(Employee):
    pass
```

### TypeScript

**Before:**

```typescript
class Employee {
    getQuota(): number {
        // ...
    }
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
    getQuota(): number {
        // ...
    }
}

class Engineer extends Employee {
}
```
