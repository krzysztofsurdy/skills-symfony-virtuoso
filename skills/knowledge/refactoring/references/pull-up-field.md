# Pull Up Field Refactoring

## Overview

Pull Up Field moves a field that appears in multiple subclasses into their common superclass. When two or more child classes declare the same field for the same purpose, centralizing the declaration in the parent removes the redundancy and establishes a single authoritative location for the shared state.

## Motivation

Repeated field declarations across sibling classes produce several downsides:

- **Scattered updates**: Renaming or changing the field type must be done in every subclass
- **Silent divergence**: Subclasses may gradually handle the field differently, introducing subtle bugs
- **Blocked consolidation**: Methods that depend on the duplicated field cannot be pulled up until the field itself is consolidated
- **Obscured intent**: The fact that the field is shared across the hierarchy is not visible from any single class

Lifting the field into the parent creates one definition that all subclasses inherit, enabling further refactorings and making the shared nature of the data explicit.

## Mechanics

1. **Analyze the fields**: Verify that the fields in different subclasses serve identical purposes
2. **Standardize naming**: If fields have different names, choose a consistent name
3. **Declare in superclass**: Add the field to the parent class with appropriate visibility (typically `protected`)
4. **Remove from subclasses**: Delete the field declarations from all subclasses
5. **Update references**: Ensure all code correctly references the inherited field
6. **Consider encapsulation**: Apply Self Encapsulate Field to hide the field behind accessor methods

## Before/After PHP 8.3+ Code

### Before: Duplicate Fields in Subclasses

```php
abstract class Employee
{
    protected string $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    abstract public function calculateSalary(): float;
}

class Developer extends Employee
{
    private string $department;
    private int $yearsExperience;
    private array $skills;

    public function __construct(string $name, string $department, int $yearsExperience, array $skills)
    {
        parent::__construct($name);
        $this->department = $department;
        $this->yearsExperience = $yearsExperience;
        $this->skills = $skills;
    }

    public function calculateSalary(): float
    {
        return 50000 + ($this->yearsExperience * 2000);
    }
}

class Designer extends Employee
{
    private string $department;
    private int $yearsExperience;
    private array $specializations;

    public function __construct(string $name, string $department, int $yearsExperience, array $specializations)
    {
        parent::__construct($name);
        $this->department = $department;
        $this->yearsExperience = $yearsExperience;
        $this->specializations = $specializations;
    }

    public function calculateSalary(): float
    {
        return 45000 + ($this->yearsExperience * 1500);
    }
}
```

### After: Fields Pulled Up to Superclass

```php
abstract class Employee
{
    protected string $name;
    protected string $department;
    protected int $yearsExperience;

    public function __construct(
        string $name,
        string $department,
        int $yearsExperience
    ) {
        $this->name = $name;
        $this->department = $department;
        $this->yearsExperience = $yearsExperience;
    }

    abstract public function calculateSalary(): float;
}

class Developer extends Employee
{
    private array $skills;

    public function __construct(
        string $name,
        string $department,
        int $yearsExperience,
        array $skills
    ) {
        parent::__construct($name, $department, $yearsExperience);
        $this->skills = $skills;
    }

    public function calculateSalary(): float
    {
        return 50000 + ($this->yearsExperience * 2000);
    }
}

class Designer extends Employee
{
    private array $specializations;

    public function __construct(
        string $name,
        string $department,
        int $yearsExperience,
        array $specializations
    ) {
        parent::__construct($name, $department, $yearsExperience);
        $this->specializations = $specializations;
    }

    public function calculateSalary(): float
    {
        return 45000 + ($this->yearsExperience * 1500);
    }
}
```

## Benefits

- **Single definition**: One field declaration replaces several identical ones
- **Uniform behavior**: All subclasses share the same storage and access rules
- **Stronger type guarantees**: A centralized declaration enforces a consistent type across the hierarchy
- **Unlocks further refactoring**: Methods that use the field can now be pulled up as well
- **Visible hierarchy design**: The parent class clearly communicates which state is shared

## When NOT to Use

- **Different purposes**: If subclasses use similarly-named fields for different purposes, pulling up creates false cohesion
- **Different initialization logic**: When subclasses initialize the same field differently, consolidation may add unnecessary complexity
- **Temporary fields**: Avoid pulling up fields used by only one or two subclasses; extract a new subclass instead
- **Conditional usage**: If not all subclasses actually need the field, consider using composition or creating intermediate abstract classes

## Related Refactorings

- **Pull Up Method**: Consolidate duplicate methods the same way as fields
- **Push Down Field**: The opposite operation when fields need to be moved to subclasses
- **Extract Superclass**: Create a new superclass when duplication spans unrelated classes
- **Self Encapsulate Field**: Hide the field behind getter/setter methods for better control
- **Replace Data with Object**: Convert primitive fields to dedicated objects for richer behavior

## Examples in Other Languages

### Java

**Before:**

```java
class Employee {
    String name;
}

class Salesman extends Employee {
    String department;
}

class Engineer extends Employee {
    String department;
}
```

**After:**

```java
class Employee {
    String name;
    String department;
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
    string name;
}

class Salesman : Employee
{
    string department;
}

class Engineer : Employee
{
    string department;
}
```

**After:**

```csharp
class Employee
{
    string name;
    string department;
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
    def __init__(self, name: str):
        self.name = name

class Salesman(Employee):
    def __init__(self, name: str, department: str):
        super().__init__(name)
        self.department = department

class Engineer(Employee):
    def __init__(self, name: str, department: str):
        super().__init__(name)
        self.department = department
```

**After:**

```python
class Employee:
    def __init__(self, name: str, department: str):
        self.name = name
        self.department = department

class Salesman(Employee):
    pass

class Engineer(Employee):
    pass
```

### TypeScript

**Before:**

```typescript
class Employee {
    name: string;
}

class Salesman extends Employee {
    department: string;
}

class Engineer extends Employee {
    department: string;
}
```

**After:**

```typescript
class Employee {
    name: string;
    department: string;
}

class Salesman extends Employee {
}

class Engineer extends Employee {
}
```
