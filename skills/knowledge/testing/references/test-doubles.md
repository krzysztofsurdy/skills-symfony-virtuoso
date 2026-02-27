# Test Doubles

## Overview

A test double is any object that stands in for a real dependency during testing. The term comes from the film industry's "stunt double" — a substitute that looks like the real thing but serves a specific purpose. Understanding the distinctions between double types helps you choose the right tool and avoid over-mocking.

## Types of Test Doubles

### Dummy

An object passed to satisfy a parameter list but never actually used by the code under test.

**When to use:** A constructor or method requires a parameter that is irrelevant to the behavior you are testing.

**Example scenario:** Testing an order's total calculation. The method signature requires a logger, but logging is not involved in the calculation. Pass a dummy logger.

### Stub

An object that returns pre-configured answers to method calls. No verification of how it was called.

**When to use:** You need to control indirect inputs to the system under test. The dependency provides data that influences the behavior you are testing.

**Example scenario:** Testing a pricing service that reads exchange rates from an external API. Stub the API client to return a fixed exchange rate so the test is deterministic and fast.

### Spy

A stub that also records information about how it was called — which methods, with what arguments, how many times.

**When to use:** You need to verify that the system under test interacted with a dependency in a specific way, but you want to make the assertion *after* the act phase (not inline).

**Example scenario:** Testing that a registration service sends a welcome email. Use a spy on the email sender, then assert after the act that `send` was called once with the correct recipient.

### Mock

An object pre-programmed with expectations about how it will be called. Verification happens on the mock itself, typically before or during the act phase.

**When to use:** When you want strict verification of interactions and want the test to fail immediately if the expected interaction does not occur.

**Example scenario:** Testing that a payment processor is called exactly once with the correct amount. The mock is configured with this expectation up front.

**Mock vs Spy:** Mocks verify expectations eagerly (the mock itself fails). Spies record passively and let you verify later with assertions. In practice, many testing frameworks blur this distinction.

### Fake

A lightweight, working implementation of a dependency that takes shortcuts unsuitable for production.

**When to use:** When a real dependency is too slow or complex for tests, but you need realistic behavior — not just canned answers.

**Example scenario:**
- In-memory repository instead of a real database
- Fake file system that operates on a dictionary in memory
- Fake email sender that collects messages into a list

Fakes require maintenance — they must be kept in sync with the real implementation's contract.

## When NOT to Use Test Doubles

- **Pure functions and value objects** — just call them directly; no doubles needed
- **Simple collaborators that are fast and deterministic** — using the real thing gives higher confidence
- **To avoid writing integration tests entirely** — doubles verify contracts, not wiring

## The "Don't Mock What You Don't Own" Principle

Avoid creating test doubles for third-party APIs, libraries, or framework internals. Instead:

1. Create your own abstraction (port/interface) that wraps the third-party dependency
2. Mock your own abstraction in tests
3. Write a thin adapter that implements your abstraction using the real third-party code
4. Test the adapter with integration tests

**Why:** Third-party APIs change without notice. If you mock them directly, your tests will keep passing even when the real behavior has changed — giving false confidence.

## Mock at Architectural Boundaries

The most effective place to use test doubles is at architectural boundaries — the "ports" in a ports-and-adapters architecture:

- **Database access** — stub/fake the repository interface
- **External HTTP services** — stub the HTTP client abstraction
- **Message queues** — fake the message bus
- **File system** — fake the file storage interface
- **Clock/time** — stub a clock interface for deterministic time

Avoid mocking between internal collaborators (service A mocking service B within the same bounded context). This couples tests to the internal structure and makes refactoring expensive.

## Mockist vs Classicist Debate

| Approach | Uses Doubles For | Trade-off |
|---|---|---|
| **Classicist** | Only external dependencies and slow resources | Higher confidence, more complex setup |
| **Mockist** | All collaborators except the unit under test | Focused tests, but coupled to implementation |

Neither approach is universally better. Many teams adopt a hybrid:

- Use real objects for fast, deterministic collaborators (value objects, domain services)
- Use doubles for slow, non-deterministic, or external dependencies (databases, APIs, clocks)

## Common Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Mocking everything | Tests verify wiring, not behavior; break on any refactor | Use real collaborators where practical |
| Mocking return values of mocks | Deep mock chains signal a design problem (Law of Demeter) | Simplify the interface; inject what you need directly |
| Not verifying fake correctness | Fake drifts from real implementation; tests pass but production fails | Write contract tests that run against both fake and real implementations |
| Verifying too many interactions | Tests become a mirror of the implementation | Verify only the interactions that matter to the behavior |
