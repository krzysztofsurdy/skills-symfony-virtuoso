## Overview

Duplicate Observed Data resolves the problem of data being stored in both domain objects and UI components by introducing an observer-based synchronization mechanism. The domain model becomes the single source of truth, and UI components subscribe to it for automatic updates. This prevents the data drift that occurs when two copies of the same information must be kept in sync manually.

## Motivation

### When to Apply

- **Mirrored data**: The same information is stored in both the domain layer and UI layer
- **Synchronization failures**: Changes to the domain do not always reach the UI, or vice versa
- **Redundant update code**: Logic for updating both copies is scattered and easy to forget
- **Hidden bugs**: Stale data in one layer causes incorrect behavior that is hard to trace
- **Complex state tracking**: Multiple locations maintain overlapping information
- **Testing difficulty**: Data duplication makes it hard to test domain logic independently of the UI

### Why It Matters

Establishing a single authoritative data store (the domain model) and using observers to propagate changes eliminates an entire class of synchronization bugs. It also decouples the UI from the details of data storage, making both layers easier to test and modify independently.

## Mechanics: Step-by-Step

1. **Map the duplication**: Identify every place where the same data lives in both domain and UI
2. **Define an observer contract**: Create an interface that UI components will implement to receive change notifications
3. **Register observers**: Have UI components subscribe to the domain objects they depend on
4. **Notify on change**: Modify domain setters to broadcast notifications to all registered observers
5. **Remove cached copies**: Delete the duplicate data fields from UI components
6. **Read from the source**: Update UI accessors to fetch values directly from the domain model
7. **Verify synchronization**: Confirm that UI always reflects the current domain state, regardless of how changes originate

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class Person
{
    private string $name;
    private int $age;

    public function __construct(string $name, int $age)
    {
        $this->name = $name;
        $this->age = $age;
    }

    public function setName(string $name): void
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function setAge(int $age): void
    {
        $this->age = $age;
    }

    public function getAge(): int
    {
        return $this->age;
    }
}

class PersonUI
{
    private string $nameField;
    private int $ageField;
    private Person $person;

    public function __construct(Person $person)
    {
        $this->person = $person;
        // Duplicate data storage in UI
        $this->nameField = $person->getName();
        $this->ageField = $person->getAge();
    }

    public function updatePerson(string $name, int $age): void
    {
        // Must update both domain and UI separately
        $this->person->setName($name);
        $this->person->setAge($age);

        // Easy to forget these UI updates
        $this->nameField = $name;
        $this->ageField = $age;
    }

    public function getNameDisplay(): string
    {
        return $this->nameField;
    }

    public function getAgeDisplay(): int
    {
        return $this->ageField;
    }

    // Risk: Data can become out of sync if person is updated elsewhere
}
```

## After: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

interface Observer
{
    public function update(): void;
}

class Person
{
    private string $name;
    private int $age;
    /** @var Observer[] */
    private array $observers = [];

    public function __construct(string $name, int $age)
    {
        $this->name = $name;
        $this->age = $age;
    }

    public function attach(Observer $observer): void
    {
        $this->observers[] = $observer;
    }

    public function detach(Observer $observer): void
    {
        $this->observers = array_filter(
            $this->observers,
            fn(Observer $obs) => $obs !== $observer
        );
    }

    private function notifyObservers(): void
    {
        foreach ($this->observers as $observer) {
            $observer->update();
        }
    }

    public function setName(string $name): void
    {
        $this->name = $name;
        $this->notifyObservers();
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function setAge(int $age): void
    {
        $this->age = $age;
        $this->notifyObservers();
    }

    public function getAge(): int
    {
        return $this->age;
    }
}

class PersonUI implements Observer
{
    private Person $person;

    public function __construct(Person $person)
    {
        $this->person = $person;
        // Register as observer instead of storing duplicate data
        $person->attach($this);
    }

    public function update(): void
    {
        // Automatically called when person changes
        // No need to manually sync - read from domain directly
    }

    public function updatePerson(string $name, int $age): void
    {
        // Single update point - domain notifies observers
        $this->person->setName($name);
        $this->person->setAge($age);
    }

    public function getNameDisplay(): string
    {
        // Always reads from single source of truth
        return $this->person->getName();
    }

    public function getAgeDisplay(): int
    {
        // Always reads from single source of truth
        return $this->person->getAge();
    }

    public function __destruct()
    {
        $this->person->detach($this);
    }
}

// Usage
$person = new Person('John Doe', 30);
$ui = new PersonUI($person);

echo $ui->getNameDisplay(); // "John Doe"

// Update through UI
$ui->updatePerson('Jane Doe', 31);
echo $ui->getNameDisplay(); // "Jane Doe" - automatically synced

// Update domain directly - UI stays in sync automatically
$person->setName('Bob Smith');
echo $ui->getNameDisplay(); // "Bob Smith" - still synced
```

## Benefits

- **Authoritative Data Store**: The domain model is the only place data lives
- **Automatic Propagation**: UI components refresh themselves without manual coordination
- **No Stale Data**: Every read returns the current value from the source of truth
- **Cleaner Update Logic**: Duplicate update code disappears from the UI layer
- **Isolated Testing**: Domain and UI can be tested independently
- **Single Point of Change**: Structural changes to the data model happen in one place
- **Multiple Consumers**: Several UI components can observe the same domain object simultaneously
- **Loose Coupling**: The domain knows nothing about the UI; the UI depends on the domain through a generic observer contract

## When NOT to Use

- **Read-only or immutable data**: If data never changes, there is nothing to synchronize
- **High-frequency updates**: Notification overhead may be unacceptable in tight loops or real-time systems
- **Batched changes**: Frequent small updates can flood observers; consider batching or debouncing instead
- **Separate processes**: When domain and UI run in different processes or services, an observer within a single process is not sufficient
- **Heavily coupled legacy code**: Retrofitting the observer pattern into tightly coupled legacy systems may require extensive changes
- **One-way data flow**: If data only moves from UI to domain and never back, the duplication problem does not apply

## Related Refactorings

- **Extract Class**: Split observer management into a dedicated class if the domain object becomes too large
- **Replace Temp with Query**: Remove temporary variables that cache domain data
- **Replace Data Value with Object**: Promote primitive fields into richer objects that can participate in observation
- **Move Method**: Relocate observer-related logic to the class where it fits best
- **Introduce Parameter Object**: Group related observed fields into a single object
- **Observer Pattern**: The design pattern that underpins this refactoring
