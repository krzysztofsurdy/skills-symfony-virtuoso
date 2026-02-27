# Incomplete Library Class

## Overview

The Incomplete Library Class smell appears when a third-party library does not provide the functionality your application requires, and you cannot modify its source to fill the gap. Developers end up scattering workarounds and duplicated logic throughout the codebase instead of extending the library cleanly. The appropriate remedy depends on scale: a handful of missing methods call for Foreign Methods, while broader gaps justify building a Local Extension (wrapper or decorator).

## Why It's a Problem

Libraries follow their own development roadmap, which may never align with your application's needs. When the functionality you require falls outside the library's scope or timeline, you face unpleasant trade-offs:
- Workaround logic gets copy-pasted wherever the library is used
- Fragile hacks accumulate and become increasingly expensive to maintain
- Code reusability and testability suffer as custom logic is scattered rather than centralized

Over time this binds your application tightly to an incomplete abstraction, driving up long-term maintenance costs.

## Signs and Symptoms

- The same supplemental logic appearing after library calls in multiple places
- Utility classes that exist solely to patch missing library methods
- Comments explaining library shortcomings or justifying workarounds
- Tests that mock or extend library classes to simulate absent features
- Developers avoiding certain library classes because they feel "incomplete"

## Before/After Examples

### Before: Workaround Duplication

```php
<?php
declare(strict_types=1);

namespace App\UserManagement;

use ThirdParty\UserRepository;

final readonly class UserService
{
    public function __construct(private UserRepository $repository)
    {
    }

    public function getUsersOrderedByName(): array
    {
        $users = $this->repository->findAll();

        // Workaround: library lacks sorting capability
        usort($users, static fn($a, $b) =>
            strcmp($a->getName(), $b->getName())
        );

        return $users;
    }

    public function getActiveUsersOrderedByName(): array
    {
        $users = $this->repository->findAllActive();

        // Duplicate workaround logic
        usort($users, static fn($a, $b) =>
            strcmp($a->getName(), $b->getName())
        );

        return $users;
    }
}
```

### After: Local Extension

```php
<?php
declare(strict_types=1);

namespace App\UserManagement;

use ThirdParty\UserRepository;

final readonly class SortableUserRepository
{
    public function __construct(private UserRepository $decorated)
    {
    }

    public function findAll(): array
    {
        return $this->sortByName($this->decorated->findAll());
    }

    public function findAllActive(): array
    {
        return $this->sortByName($this->decorated->findAllActive());
    }

    public function findById(int $id): ?object
    {
        return $this->decorated->findById($id);
    }

    private function sortByName(array $users): array
    {
        usort($users, static fn($a, $b) =>
            strcmp($a->getName(), $b->getName())
        );
        return $users;
    }
}
```

## Recommended Refactorings

### 1. Introduce Foreign Method
Use for 1-2 missing methods. Add as static helper methods in your codebase:

```php
<?php
declare(strict_types=1);

final class UserRepositoryExtensions
{
    public static function sortByName(array $users): array
    {
        usort($users, static fn($a, $b) =>
            strcmp($a->getName(), $b->getName())
        );
        return $users;
    }
}

// Usage
$sorted = UserRepositoryExtensions::sortByName($users);
```

### 2. Introduce Local Extension (Decorator Pattern)
Use for substantial missing features. Wrap the library class:

```php
<?php
declare(strict_types=1);

final readonly class EnhancedUserRepository
{
    public function __construct(
        private \ThirdParty\UserRepository $repository
    ) {
    }

    public function findAllSorted(SortOrder $order = SortOrder::NAME): array
    {
        $users = $this->repository->findAll();
        return $this->applySorting($users, $order);
    }

    private function applySorting(array $users, SortOrder $order): array
    {
        return match($order) {
            SortOrder::NAME => $this->sortByName($users),
            SortOrder::DATE => $this->sortByCreatedDate($users),
        };
    }

    private function sortByName(array $users): array
    {
        usort($users, static fn($a, $b) =>
            strcmp($a->getName(), $b->getName())
        );
        return $users;
    }

    private function sortByCreatedDate(array $users): array
    {
        usort($users, static fn($a, $b) =>
            $a->getCreatedAt() <=> $b->getCreatedAt()
        );
        return $users;
    }
}

enum SortOrder
{
    case NAME;
    case DATE;
}
```

## Exceptions

It is reasonable to tolerate an incomplete library class when:
- The missing feature genuinely falls outside the library's intended scope
- Building extensions would require deep knowledge of library internals
- You use only the library's core functionality and rarely encounter the gap
- Contributing upstream or switching libraries is impractical

Keep in mind that extending a library introduces a maintenance surface: when the library updates, your extensions may need corresponding adjustments. Weigh this ongoing cost before committing to a wrapper or decorator.

## Related Smells

- **Feature Envy**: Your code constantly reaching into another class for data it needs
- **Inappropriate Intimacy**: Extensions that require deep understanding of library internals
- **Data Clumps**: Workarounds that repeat the same parameter groups the library fails to encapsulate
- **Duplicated Code**: The natural consequence of scattering the same workaround in multiple places
