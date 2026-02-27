## Overview

This refactoring strips away an unnecessary back-reference between two classes that are linked bidirectionally. When one side of the relationship never actually uses its link to the other, that link is dead weight. Removing it yields simpler classes with fewer obligations.

## Motivation

### When to Apply

- **Unused back-reference**: One class holds a reference to the other but never accesses it
- **Alternative lookup paths**: The referenced object can be obtained through queries, parameters, or service calls instead
- **Memory overhead**: Circular references hinder garbage collection and waste memory
- **Excessive coupling**: Both classes are forced to know about each other when only one truly needs to
- **Maintenance burden**: Fewer dependencies make code easier to read and change

### Why It Matters

Bidirectional links carry a maintenance cost: they require synchronization code during object creation, modification, and destruction. Classes entangled in two-way references cannot be understood or modified independently. When one side of the link goes unused, the coupling is pure overhead.

## Mechanics: Step-by-Step

1. **Confirm the link is unnecessary**: Verify that one side never reads or writes the back-reference, or can obtain the same information through other means
2. **Identify alternative access paths**: Determine whether the needed data can come from method parameters, repository lookups, or service calls
3. **Redirect existing usage**: Replace any remaining direct field access with the alternative path
4. **Clean up assignment code**: Remove statements that set the back-reference during object creation or updates
5. **Delete the field**: Remove the now-unused reference field from the class
6. **Run the test suite**: Confirm that all behavior remains correct

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class Company
{
    private string $name;
    private array $employees = [];

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function addEmployee(Employee $employee): void
    {
        $this->employees[] = $employee;
        $employee->setCompany($this);
    }

    public function removeEmployee(Employee $employee): void
    {
        $key = array_search($employee, $this->employees, true);
        if ($key !== false) {
            unset($this->employees[$key]);
            $employee->setCompany(null);
        }
    }

    public function getEmployees(): array
    {
        return $this->employees;
    }

    public function getName(): string
    {
        return $this->name;
    }
}

class Employee
{
    private string $name;
    private ?Company $company = null;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function setCompany(?Company $company): void
    {
        $this->company = $company;
    }

    public function getCompany(): ?Company
    {
        return $this->company;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function reportWork(): void
    {
        // Company reference never used - only needs employee name
        echo "Employee {$this->name} is working";
    }
}
```

## After: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class Company
{
    private string $name;
    private array $employees = [];

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function addEmployee(Employee $employee): void
    {
        $this->employees[] = $employee;
    }

    public function removeEmployee(Employee $employee): void
    {
        $key = array_search($employee, $this->employees, true);
        if ($key !== false) {
            unset($this->employees[$key]);
        }
    }

    public function getEmployees(): array
    {
        return $this->employees;
    }

    public function getName(): string
    {
        return $this->name;
    }
}

class Employee
{
    private string $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function reportWork(): void
    {
        echo "Employee {$this->name} is working";
    }
}
```

## Benefits

- **Simpler Classes**: Dropping the unused link reduces the amount of code each class must maintain
- **Better Memory Behavior**: Eliminating circular references helps garbage collectors reclaim memory efficiently
- **Reduced Coupling**: Each class can evolve without worrying about its effect on the other
- **Straightforward Testing**: Independent classes need less setup in unit tests
- **Cleaner Lifecycle Management**: No synchronization logic is needed for the removed direction
- **Stronger Encapsulation**: Classes expose only the associations they genuinely depend on

## When NOT to Use

- **Both directions are actively used**: If both sides read the reference, the bidirectional link is justified
- **Performance-sensitive reverse lookups**: When replacing the direct reference with a database query would be too slow
- **Genuine mutual dependency**: Some domain relationships are inherently two-way
- **Published API constraints**: Removing the association may break consumers who depend on it
- **Incomplete analysis**: If you are unsure whether the back-reference is truly unused, investigate further before removing it

## Related Refactorings

- **Change Unidirectional Association to Bidirectional**: The reverse operation, adding a back-reference when needed
- **Extract Class**: Separates responsibilities to further reduce coupling
- **Move Method**: Shifts behavior closer to the data it operates on
- **Hide Delegate**: Wraps associations behind accessor methods to limit exposure
- **Remove Middle Man**: Eliminates intermediary objects that manage relationships unnecessarily
