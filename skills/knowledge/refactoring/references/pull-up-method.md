## Overview

Pull Up Method consolidates identical or nearly identical methods from multiple subclasses into their shared superclass. When sibling classes carry the same implementation of a method, hoisting it into the parent eliminates the redundancy and guarantees that every subclass uses a single, consistent version.

## Motivation

Duplicate methods spread across subclasses are a maintenance hazard. Each change must be replicated in every copy, and any omission introduces inconsistencies that surface as bugs. Pulling the method into the superclass creates one authoritative implementation that all children inherit, shrinking the codebase and making future modifications straightforward.

## Mechanics

1. **Examine similar methods** across subclasses to identify candidates for consolidation
2. **Standardize implementations** if methods differ slightly by adjusting their logic to work universally
3. **Handle subclass-specific dependencies** using Pull Up Field or abstract getter/setter methods
4. **Move the method** to the superclass
5. **Remove duplicate implementations** from all subclasses
6. **Test thoroughly** to ensure behavior remains consistent across the class hierarchy

## Before/After Code

### Before (PHP 8.3+)

```php
abstract class Employee {
    protected string $name;

    public function __construct(string $name) {
        $this->name = $name;
    }
}

class Manager extends Employee {
    public function getAnnualBonus(): float {
        return 5000.0;
    }
}

class Developer extends Employee {
    public function getAnnualBonus(): float {
        return 5000.0;
    }
}

class Designer extends Employee {
    public function getAnnualBonus(): float {
        return 5000.0;
    }
}
```

### After (PHP 8.3+)

```php
abstract class Employee {
    protected string $name;

    public function __construct(string $name) {
        $this->name = $name;
    }

    public function getAnnualBonus(): float {
        return 5000.0;
    }
}

class Manager extends Employee {}

class Developer extends Employee {}

class Designer extends Employee {}
```

## Benefits

- **No more copies**: A single implementation serves the entire hierarchy
- **Automatic consistency**: All subclasses inherit the same logic without manual synchronization
- **Lower bug risk**: Edits happen in one place, preventing one-off oversights
- **Leaner hierarchy**: Subclasses shrink, making the class tree easier to scan
- **Foundation for patterns**: A pulled-up method can become the skeleton of a Template Method

## When NOT to Use

- When methods in subclasses have fundamentally different implementations and only appear similar on the surface
- When pulling up a method would require the superclass to know about subclass-specific details
- When the method relies on state that exists only in specific subclasses and cannot be abstracted
- When the overhead of abstraction outweighs the benefit of code reuse

## Related Refactorings

- **Push Down Method**: The opposite operation; moves methods from superclass down to specific subclasses
- **Pull Up Field**: Consolidates fields from subclasses into the superclass
- **Extract Method**: Often used in conjunction to identify and isolate duplicate logic before pulling up
- **Template Method Pattern**: Can be formed by pulling up methods and leaving specific steps to be overridden by subclasses

## Examples in Other Languages

### Java

**Before:**

```java
class Employee {
    // ...
}

class Salesman extends Employee {
    String getName() {
        // ...
    }
}

class Engineer extends Employee {
    String getName() {
        // ...
    }
}
```

**After:**

```java
class Employee {
    String getName() {
        // ...
    }
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```

### C#

**Before:**

```csharp
class Employee
{
    // ...
}

class Salesman : Employee
{
    string GetName()
    {
        // ...
    }
}

class Engineer : Employee
{
    string GetName()
    {
        // ...
    }
}
```

**After:**

```csharp
class Employee
{
    string GetName()
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

### Python

**Before:**

```python
class Employee:
    pass

class Salesman(Employee):
    def get_name(self) -> str:
        # ...

class Engineer(Employee):
    def get_name(self) -> str:
        # ...
```

**After:**

```python
class Employee:
    def get_name(self) -> str:
        # ...

class Salesman(Employee):
    pass

class Engineer(Employee):
    pass
```

### TypeScript

**Before:**

```typescript
class Employee {
    // ...
}

class Salesman extends Employee {
    getName(): string {
        // ...
    }
}

class Engineer extends Employee {
    getName(): string {
        // ...
    }
}
```

**After:**

```typescript
class Employee {
    getName(): string {
        // ...
    }
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```
