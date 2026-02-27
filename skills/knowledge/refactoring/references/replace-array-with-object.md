## Overview

Replace Array with Object converts arrays that hold a fixed set of semantically distinct values into dedicated objects with named properties. Arrays are built for homogeneous collections; when each index carries a specific meaning, an object with typed properties communicates that structure far more clearly and enables tooling support, validation, and encapsulation.

## Motivation

Using positional array indices to represent structured data creates a number of hazards:

- **No type enforcement**: Any index can hold any value, defeating static analysis
- **Opaque access**: `$person[0]` reveals nothing about what it contains; `$person->name` is self-explanatory
- **Fragile ordering**: Inserting or reordering elements breaks every access site
- **Missing IDE support**: Editors cannot autocomplete or rename array keys the way they can with properties
- **No behavioral home**: Arrays cannot host methods, so related logic scatters elsewhere

An object with named, typed properties makes the structure explicit and provides a natural home for associated behavior.

## Mechanics

1. Create a new class or value object with named properties matching array indices
2. Add a constructor to initialize the object from array data (if needed)
3. Add properties and methods for accessing and manipulating data
4. Replace all array creation calls with object instantiation
5. Replace all array access (`$arr[0]`) with property access (`$obj->field`)
6. Remove temporary array usage patterns
7. Add type hints and validation as appropriate

## Before/After

### Before: Using Arrays

```php
// Poor: Magic indices, unclear structure
function getUserInfo($userId): array {
    $user = fetchUserData($userId);
    return [$user['name'], $user['email'], $user['age']];
}

// Unclear what each index means
$info = getUserInfo(42);
echo $info[0]; // Is this the name? No type safety
echo $info[1]; // Email? Confusing

// Brittle: reordering breaks code
function displayUser($data): void {
    echo "Name: " . $data[0];
    echo "Email: " . $data[1];
    echo "Age: " . $data[2];
}
```

### After: Using Objects (PHP 8.3+)

```php
// Good: Self-documenting, type-safe
final readonly class UserInfo {
    public function __construct(
        public string $name,
        public string $email,
        public int $age,
    ) {}

    public function isAdult(): bool {
        return $this->age >= 18;
    }

    public function getDisplayName(): string {
        return ucfirst($this->name);
    }
}

function getUserInfo($userId): UserInfo {
    $user = fetchUserData($userId);
    return new UserInfo(
        name: $user['name'],
        email: $user['email'],
        age: $user['age'],
    );
}

// Clear, type-safe, refactorable
$info = getUserInfo(42);
echo $info->name; // IDE autocomplete, type checking
echo $info->email;
echo $info->age;

function displayUser(UserInfo $data): void {
    echo "Name: " . $data->getDisplayName();
    echo "Email: " . $data->email;
    if ($data->isAdult()) {
        echo "Age: " . $data->age;
    }
}
```

### Complex Example: Coordinate Array

```php
// Before: Numeric indices
$point = [10, 20, 'red'];
function movePoint(array $point, int $dx, int $dy): array {
    return [$point[0] + $dx, $point[1] + $dy, $point[2]];
}

// After: Semantic object
final readonly class Point {
    public function __construct(
        public int $x,
        public int $y,
        public string $color,
    ) {}

    public function move(int $dx, int $dy): self {
        return new self(
            x: $this->x + $dx,
            y: $this->y + $dy,
            color: $this->color,
        );
    }

    public function distance(Point $other): float {
        return sqrt(
            pow($this->x - $other->x, 2) +
            pow($this->y - $other->y, 2)
        );
    }
}

$point = new Point(x: 10, y: 20, color: 'red');
$moved = $point->move(5, 5);
$dist = $point->distance($moved);
```

## Benefits

- **Compile-time safety**: Type hints catch misassignments before the code runs
- **Readable by default**: Named properties make every access self-documenting
- **Full tooling support**: Autocomplete, rename refactoring, and static analysis all work out of the box
- **Built-in validation**: Constructors can enforce invariants at creation time
- **Room to grow**: Methods can be added without restructuring callers
- **Easier test setup**: Objects with clear constructors are simpler to build in test fixtures
- **Resilient to change**: Adding a property with a default does not break existing call sites

## When NOT to Use

- **Variable-Length Collections**: Use arrays or `Collection` objects for lists of unknown size
- **Homogeneous Data**: Arrays are appropriate for collections of similar items
- **Pure Data Transport**: Very simple DTOs might be overkill (though typed properties are still recommended)
- **Legacy Code**: Gradual refactoring may be necessary; do this incrementally
- **Performance-Critical Hot Paths**: Profile first; modern PHP is fast enough for most use cases

## Related Refactorings

- **Extract Class**: Move related properties into their own class
- **Introduce Parameter Object**: Group method parameters into an object
- **Replace Magic Numbers**: Use named constants alongside object properties
- **Extract Value Object**: Create immutable objects that represent domain concepts
- **Introduce Builder**: Use builders for complex object construction

## Examples in Other Languages

### Java

**Before:**
```java
String[] row = new String[2];
row[0] = "Liverpool";
row[1] = "15";
```

**After:**
```java
Performance row = new Performance();
row.setName("Liverpool");
row.setWins("15");
```

### C#

**Before:**
```csharp
string[] row = new string[2];
row[0] = "Liverpool";
row[1] = "15";
```

**After:**
```csharp
Performance row = new Performance();
row.SetName("Liverpool");
row.SetWins("15");
```

### Python

**Before:**
```python
row = [None * 2]
row[0] = "Liverpool"
row[1] = "15"
```

**After:**
```python
row = Performance()
row.setName("Liverpool")
row.setWins("15")
```

### TypeScript

**Before:**
```typescript
let row = new Array(2);
row[0] = "Liverpool";
row[1] = "15";
```

**After:**
```typescript
let row = new Performance();
row.setName("Liverpool");
row.setWins("15");
```
