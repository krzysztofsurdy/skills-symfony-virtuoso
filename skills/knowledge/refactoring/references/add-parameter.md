# Add Parameter Refactoring

## Overview

Add Parameter addresses situations where a method lacks the information it needs to carry out its work. Rather than having the method reach into class state or global context, you provide the missing data through an explicit parameter. This leads to methods that are self-contained, easier to reason about, and simpler to test.

## Motivation

Apply this technique when:

- A method requires data it currently cannot access through its existing signature
- The needed data is contextual or varies per call, making it unsuitable as a class field
- You want to improve testability by making inputs explicit
- You aim to decouple the method from internal object state
- Callers have context-specific information that the method should receive directly

## Mechanics

1. **Introduce the new method** with the added parameter in its signature
2. **Bridge from the old method** by having it call the new version with a sensible default
3. **Migrate callers** that need the new capability to supply the parameter directly
4. **Retire the original method** once all callers have been updated, or retain it as a convenience overload

Points to keep in mind:
- Proceed carefully with signature changes to avoid breaking existing call sites
- Default parameter values help preserve backward compatibility during migration
- If the parameter seems forced, it may indicate a deeper structural problem

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

- **Adaptability**: The method can serve a wider range of use cases without modification
- **Testability**: Supplying different parameter values makes comprehensive testing straightforward
- **Looser Coupling**: The method no longer depends on mutable object state for its inputs
- **Reuse**: Identical logic can be driven with varying data from different callers
- **Explicit Dependencies**: The method signature documents exactly what data is required
- **Named Arguments**: PHP 8.0+ named parameters make call sites highly readable

## When NOT to Use

- **Too Many Parameters**: Methods with more than 3-4 parameters suggest the design needs rethinking
- **Recurring Additions**: Continuously adding parameters points toward a Parameter Object or DTO
- **Closely Related Data**: When the new parameter belongs alongside existing ones, group them into a value object
- **Stable Public APIs**: Changing published interfaces breaks consumers
- **Symptom of Missing Abstraction**: Needing to pass data may indicate a class is missing a responsibility

Alternatives to consider:
- Store the data as a class property if it belongs to the object
- Bundle related parameters into a DTO or value object
- Extract a dedicated class for the related functionality
- Use constructor injection for service-level dependencies

## Related Refactorings

- **Remove Parameter**: The reverse operation, applied when a parameter is no longer needed
- **Introduce Parameter Object**: Consolidates multiple related parameters into one object
- **Extract Method**: Frequently applied alongside to sharpen method responsibilities
- **Replace Method with Method Object**: Suitable for complex methods accumulating many parameters
- **Move Method**: Relocates logic to a class that already has access to the required data
