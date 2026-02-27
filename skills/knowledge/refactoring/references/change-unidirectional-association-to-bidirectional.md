## Overview

This refactoring introduces a reverse link between two classes that currently have only a one-way association. When both sides of a relationship need to navigate to the other, adding the missing direction eliminates awkward workarounds and makes the domain model more expressive.

## Motivation

### When to Apply

- **Both sides need navigation**: Client code regularly needs to traverse the relationship in both directions
- **Costly reverse lookups**: Computing the reverse relationship through searches or global scans is inefficient
- **Clearer domain modeling**: The real-world relationship is naturally bidirectional
- **Workaround elimination**: The codebase contains clumsy patterns to simulate the missing direction
- **Simplified client code**: Consumers of both classes would benefit from direct access

### Why It Matters

Software requirements evolve, and a relationship that started as one-way often needs to support navigation in both directions. Without the reverse link, developers resort to global searches, parameter threading, or other fragile approaches. Adding the bidirectional association directly expresses the relationship at the cost of tighter coupling between the two classes.

## Mechanics: Step-by-Step

1. **Add a reverse field**: Create a field in the non-owning class to hold a reference back to the owning class
2. **Decide on ownership**: Determine which class is responsible for managing the association
3. **Build helper methods**: Add methods on the non-owning side to set and clear the back-reference
4. **Wire up the owning side**: Modify the owning class's add/remove methods to keep the back-reference in sync
5. **Centralize updates**: Ensure the association is only modified through the controlling methods
6. **Remove workarounds**: Delete any global lookups or parameter threading that simulated the reverse link
7. **Verify consistency**: Test that both directions stay synchronized under all operations

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class Department
{
    private string $name;
    private array $employees = [];

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function addEmployee(Employee $employee): void
    {
        $this->employees[] = $employee;
        // Employee doesn't know about its department
    }

    public function getEmployees(): array
    {
        return $this->employees;
    }
}

class Employee
{
    private string $name;
    // No reference back to Department - unidirectional only

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function getDepartmentName(): string
    {
        // Awkward workaround: must search all departments
        // This is inefficient and fragile
        foreach ($GLOBALS['allDepartments'] as $dept) {
            if (in_array($this, $dept->getEmployees())) {
                return $dept->getName();
            }
        }
        return 'Unknown';
    }
}
```

## After: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class Department
{
    private string $name;
    private array $employees = [];

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function addEmployee(Employee $employee): void
    {
        if (!in_array($employee, $this->employees, true)) {
            $this->employees[] = $employee;
            $employee->setDepartment($this);
        }
    }

    public function removeEmployee(Employee $employee): void
    {
        $key = array_search($employee, $this->employees, true);
        if ($key !== false) {
            unset($this->employees[$key]);
            $employee->setDepartment(null);
        }
    }

    public function getEmployees(): array
    {
        return array_values($this->employees);
    }
}

class Employee
{
    private string $name;
    private ?Department $department = null;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function setDepartment(?Department $department): void
    {
        $this->department = $department;
    }

    public function getDepartment(): ?Department
    {
        return $this->department;
    }

    public function getDepartmentName(): string
    {
        return $this->department?->getName() ?? 'Unassigned';
    }
}
```

## Benefits

- **Eliminates Workarounds**: No more global scans or parameter threading to find related objects
- **Faster Navigation**: Direct references are faster than searching or iterating collections
- **Explicit Modeling**: The code reflects the true shape of the domain relationship
- **Natural Traversal**: Both classes can reach the other without external help
- **Consistent Updates**: Synchronized add/remove methods keep both sides in agreement
- **Readable Code**: Relationships are self-evident from the class structure

## When NOT to Use

- **One direction is sufficient**: If only one side genuinely needs the reference, keep the association unidirectional
- **Infrequent reverse access**: Occasional reverse lookups may not justify the added coupling
- **Architectural boundaries**: Bidirectional links can violate layering constraints in modular architectures
- **Simple containment**: Basic one-to-many relationships where the child never needs to find its parent
- **Negligible but real overhead**: Maintaining synchronization has a cost, however small
- **Design clarity**: Some designs intentionally restrict navigation to enforce clean data flow

## Related Refactorings

- **Change Bidirectional Association to Unidirectional**: The inverse transformation, removing unnecessary coupling
- **Extract Class**: Useful when association management logic grows complex enough to warrant its own class
- **Encapsulate Collection**: Often applied alongside to safely manage bidirectional collection updates
- **Hide Delegate**: Reduces the surface area of exposed associations
- **Move Field**: Relocates association data when it belongs in a different class
