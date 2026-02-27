## Overview

This refactoring removes a superfluous back-reference from a bidirectional relationship between two classes. When one side of a two-way link never actually uses its connection to the other, that connection serves no purpose and only adds complexity. Eliminating it produces leaner classes with fewer responsibilities.

## Motivation

### When to Apply

- **Dormant reference**: One class maintains a link to the other but never reads or writes through it
- **Indirect access suffices**: The referenced object can be retrieved via queries, method arguments, or services instead
- **Resource waste**: Circular references interfere with garbage collection and consume unnecessary memory
- **Unnecessary coupling**: Both classes are forced into mutual awareness when only one genuinely depends on the other
- **Simpler evolution**: Fewer interdependencies make the code easier to understand and modify

### Why It Matters

Two-way associations impose ongoing coordination costs: they demand synchronization logic whenever objects are created, updated, or destroyed. Classes bound by bidirectional references cannot be comprehended or changed independently. When one direction of the link sits unused, the resulting coupling is pure waste.

## Mechanics: Step-by-Step

1. **Verify the link is unused**: Confirm that one class never reads, writes, or otherwise relies on the back-reference, or that the same data is reachable by other means
2. **Map out alternative access paths**: Determine whether the needed information can arrive through method arguments, repository queries, or service lookups
3. **Reroute existing usage**: Swap any remaining direct field access with the alternative path
4. **Strip assignment code**: Remove statements that establish or update the back-reference during object lifecycle events
5. **Drop the field**: Delete the now-unused reference property from the class
6. **Execute the test suite**: Verify that all behavior is preserved

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

- **Leaner Classes**: Removing the unused link cuts down on code each class must carry
- **Improved Memory Management**: Breaking circular references allows garbage collectors to reclaim memory more efficiently
- **Lower Coupling**: Each class can change independently without ripple effects on the other
- **Easier Testing**: Classes that stand alone require less scaffolding in unit tests
- **Simplified Lifecycle**: No synchronization logic is required for the eliminated direction
- **Tighter Encapsulation**: Classes only expose associations they genuinely rely on

## When NOT to Use

- **Both directions see active use**: If both classes read the reference, the bidirectional link is warranted
- **Reverse lookup performance**: When substituting the direct reference with a database query would introduce unacceptable latency
- **Inherently mutual relationships**: Some domain concepts are naturally two-way
- **Published API surface**: Removing the association may break external consumers who depend on it
- **Uncertain usage**: If you cannot confirm the back-reference is truly unused, investigate thoroughly before deleting it

## Related Refactorings

- **Change Unidirectional Association to Bidirectional**: The reverse operation, introducing a back-reference when needed
- **Extract Class**: Separates responsibilities to further decrease coupling
- **Move Method**: Relocates behavior closer to the data it operates on
- **Hide Delegate**: Wraps associations behind accessor methods to limit exposure
- **Remove Middle Man**: Strips out intermediary objects that manage relationships unnecessarily
