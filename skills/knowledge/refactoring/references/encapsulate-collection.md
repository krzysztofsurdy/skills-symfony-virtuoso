## Overview

Encapsulate Collection replaces direct public access to a collection field with a controlled API of add, remove, and query methods. The class becomes the gatekeeper for all modifications to the collection, preventing external code from bypassing validation or corrupting invariants.

## Motivation

Collections are inherently mutable. When exposed through a public field or a getter that returns the live reference, any caller can insert, delete, or replace elements without the owning class knowing. This creates several problems:

- The class loses control over its own state
- Business rules and validation logic can be bypassed
- Unexpected mutations are hard to debug
- The code becomes fragile and resistant to change
- Responsibilities leak from the owning class to its callers

Wrapping the collection behind dedicated methods gives the class the authority to validate inputs, enforce constraints, and react to changes.

## Mechanics

1. **Provide targeted mutation methods**: Create `addX()` and `removeX()` methods instead of exposing the raw collection
2. **Return defensive copies**: The getter should hand back a copy or read-only snapshot so callers cannot mutate the original
3. **Restrict field visibility**: Make the collection field private
4. **Migrate all callers**: Replace every direct collection manipulation in client code with calls to the new methods
5. **Add bulk operations if needed**: For performance-sensitive paths, provide methods that accept multiple items at once

## Before/After PHP 8.3+ Code

### Before: Direct Collection Access

```php
class Person
{
    public array $hobbies = [];
}

// Client code - problematic
$person = new Person();
$person->hobbies[] = 'reading';
$person->hobbies[] = 'gaming';
unset($person->hobbies[0]); // Direct modification!
```

### After: Encapsulated Collection

```php
class Person
{
    private array $hobbies = [];

    public function addHobby(string $hobby): void
    {
        if (empty(trim($hobby))) {
            throw new InvalidArgumentException('Hobby cannot be empty');
        }
        if (!in_array($hobby, $this->hobbies, true)) {
            $this->hobbies[] = $hobby;
        }
    }

    public function removeHobby(string $hobby): void
    {
        $key = array_search($hobby, $this->hobbies, true);
        if ($key !== false) {
            unset($this->hobbies[$key]);
            $this->hobbies = array_values($this->hobbies); // Re-index
        }
    }

    public function getHobbies(): array
    {
        return [...$this->hobbies]; // Return copy, not reference
    }

    public function hasHobby(string $hobby): bool
    {
        return in_array($hobby, $this->hobbies, true);
    }
}

// Client code - controlled and safe
$person = new Person();
$person->addHobby('reading');
$person->addHobby('gaming');
$person->removeHobby('reading');
$hobbies = $person->getHobbies();
```

### Advanced: Using Collections Class (PHP 8.3+)

```php
#[Attribute]
readonly class Hobby
{
    public function __construct(public string $name) {}
}

class PersonWithCollection
{
    /** @var array<Hobby> */
    private array $hobbies = [];

    public function addHobby(Hobby $hobby): self
    {
        if (!in_array($hobby, $this->hobbies, true)) {
            $this->hobbies[] = $hobby;
        }
        return $this;
    }

    public function removeHobby(Hobby $hobby): self
    {
        $this->hobbies = array_filter(
            $this->hobbies,
            fn(Hobby $h) => $h !== $hobby
        );
        return $this;
    }

    /** @return array<Hobby> */
    public function getHobbies(): array
    {
        return [...$this->hobbies];
    }

    public function countHobbies(): int
    {
        return count($this->hobbies);
    }
}

// Usage
$person = new PersonWithCollection();
$person->addHobby(new Hobby('reading'))
       ->addHobby(new Hobby('gaming'));

foreach ($person->getHobbies() as $hobby) {
    echo $hobby->name;
}
```

## Benefits

- **Full State Control**: The owning class decides what goes into the collection and under what conditions
- **Built-in Validation**: Business rules are enforced every time the collection changes
- **Localized Changes**: All collection management logic lives in one place
- **Observable Mutations**: Modifications flow through methods that can log, trigger events, or audit changes
- **Safe Reads**: Returning copies prevents callers from accidentally altering internal state
- **Preserved Invariants**: The class can guarantee consistency at all times
- **Intentional API**: The set of allowed operations is explicit and discoverable

## When NOT to Use

- **Hot paths with large collections**: Copying a large array on every read may hurt performance; consider lazy or immutable collection types instead
- **Pure data holders**: If the class has no validation logic and serves only as a data container, full encapsulation may be unnecessary overhead
- **Immutable value objects**: Readonly classes constructed via named constructors may not need mutation methods
- **Internal-only classes**: Private implementation details with no external consumers may not warrant the ceremony
- **Specialized collection libraries**: When using a library with its own encapsulation conventions, follow those instead

## Related Refactorings

- **Extract Class**: When collection management becomes complex enough to justify its own class
- **Replace Temp with Query**: Avoid caching collection computations in temporary variables
- **Move Method**: Relocate collection-related logic from callers into the collection owner
- **Introduce Parameter Object**: Bundle related collection-like parameters into a dedicated type
- **Replace Array with Object**: Promote untyped arrays to typed objects for stronger guarantees
