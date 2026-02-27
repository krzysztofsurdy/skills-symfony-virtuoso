# Add Parameter Refactoring

## Overview

Add Parameter solves the problem of a method that needs additional data to perform its job correctly. Instead of having the method dig into class internals or rely on global state, you surface the missing information as an explicit parameter. This produces methods with transparent inputs that are straightforward to understand and verify.

## Motivation

Apply this technique when:

- A method needs data that its current signature does not provide
- The required information changes from call to call, making it a poor fit for a class property
- You want tests to control method inputs directly without manipulating object state
- You need to break an implicit dependency on internal fields
- Different callers possess context-specific values that should flow into the method

## Mechanics

1. **Create the new method** with the additional parameter in its signature
2. **Delegate from the old method** by calling the new version with a reasonable default value
3. **Update callers progressively** so each one passes the parameter explicitly
4. **Remove the original method** once every caller has been migrated, or keep it as a shorthand overload

Points to keep in mind:
- Apply signature changes methodically to avoid breaking existing call sites
- Default parameter values ease the transition by preserving backward compatibility
- If the parameter feels unnatural, it may signal a more fundamental design issue

## Before/After - PHP 8.3+ Code

**BEFORE:**

```php
class NotificationService {
    private string $channel = 'email';

    public function send(User $user, string $message): void {
        // Channel is hardcoded to instance variable
        $this->sendViaChannel($user, $message, $this->channel);
    }

    private function sendViaChannel(
        User $user,
        string $message,
        string $channel
    ): void {
        match($channel) {
            'email' => $this->sendEmail($user->email, $message),
            'sms' => $this->sendSms($user->phone, $message),
            'push' => $this->sendPush($user->id, $message),
        };
    }
}
```

**AFTER:**

```php
class NotificationService {
    public function send(
        User $user,
        string $message,
        string $channel = 'email'
    ): void {
        // Channel is now explicit parameter with default
        match($channel) {
            'email' => $this->sendEmail($user->email, $message),
            'sms' => $this->sendSms($user->phone, $message),
            'push' => $this->sendPush($user->id, $message),
        };
    }
}

// Usage becomes more flexible:
$service = new NotificationService();
$service->send($user, 'Hello');              // Uses default 'email'
$service->send($user, 'Alert', 'sms');      // Uses 'sms' channel
$service->send($user, 'Urgent', 'push');    // Uses 'push' channel
```

## Benefits

- **Flexibility**: The method handles a broader set of scenarios without internal changes
- **Testability**: Passing different values as arguments enables thorough, isolated tests
- **Reduced Coupling**: The method no longer pulls values from mutable internal state
- **Reusability**: The same logic serves multiple callers with varying data
- **Transparent Interface**: The signature communicates every piece of data the method depends on
- **Named Arguments**: PHP 8.0+ named parameters make call sites self-documenting

## When NOT to Use

- **Parameter Overload**: Methods with more than 3-4 parameters signal a need for structural redesign
- **Repeated Growth**: Continuously appending parameters suggests bundling them into a Parameter Object or DTO
- **Related Values**: When the new parameter naturally groups with existing ones, wrap them in a value object
- **Stable Public Contracts**: Altering published interfaces disrupts downstream consumers
- **Hidden Abstraction Gap**: The need to pass data may reveal a missing class or responsibility

Alternatives to consider:
- Promote the data to a class property if it logically belongs to the object
- Combine related parameters into a DTO or value object
- Carve out a separate class for the associated functionality
- Inject service-level dependencies through the constructor

## Related Refactorings

- **Remove Parameter**: The inverse operation, used when a parameter becomes unnecessary
- **Introduce Parameter Object**: Groups multiple related parameters into a single object
- **Extract Method**: Often applied in tandem to sharpen method focus
- **Replace Method with Method Object**: Handles complex methods that accumulate many parameters
- **Move Method**: Shifts logic to a class that already holds the needed data
