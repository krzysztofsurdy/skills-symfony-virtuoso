## Overview

Introduce Local Extension creates a subclass or wrapper around a third-party or legacy class to add methods the original class does not provide. Rather than modifying foreign code or spreading workaround logic throughout your application, you build a local extension that augments the class's capabilities while keeping the original untouched.

## Motivation

### When to Apply

- **Library gaps**: An external class is missing methods your domain requires
- **Legacy augmentation**: You need new behavior on a class whose source you should not touch
- **Incomplete APIs**: The library does not cover all the operations your use case demands
- **Safe extension**: PHP does not support open classes, so inheritance or composition fills the gap
- **Diverging needs**: Your application requires domain-specific operations the library author would not accept upstream
- **Upgrade safety**: Adding functionality locally avoids depending on a newer (potentially breaking) version of the library

### Why It Matters

A local extension keeps your additions organized in a single class rather than scattered as foreign methods or inline workarounds. It provides the full method-call experience on the extended class, maintains compatibility with the original, and isolates your changes from library updates.

## Mechanics: Step-by-Step

1. **Pinpoint the missing functionality**: Determine which methods the foreign class lacks
2. **Choose the approach**: Subclass (inheritance) if the class is open for extension; wrapper (composition) if it is final or sealed
3. **Build the extension class**: Create a class that inherits from or wraps the original
4. **Add the missing methods**: Implement the desired functionality in the extension
5. **Migrate callers**: Replace direct use of the original class with the extension where the new methods are needed
6. **Test everything**: Verify that new methods work and existing behavior is unaffected
7. **Document clearly**: Mark the class as a local extension of foreign code

## Before: PHP 8.3+ Example

```php
<?php

declare(strict_types=1);

class DateProcessor
{
    private DateTime $date;

    public function __construct()
    {
        $this->date = new DateTime('2024-01-15');
    }

    public function displayFormattedDate(): string
    {
        // DateTime doesn't provide isWeekend() method
        // We need to add this functionality ourselves

        $dayOfWeek = (int) $this->date->format('w');
        $isWeekend = $dayOfWeek === 0 || $dayOfWeek === 6;

        return sprintf(
            'Date: %s (%s)',
            $this->date->format('Y-m-d'),
            $isWeekend ? 'Weekend' : 'Weekday'
        );
    }

    public function getQuarter(): int
    {
        $month = (int) $this->date->format('m');
        return (int) ceil($month / 3);
    }

    public function getDaysSinceEpoch(): int
    {
        $epoch = new DateTime('1970-01-01');
        $diff = $this->date->diff($epoch);
        return (int) $diff->days;
    }
}
```

## After: PHP 8.3+ Example

### Solution 1: Inheritance-based Extension

```php
<?php

declare(strict_types=1);

/**
 * Local extension of DateTime class with domain-specific functionality.
 * Inherits from DateTime to add business logic methods.
 */
class LocalDateTime extends DateTime
{
    /**
     * Check if the date falls on a weekend.
     */
    public function isWeekend(): bool
    {
        $dayOfWeek = (int) $this->format('w');
        return $dayOfWeek === 0 || $dayOfWeek === 6;
    }

    /**
     * Get the calendar quarter (1-4) for this date.
     */
    public function getQuarter(): int
    {
        $month = (int) $this->format('m');
        return (int) ceil($month / 3);
    }

    /**
     * Calculate days since Unix epoch.
     */
    public function getDaysSinceEpoch(): int
    {
        $epoch = new DateTime('1970-01-01');
        $diff = $this->diff($epoch);
        return (int) $diff->days;
    }

    /**
     * Check if date is in the future.
     */
    public function isFuture(): bool
    {
        return $this > new DateTime('now');
    }

    /**
     * Get human-readable relative date (e.g., "2 days ago").
     */
    public function getRelativeFormat(): string
    {
        $now = new DateTime('now');
        $interval = $now->diff($this);

        if ($interval->days === 0) {
            return 'Today';
        }

        if ($interval->days === 1 && $interval->invert === 1) {
            return 'Yesterday';
        }

        if ($interval->days === 1 && $interval->invert === 0) {
            return 'Tomorrow';
        }

        $direction = $interval->invert === 1 ? 'ago' : 'in';
        return sprintf('%d days %s', $interval->days, $direction);
    }
}

class DateProcessor
{
    private LocalDateTime $date;

    public function __construct()
    {
        $this->date = new LocalDateTime('2024-01-15');
    }

    public function displayFormattedDate(): string
    {
        return sprintf(
            'Date: %s (%s)',
            $this->date->format('Y-m-d'),
            $this->date->isWeekend() ? 'Weekend' : 'Weekday'
        );
    }

    public function getQuarter(): int
    {
        return $this->date->getQuarter();
    }

    public function getDaysSinceEpoch(): int
    {
        return $this->date->getDaysSinceEpoch();
    }
}
```

### Solution 2: Composition-based Extension (Safer Alternative)

```php
<?php

declare(strict_types=1);

/**
 * Local extension using composition.
 * Wraps DateTime to add domain-specific functionality.
 */
class LocalDateWrapper
{
    public function __construct(
        private readonly DateTime $dateTime
    ) {
    }

    public static function now(): self
    {
        return new self(new DateTime('now'));
    }

    public static function fromString(string $dateString): self
    {
        return new self(new DateTime($dateString));
    }

    public function isWeekend(): bool
    {
        $dayOfWeek = (int) $this->dateTime->format('w');
        return $dayOfWeek === 0 || $dayOfWeek === 6;
    }

    public function getQuarter(): int
    {
        $month = (int) $this->dateTime->format('m');
        return (int) ceil($month / 3);
    }

    public function getDaysSinceEpoch(): int
    {
        $epoch = new DateTime('1970-01-01');
        $diff = $this->dateTime->diff($epoch);
        return (int) $diff->days;
    }

    public function isFuture(): bool
    {
        return $this->dateTime > new DateTime('now');
    }

    public function getRelativeFormat(): string
    {
        $now = new DateTime('now');
        $interval = $now->diff($this->dateTime);

        if ($interval->days === 0) {
            return 'Today';
        }

        if ($interval->days === 1 && $interval->invert === 1) {
            return 'Yesterday';
        }

        if ($interval->days === 1 && $interval->invert === 0) {
            return 'Tomorrow';
        }

        $direction = $interval->invert === 1 ? 'ago' : 'in';
        return sprintf('%d days %s', $interval->days, $direction);
    }

    // Delegate to wrapped DateTime
    public function format(string $format): string
    {
        return $this->dateTime->format($format);
    }

    public function diff(DateTime $other, bool $absolute = false): DateInterval
    {
        return $this->dateTime->diff($other, $absolute);
    }
}

class DateProcessor
{
    private LocalDateWrapper $date;

    public function __construct()
    {
        $this->date = LocalDateWrapper::fromString('2024-01-15');
    }

    public function displayFormattedDate(): string
    {
        return sprintf(
            'Date: %s (%s)',
            $this->date->format('Y-m-d'),
            $this->date->isWeekend() ? 'Weekend' : 'Weekday'
        );
    }

    public function getQuarter(): int
    {
        return $this->date->getQuarter();
    }

    public function getDaysSinceEpoch(): int
    {
        return $this->date->getDaysSinceEpoch();
    }
}
```

## Benefits

- **Preserves the original**: Third-party or legacy code stays untouched
- **Conflict-free upgrades**: Library updates do not collide with your additions
- **Organized extensions**: All custom behavior lives in a single, dedicated class
- **Application-specific features**: Add exactly the methods your domain needs without polluting a general-purpose class
- **Testable in isolation**: The extension class can be unit tested independently
- **Reusable across the codebase**: Any module can use the extension without duplicating workarounds
- **Discoverable**: A named extension class is easier to find than scattered helper functions
- **Clean OOP approach**: Avoids monkey-patching or runtime class modification

## When NOT to Use

- **You own the class**: Modify it directly instead of creating a wrapper
- **A single helper method suffices**: A foreign method may be simpler than a full extension class
- **Constant additions**: If you keep adding methods, reconsider whether you should own a fork or contribute upstream
- **Liskov violation risk**: Do not extend a class in a way that changes its fundamental behavior
- **Excessive delegation overhead**: If nearly every method must be delegated, inheritance may be a better fit
- **Official extension points exist**: Use the library's plugin or extension API when available
- **Performance-critical paths**: Composition adds a thin layer of indirection (usually negligible)

## Related Refactorings

- **Extract Class**: Organizes the new functionality into a dedicated class
- **Replace Conditional with Polymorphism**: Useful when behavior varies significantly between the base and extension
- **Adapter Pattern**: Focused on interface compatibility rather than feature addition
- **Decorator Pattern**: Adds responsibilities dynamically, offering more flexibility than subclassing
- **Introduce Foreign Method**: A lighter alternative when only one or two methods are needed
