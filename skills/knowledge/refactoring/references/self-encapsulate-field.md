## Overview

Self Encapsulate Field is a foundational refactoring that replaces direct field access within a class with getter and setter methods. This introduces an intermediary layer between the field and all code that reads or writes it, allowing the class to evolve its internal representation without disrupting external consumers.

Instead of referencing a field directly (e.g., `$this->name`), you route all access through accessor methods (`getName()` and `setName()`). This becomes especially valuable in larger systems where fields eventually need validation, change notification, or deferred initialization.

## Motivation

**Why encapsulate fields:**

1. **Flexibility**: Storage format or computation logic can change without breaking callers
2. **Validation**: Setters can enforce constraints and business rules at the point of assignment
3. **Side effects**: Field changes can trigger observers, dirty flags, or audit logging
4. **Lazy initialization**: Getters can delay expensive object creation until first access
5. **Single Responsibility**: Separates the concern of data access from data storage
6. **Gradual evolution**: Provides a path to introduce computed properties or derived values over time

## Mechanics

The refactoring proceeds as follows:

1. Write a getter method that returns the field value
2. Write a setter method that assigns a new value to the field
3. Locate every direct read of the field throughout the class
4. Replace each direct read with a call to the getter
5. Replace each direct write with a call to the setter
6. Restrict the field's visibility to private or protected
7. Add validation or side-effect logic inside the setter as needed

## Before/After PHP 8.3+ Code

### Before: Direct Field Access

```php
class User
{
    public string $email;
    public int $age;
    public string $status = 'active';

    public function __construct(string $email, int $age)
    {
        $this->email = $email;
        $this->age = $age;
    }

    public function processUser(): void
    {
        // Direct access to fields throughout the class
        if ($this->age < 18) {
            $this->status = 'minor';
        }

        echo "User: " . $this->email . " is " . $this->status;
    }
}

// Client code with direct access
$user = new User('john@example.com', 15);
$user->email = 'newemail@example.com'; // Direct assignment
$user->age = 25; // Direct assignment
echo $user->status; // Direct read
```

### After: Encapsulated Access

```php
class User
{
    private string $email;
    private int $age;
    private string $status = 'active';

    public function __construct(string $email, int $age)
    {
        $this->setEmail($email);
        $this->setAge($age);
    }

    public function getEmail(): string
    {
        return $this->email;
    }

    public function setEmail(string $email): void
    {
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email format');
        }
        $this->email = $email;
    }

    public function getAge(): int
    {
        return $this->age;
    }

    public function setAge(int $age): void
    {
        if ($age < 0 || $age > 150) {
            throw new InvalidArgumentException('Age must be between 0 and 150');
        }
        $this->age = $age;
        // Trigger validation logic
        $this->updateStatus();
    }

    public function getStatus(): string
    {
        return $this->status;
    }

    protected function setStatus(string $status): void
    {
        $this->status = $status;
    }

    private function updateStatus(): void
    {
        if ($this->age < 18) {
            $this->setStatus('minor');
        } else {
            $this->setStatus('adult');
        }
    }

    public function processUser(): void
    {
        if ($this->getAge() < 18) {
            $this->setStatus('minor');
        }

        echo "User: " . $this->getEmail() . " is " . $this->getStatus();
    }
}

// Client code with encapsulated access
$user = new User('john@example.com', 15);
$user->setEmail('newemail@example.com'); // Through setter
$user->setAge(25); // Through setter with validation
echo $user->getStatus(); // Through getter
```

## Benefits

- **Validation and constraints**: Business rules are enforced at the moment of assignment
- **Centralized modification**: All changes to a field flow through a single point, simplifying debugging
- **Lazy initialization**: Expensive computations can be deferred until the getter is first called
- **Observable state**: Observers or event handlers can be triggered on field changes
- **Computed properties**: Fields can be transparently replaced by derived values
- **Backward compatibility**: Internal representation can change without altering the public API
- **Debugging support**: Breakpoints in getters and setters make it easy to trace access
- **Polymorphic behavior**: Subclasses can override accessors to customize field behavior

## When NOT to Use

- **Value Objects**: Immutable value classes with final fields may not benefit from encapsulation
- **DTOs**: Simple data transfer objects might not justify the overhead of getters and setters
- **High-frequency access**: Accessor methods add negligible overhead, but in extreme cases it may be a consideration
- **Wholesale public fields**: If the entire codebase relies on public fields, a massive encapsulation effort may not be justified
- **Already encapsulated**: If getters and setters are already in place, further application yields diminishing returns

## Related Refactorings

- **Replace Data Value with Object**: Upgrade a primitive field to a dedicated object with richer behavior
- **Remove Setter**: Eliminate setters for fields that should be immutable or write-once
- **Replace Temp with Query**: Extract field initialization logic into query methods
- **Hide Delegate**: Encapsulate internal dependencies behind the class's own interface
- **Introduce Parameter Object**: Bundle related fields into a single parameter object

## Examples in Other Languages

### Java

**Before:**
```java
class Range {
  private int low, high;
  boolean includes(int arg) {
    return arg >= low && arg <= high;
  }
}
```

**After:**
```java
class Range {
  private int low, high;
  boolean includes(int arg) {
    return arg >= getLow() && arg <= getHigh();
  }
  int getLow() {
    return low;
  }
  int getHigh() {
    return high;
  }
}
```

### C#

**Before:**
```csharp
class Range
{
  private int low, high;

  bool Includes(int arg)
  {
    return arg >= low && arg <= high;
  }
}
```

**After:**
```csharp
class Range
{
  private int low, high;

  int Low {
    get { return low; }
  }
  int High {
    get { return high; }
  }

  bool Includes(int arg)
  {
    return arg >= Low && arg <= High;
  }
}
```

### TypeScript

**Before:**
```typescript
class Range {
  private low: number
  private high: number;
  includes(arg: number): boolean {
    return arg >= low && arg <= high;
  }
}
```

**After:**
```typescript
class Range {
  private low: number
  private high: number;
  includes(arg: number): boolean {
    return arg >= getLow() && arg <= getHigh();
  }
  getLow(): number {
    return low;
  }
  getHigh(): number {
    return high;
  }
}
```
