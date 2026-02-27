# Parallel Inheritance Hierarchies

## Overview

Parallel Inheritance Hierarchies emerge when two or more class hierarchies mirror each other's structure. Adding a subclass to one hierarchy compels you to add a corresponding subclass to the other. What starts as a minor inconvenience compounds as the hierarchies grow, producing systematic duplication and fragile coupling between structures that should be independent.

## Why It's a Problem

Every new class added to one hierarchy demands a matching class in the other, doubling the maintenance effort. The implicit dependencies between the two structures are easy to overlook and hard to keep synchronized. As the hierarchies expand, the risk of inconsistencies rises, and the cognitive overhead of understanding the full picture grows substantially. Refactoring one hierarchy without accidentally breaking the other becomes increasingly difficult.

## Signs and Symptoms

- Adding a subclass in one hierarchy always requires creating a matching subclass elsewhere
- Two hierarchies grow in tandem with nearly identical structures
- Abstract base classes in separate hierarchies have mirrored method signatures
- Structural changes in one hierarchy force corresponding adjustments in the other
- Strong coupling between hierarchies that are nominally independent

## Before/After Examples

**Before: Parallel Hierarchies**

```php
<?php
declare(strict_types=1);

abstract class ReportGenerator
{
    abstract public function generate(): string;
}

class PDFReportGenerator extends ReportGenerator
{
    public function generate(): string
    {
        return "Generating PDF...";
    }
}

class HTMLReportGenerator extends ReportGenerator
{
    public function generate(): string
    {
        return "Generating HTML...";
    }
}

// Parallel hierarchy - mirrors ReportGenerator
abstract class ReportExporter
{
    abstract public function export(): string;
}

class PDFReportExporter extends ReportExporter
{
    public function export(): string
    {
        return "Exporting to PDF...";
    }
}

class HTMLReportExporter extends ReportExporter
{
    public function export(): string
    {
        return "Exporting to HTML...";
    }
}
```

**After: Using Composition**

```php
<?php
declare(strict_types=1);

readonly class Report
{
    public function __construct(
        private ReportFormatter $formatter,
    ) {}

    public function generate(): string
    {
        return $this->formatter->format();
    }

    public function export(): string
    {
        return $this->formatter->export();
    }
}

interface ReportFormatter
{
    public function format(): string;
    public function export(): string;
}

readonly class PDFFormatter implements ReportFormatter
{
    public function format(): string
    {
        return "Generating PDF...";
    }

    public function export(): string
    {
        return "Exporting to PDF...";
    }
}

readonly class HTMLFormatter implements ReportFormatter
{
    public function format(): string
    {
        return "Generating HTML...";
    }

    public function export(): string
    {
        return "Exporting to HTML...";
    }
}
```

## Recommended Refactorings

**1. Create References (Composition)**
Replace inheritance relationships with composition by injecting instances of one hierarchy into the other. This decouples the structures and eliminates the need to maintain parallel subclasses.

**2. Move Methods and Fields**
Extract common behavior into shared classes that both hierarchies can use. Use Move Method and Move Field techniques to consolidate functionality.

**3. Use Strategy Pattern**
Replace parallel hierarchies with a single class that delegates to strategy implementations. This simplifies the class structure significantly.

**4. Apply Decorator Pattern**
When parallel hierarchies represent different concerns (e.g., export format vs. report type), use decorators to compose behaviors independently.

## Exceptions

- **True Parallel Requirements**: If two domains genuinely require parallel structures with different evolution paths, maintaining them may be acceptable.
- **Legacy Systems**: Complete refactoring may be impractical; consider gradual migration using adapters.
- **Performance-Critical Code**: In rare cases, explicit hierarchies may outperform composition; benchmark before refactoring.

## Related Smells

- **Duplicate Code**: Parallel hierarchies are a structural form of systematic duplication spread across multiple classes.
- **Feature Envy**: Methods in one hierarchy that constantly reference the other hierarchy's data suggest the logic belongs elsewhere.
- **God Class**: Parallel hierarchies sometimes result from incorrectly splitting a single domain concept.
- **Middle Man**: Consolidating via composition can introduce pointless delegation if not designed thoughtfully.

Note: Small parallel hierarchies may not cause noticeable pain, but the cost grows proportionally with each new subclass pair. If attempting to consolidate the hierarchies produces messier code than the duplication itself, it may be more pragmatic to leave them as-is.
