## Overview

Remove Parameter strips an unused parameter from a method signature. When a parameter is never referenced inside the method body, it adds noise to the interface and forces callers to supply a value that serves no purpose. Dropping it produces a cleaner contract that accurately reflects what the method actually needs.

## Motivation

Unused parameters cause several problems:

- **Wasted attention**: Developers spend effort figuring out why the parameter exists when it contributes nothing
- **Misleading signatures**: The method promises to use data it ignores, eroding trust in the API
- **Heavier call sites**: Callers must construct and pass an argument that is immediately discarded
- **Speculative design**: Parameters are often added "just in case" for changes that never arrive

## Mechanics

The refactoring process follows these steps:

1. **Identify unused parameters**: Scan the method body to find parameters that are never referenced.
2. **Check for overrides**: Verify if the parameter is used in superclass or subclass implementations.
3. **Update callers**: Find all places where this method is called and update them to omit the unused argument.
4. **Remove the parameter**: Delete the parameter from the method signature.
5. **Handle public APIs**: For public methods, consider deprecation before complete removal.

## Before/After Example (PHP 8.3+)

### Before: Unused Parameter

```php
class UserService
{
    public function updateEmail(User $user, string $email, string $unused): void
    {
        $user->setEmail($email);
        $user->save();
    }
}

// Usage
$service->updateEmail($user, 'new@example.com', 'this is never used');
```

### After: Parameter Removed

```php
class UserService
{
    public function updateEmail(User $user, string $email): void
    {
        $user->setEmail($email);
        $user->save();
    }
}

// Usage
$service->updateEmail($user, 'new@example.com');
```

### With Named Arguments (PHP 8.0+)

```php
class ReportGenerator
{
    // Before
    public function generate(
        Report $report,
        string $format,
        string $title,
        bool $unusedFlag,
        array $options = []
    ): string {
        return $this->render($report, $format, $title, $options);
    }

    // After
    public function generate(
        Report $report,
        string $format,
        string $title,
        array $options = []
    ): string {
        return $this->render($report, $format, $title, $options);
    }
}

// Callers using named arguments adapt automatically
$generator->generate(
    report: $myReport,
    format: 'pdf',
    title: 'Monthly Report',
    options: ['pageSize' => 'A4']
);
```

## Benefits

- **Honest interface**: The signature lists exactly the data the method consumes
- **Lighter call sites**: Callers no longer fabricate throwaway arguments
- **Reduced confusion**: Future readers are not left wondering what the parameter was for
- **Simpler testing**: Fewer arguments to set up in test doubles and fixtures
- **Tighter contracts**: The relationship between caller and method is unambiguous

## When NOT to Use

Avoid this refactoring if:

- **The parameter is used in subclass/superclass implementations**: Polymorphic methods must maintain compatible signatures.
- **The method is part of a widely-used public API**: Removing parameters could break external code.
- **It's required by an interface contract**: Implementing an interface requires matching the method signature.
- **The parameter might be needed for forward compatibility**: In libraries, sometimes parameters are kept for future use.

## Related Refactorings

- **Add Parameter**: The opposite refactoring; use when a method needs additional data.
- **Rename Method**: Often combined with Remove Parameter to better reflect intent.
- **Change Method Signature**: A broader refactoring that encompasses parameter changes.
- **Extract Method**: May eliminate parameters by creating focused, single-responsibility methods.
