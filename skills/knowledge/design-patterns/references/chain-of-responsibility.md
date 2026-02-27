# Chain of Responsibility Pattern

## Overview

The Chain of Responsibility pattern is a behavioral design pattern that passes requests along an ordered series of handler objects until one of them takes action. Each handler inspects the incoming request independently, either processing it or forwarding it to the next link in the chain. This arrangement severs the direct connection between whoever issues a request and whoever ultimately fulfills it.

## Intent

- Channel requests through an ordered pipeline of candidate handlers
- Give each handler full autonomy to process a request or pass it along to its successor
- Eliminate hard-coded dependencies between the request originator and its eventual processor
- Allow handler chains to be constructed, reordered, or extended at runtime without code changes
- Offer a uniform dispatching mechanism that scales naturally as new request categories appear

## Problem & Solution

### Problem

When several objects are capable of servicing a request, a set of recurring design issues surfaces:

1. **Hard-Wired Dispatch**: Client code that calls specific handlers directly creates brittle, tightly coupled relationships
2. **Inflexible Ordering**: Adding, removing, or resequencing handlers requires modifications to the calling code
3. **Sprawling Conditionals**: Selecting the right handler through if-else or switch blocks produces fragile logic that resists change
4. **Runtime Resolution**: The correct handler may depend on properties of the request that are only known at execution time

### Solution

Link handler objects into a sequence where each one holds a reference to its successor. When a request enters the chain, each handler decides whether to handle it or delegate downstream. This decentralized structure makes adding or rearranging handlers straightforward and keeps the dispatch logic out of client code.

## Structure

```
Request/Task
    ↓
Handler (interface/abstract)
├── ConcreteHandlerA → ConcreteHandlerB → ConcreteHandlerC → null
│   (process/forward)   (process/forward)   (process/forward)
└── Can be configured dynamically at runtime
```

## When to Use

- Several objects might handle a request, but the specific handler is unknown until runtime
- You want to submit a request without designating a particular receiver
- Requests need to be routed dynamically based on priority levels, permissions, or other criteria
- Building approval workflows, logging pipelines, or event processing systems
- Constructing authentication or authorization layers
- Filtering or validating events through multiple stages
- Implementing tiered logging with different output targets

## Implementation

### PHP 8.3+ Example: Support Ticket Handler Chain

```php
<?php
declare(strict_types=1);

// Request object
readonly class SupportTicket {
    public function __construct(
        private string $id,
        private int $priority,
        private string $issue,
    ) {}

    public function getId(): string {
        return $this->id;
    }

    public function getPriority(): int {
        return $this->priority;
    }

    public function getIssue(): string {
        return $this->issue;
    }
}

// Abstract Handler
abstract class SupportHandler {
    protected ?SupportHandler $nextHandler = null;

    public function setNextHandler(SupportHandler $handler): self {
        $this->nextHandler = $handler;
        return $this;
    }

    abstract public function canHandle(SupportTicket $ticket): bool;

    public function handle(SupportTicket $ticket): void {
        if ($this->canHandle($ticket)) {
            $this->process($ticket);
        } elseif ($this->nextHandler !== null) {
            $this->nextHandler->handle($ticket);
        } else {
            echo "Ticket {$ticket->getId()}: No handler available\n";
        }
    }

    abstract protected function process(SupportTicket $ticket): void;
}

// Concrete Handlers
class BasicSupportHandler extends SupportHandler {
    public function canHandle(SupportTicket $ticket): bool {
        return $ticket->getPriority() <= 1;
    }

    protected function process(SupportTicket $ticket): void {
        echo "Ticket {$ticket->getId()}: Handled by Basic Support\n";
        echo "Issue: {$ticket->getIssue()}\n";
    }
}

class TechnicianHandler extends SupportHandler {
    public function canHandle(SupportTicket $ticket): bool {
        return $ticket->getPriority() === 2;
    }

    protected function process(SupportTicket $ticket): void {
        echo "Ticket {$ticket->getId()}: Handled by Technician\n";
        echo "Technical analysis: {$ticket->getIssue()}\n";
    }
}

class ManagerHandler extends SupportHandler {
    public function canHandle(SupportTicket $ticket): bool {
        return $ticket->getPriority() >= 3;
    }

    protected function process(SupportTicket $ticket): void {
        echo "Ticket {$ticket->getId()}: Handled by Manager\n";
        echo "Escalation: {$ticket->getIssue()}\n";
    }
}

// Setup and usage
$basic = new BasicSupportHandler();
$technician = new TechnicianHandler();
$manager = new ManagerHandler();

// Build the chain: basic → technician → manager
$basic->setNextHandler($technician)->setNextHandler($manager);

// Process tickets
$ticket1 = new SupportTicket('T001', 1, 'Billing inquiry');
$ticket2 = new SupportTicket('T002', 2, 'Software bug');
$ticket3 = new SupportTicket('T003', 4, 'System outage');

$basic->handle($ticket1);
$basic->handle($ticket2);
$basic->handle($ticket3);
```

### Request Logging Chain Example

```php
<?php
declare(strict_types=1);

readonly class LogEntry {
    public function __construct(
        private string $message,
        private string $level,
    ) {}

    public function getMessage(): string {
        return $this->message;
    }

    public function getLevel(): string {
        return $this->level;
    }
}

abstract class Logger {
    protected ?Logger $nextLogger = null;

    public function setNext(Logger $logger): Logger {
        $this->nextLogger = $logger;
        return $logger;
    }

    public function log(LogEntry $entry): void {
        if ($this->shouldHandle($entry)) {
            $this->writeLog($entry);
        }

        if ($this->nextLogger !== null) {
            $this->nextLogger->log($entry);
        }
    }

    abstract protected function shouldHandle(LogEntry $entry): bool;
    abstract protected function writeLog(LogEntry $entry): void;
}

class ConsoleLogger extends Logger {
    protected function shouldHandle(LogEntry $entry): bool {
        return in_array($entry->getLevel(), ['DEBUG', 'INFO']);
    }

    protected function writeLog(LogEntry $entry): void {
        echo "[CONSOLE] {$entry->getLevel()}: {$entry->getMessage()}\n";
    }
}

class FileLogger extends Logger {
    protected function shouldHandle(LogEntry $entry): bool {
        return in_array($entry->getLevel(), ['WARNING', 'ERROR']);
    }

    protected function writeLog(LogEntry $entry): void {
        echo "[FILE] {$entry->getLevel()}: {$entry->getMessage()}\n";
    }
}

class EmailLogger extends Logger {
    protected function shouldHandle(LogEntry $entry): bool {
        return $entry->getLevel() === 'CRITICAL';
    }

    protected function writeLog(LogEntry $entry): void {
        echo "[EMAIL] {$entry->getLevel()}: {$entry->getMessage()}\n";
    }
}

// Usage
$console = new ConsoleLogger();
$file = new FileLogger();
$email = new EmailLogger();

$console->setNext($file)->setNext($email);

$console->log(new LogEntry('Application started', 'INFO'));
$console->log(new LogEntry('Low disk space', 'WARNING'));
$console->log(new LogEntry('Database connection failed', 'CRITICAL'));
```

## Real-World Analogies

**Emergency Room Triage**: A patient entering an ER is assessed by a triage nurse who routes minor complaints to a general practitioner, moderate injuries to a specialist, and life-threatening cases to the trauma team. Each tier handles what falls within its competence and escalates the rest.

**Expense Approval Workflow**: A purchase request lands on a team lead's desk first. If the amount exceeds their signing authority, the request advances to a department head, then possibly to the finance director. Each approver acts within their limit or passes the request upward.

**DOM Event Bubbling**: A click on a deeply nested HTML element propagates upward through its ancestor nodes. Each node in the hierarchy may intercept and handle the event or let it continue rising to the parent.

## Pros and Cons

### Advantages
- **Sender Ignorance**: The originator of a request has no visibility into which handler ultimately services it
- **Runtime Reconfiguration**: Chains can be assembled, extended, or reshuffled without modifying source code
- **Single-Purpose Handlers**: Each handler owns exactly one concern, keeping logic focused
- **Non-Intrusive Extension**: New handlers plug into the chain without affecting existing ones
- **Open/Closed Compliance**: The system evolves through addition, not modification

### Disadvantages
- **Silent Drops**: A request may pass through every handler without any of them acting on it
- **Cumulative Latency**: Each link in the chain adds a processing hop, which compounds in long pipelines
- **Difficult Tracing**: Identifying which handler actually processed a request requires logging or debugging
- **Hidden Pipeline Shape**: The full processing sequence is only visible by inspecting how the chain was wired together
- **Memory Overhead**: Every handler stores a reference to its successor, adding a small per-node cost

## Relations with Other Patterns

- **Command**: Requests can be packaged as command objects before entering the chain, enabling queuing and logging alongside routing
- **Observer**: Both facilitate event-driven architectures, but Observer broadcasts to all subscribers while Chain of Responsibility routes to one handler
- **Strategy**: Strategy picks an algorithm upfront at configuration time; Chain of Responsibility discovers the right handler dynamically per request
- **Composite**: Often combined when requests must propagate through tree-shaped hierarchies
- **Decorator**: Shares the linked-wrapper structure, but Decorator layers additional behavior while Chain of Responsibility selects a handler

## Examples in Other Languages

### Java

Before and after comparison showing how the Chain of Responsibility pattern eliminates explicit handler selection logic:

```java
// After: handlers are linked in a chain and delegate automatically
class Handler {
    private final static Random RANDOM = new Random();
    private static int nextID = 1;
    private int id = nextID++;
    private Handler nextInChain;

    public void add(Handler next) {
        if (nextInChain == null) {
            nextInChain = next;
        } else {
            nextInChain.add(next);
        }
    }

    public void wrapAround(Handler root) {
        if (nextInChain == null) {
            nextInChain = root;
        } else {
            nextInChain.wrapAround(root);
        }
    }

    public void execute(int num) {
        if (RANDOM.nextInt(4) != 0) {
            System.out.println("   " + id + "-busy  ");
            nextInChain.execute(num);
        } else {
            System.out.println(id + "-handled-" + num);
        }
    }
}

public class ChainDemo {
    public static void main(String[] args) {
        Handler rootChain = new Handler();
        rootChain.add(new Handler());
        rootChain.add(new Handler());
        rootChain.add(new Handler());
        rootChain.wrapAround(rootChain);
        for (int i = 1; i < 6; i++) {
            System.out.println("Operation #" + i + ":");
            rootChain.execute(i);
            System.out.println();
        }
    }
}
```

### Python

```python
import abc


class Handler(metaclass=abc.ABCMeta):
    """
    Define an interface for handling requests.
    Implement the successor link.
    """

    def __init__(self, successor=None):
        self._successor = successor

    @abc.abstractmethod
    def handle_request(self):
        pass


class ConcreteHandler1(Handler):
    """
    Handle request, otherwise forward it to the successor.
    """

    def handle_request(self):
        if True:  # if can_handle:
            pass
        elif self._successor is not None:
            self._successor.handle_request()


class ConcreteHandler2(Handler):
    """
    Handle request, otherwise forward it to the successor.
    """

    def handle_request(self):
        if False:  # if can_handle:
            pass
        elif self._successor is not None:
            self._successor.handle_request()


def main():
    concrete_handler_1 = ConcreteHandler1()
    concrete_handler_2 = ConcreteHandler2(concrete_handler_1)
    concrete_handler_2.handle_request()


if __name__ == "__main__":
    main()
```

### C++

```cpp
#include <iostream>
#include <vector>
#include <ctime>
using namespace std;

class Base
{
    Base *next;
  public:
    Base()
    {
        next = 0;
    }
    void setNext(Base *n)
    {
        next = n;
    }
    void add(Base *n)
    {
        if (next)
          next->add(n);
        else
          next = n;
    }
    virtual void handle(int i)
    {
        next->handle(i);
    }
};

class Handler1: public Base
{
  public:
     void handle(int i)
    {
        if (rand() % 3)
        {
            cout << "H1 passed " << i << "  ";
            Base::handle(i);
        }
        else
          cout << "H1 handled " << i << "  ";
    }
};

class Handler2: public Base
{
  public:
     void handle(int i)
    {
        if (rand() % 3)
        {
            cout << "H2 passed " << i << "  ";
            Base::handle(i);
        }
        else
          cout << "H2 handled " << i << "  ";
    }
};

class Handler3: public Base
{
  public:
     void handle(int i)
    {
        if (rand() % 3)
        {
            cout << "H3 passed " << i << "  ";
            Base::handle(i);
        }
        else
          cout << "H3 handled " << i << "  ";
    }
};

int main()
{
  srand(time(0));
  Handler1 root;
  Handler2 two;
  Handler3 thr;
  root.add(&two);
  root.add(&thr);
  thr.setNext(&root);
  for (int i = 1; i < 10; i++)
  {
    root.handle(i);
    cout << '\n';
  }
}
```
