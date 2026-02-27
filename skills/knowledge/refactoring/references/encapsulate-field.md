## Overview

Encapsulate Field replaces direct access to a public class field with getter and setter methods. This draws a boundary between the internal representation and the external contract, allowing you to add validation, change storage mechanisms, or introduce computed properties without affecting any calling code.

## Motivation

**Why wrap fields in accessor methods:**

1. **Guard External Access**: Prevent callers from assigning invalid or inconsistent values
2. **Conceal Storage Details**: How data is stored becomes an internal decision
3. **Enforce Constraints**: Setter methods can reject values that violate business rules
4. **Support Evolution**: Swap a stored field for a computed property without breaking clients
5. **Clean Boundaries**: Public methods form a stable contract; private fields can change freely
6. **Enable Side Effects**: Add logging, caching, or event notifications later without a signature change
7. **Stronger Typing**: Method signatures enforce types more explicitly than raw field access

## Mechanics

1. Locate public or protected fields that external code reads or writes
2. Create a getter method that returns the field value
3. Create a setter method that assigns the value (with optional validation)
4. Find every external read and replace it with a getter call
5. Find every external write and replace it with a setter call
6. Change the field visibility to private
7. Add validation or constraints inside the setter

## Before/After PHP 8.3+ Code

### Before: Public Field Access

```php
<?php

declare(strict_types=1);

class Product
{
    public string $name;
    public float $price;
    public int $stock;

    public function __construct(string $name, float $price, int $stock)
    {
        $this->name = $name;
        $this->price = $price;
        $this->stock = $stock;
    }
}

// Client code accessing fields directly
$product = new Product('Laptop', 999.99, 10);
$product->price = -50; // Invalid: negative price allowed!
$product->stock = -5; // Invalid: negative stock allowed!
$product->name = ''; // Invalid: empty name allowed!

// Reading fields directly
echo "Product: " . $product->name;
echo "Price: " . $product->price;
echo "Stock: " . $product->stock;

// Risky modifications
$product->price *= 0.5; // Direct manipulation
```

### After: Encapsulated Access

```php
<?php

declare(strict_types=1);

class Product
{
    private string $name;
    private float $price;
    private int $stock;

    public function __construct(string $name, float $price, int $stock)
    {
        $this->setName($name);
        $this->setPrice($price);
        $this->setStock($stock);
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function setName(string $name): void
    {
        if (empty(trim($name))) {
            throw new InvalidArgumentException('Product name cannot be empty');
        }
        $this->name = $name;
    }

    public function getPrice(): float
    {
        return $this->price;
    }

    public function setPrice(float $price): void
    {
        if ($price < 0) {
            throw new InvalidArgumentException('Price cannot be negative');
        }
        $this->price = $price;
    }

    public function getStock(): int
    {
        return $this->stock;
    }

    public function setStock(int $stock): void
    {
        if ($stock < 0) {
            throw new InvalidArgumentException('Stock cannot be negative');
        }
        $this->stock = $stock;
    }

    public function applyDiscount(float $percentage): void
    {
        if ($percentage < 0 || $percentage > 100) {
            throw new InvalidArgumentException('Discount must be 0-100%');
        }
        // Setter ensures validation
        $this->setPrice($this->price * (1 - $percentage / 100));
    }
}

// Client code using methods
$product = new Product('Laptop', 999.99, 10);
$product->setPrice(-50); // InvalidArgumentException thrown!
$product->setStock(-5); // InvalidArgumentException thrown!
$product->setName(''); // InvalidArgumentException thrown!

// Reading through getters
echo "Product: " . $product->getName();
echo "Price: " . $product->getPrice();
echo "Stock: " . $product->getStock();

// Safe modifications through methods
$product->applyDiscount(10); // Controlled, validated change
```

## Benefits

- **Input Validation**: Setters reject values that break business rules
- **Hidden Internals**: Callers interact with a stable method-based contract
- **Seamless Migration**: Switch from a stored field to a derived computation without touching clients
- **Computed Properties**: A getter can calculate its return value on the fly
- **Observable State Changes**: Setters can trigger logging, events, or cache invalidation
- **Strict Types**: Method signatures give callers and IDEs precise type information
- **Self-Documenting**: Method names and signatures describe what the class offers
- **Room to Grow**: New behavior can be layered into accessors without altering the public contract

## When NOT to Use

- **Immutable Value Objects**: Final readonly classes may not need setters at all
- **Simple DTOs in Private Layers**: Internal data carriers with no validation needs may not benefit
- **Internal Utility Classes**: Private helpers with no outside consumers
- **Already Encapsulated**: If callers already go through methods, the work is done
- **Minimal Payoff**: Wrapping a field that will never need validation or change adds ceremony for little gain

## Related Refactorings

- **Self Encapsulate Field**: Applies the same idea to internal access within the class itself
- **Hide Delegate**: Wraps another object's fields behind the delegating class
- **Replace Data Value with Object**: Promotes a primitive field into a dedicated class
- **Extract Class**: Moves related fields into their own class
- **Introduce Parameter Object**: Groups related fields into a single parameter object
- **Remove Setter**: Makes fields read-only by dropping the setter

## Examples in Other Languages

### Java

**Before:**
```java
class Person {
  public String name;
}
```

**After:**
```java
class Person {
  private String name;

  public String getName() {
    return name;
  }
  public void setName(String arg) {
    name = arg;
  }
}
```

### C#

**Before:**
```csharp
class Person
{
  public string name;
}
```

**After:**
```csharp
class Person
{
  private string name;

  public string Name
  {
    get { return name; }
    set { name = value; }
  }
}
```

### TypeScript

**Before:**
```typescript
class Person {
  name: string;
}
```

**After:**
```typescript
class Person {
  private _name: string;

  get name() {
    return this._name;
  }
  setName(arg: string): void {
    this._name = arg;
  }
}
```
