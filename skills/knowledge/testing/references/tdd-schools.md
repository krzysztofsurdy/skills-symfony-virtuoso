# TDD Schools: London vs Chicago

## Overview

Test-Driven Development has two major schools of thought that differ in how they approach test isolation, verification style, and design direction. Neither is "correct" — each excels in different contexts. Understanding both gives you the flexibility to choose the right approach for the problem at hand.

## Chicago School (Classical / Detroit)

The original TDD approach, associated with Kent Beck's "Test-Driven Development: By Example."

### Core Principles

- **State-based verification**: assert on the output or resulting state, not on which methods were called
- **Inside-out direction**: start with the innermost domain logic, then build outward toward application and infrastructure layers
- **Real collaborators**: use actual objects wherever possible; avoid mocks unless dealing with external/slow dependencies
- **Refactoring-friendly**: since tests verify outcomes rather than interactions, internal restructuring rarely breaks tests

### Workflow

1. Identify a small piece of domain behavior
2. Write a test that asserts the expected state after invoking that behavior
3. Implement the simplest code to pass the test
4. Refactor — rearrange internals freely since tests verify outputs, not call sequences
5. Move outward to the next layer, using the already-tested domain objects as real collaborators

### Strengths

- Tests are resilient to refactoring — changing how code works does not break tests as long as what it does remains the same
- Tests serve as behavior documentation — reading the test tells you what the system does
- Higher confidence — real objects exercise actual code paths
- Simpler test code — less mock setup, fewer expectations to maintain

### Weaknesses

- Setup can become complex when the object graph is deep — creating the unit under test may require constructing many real collaborators
- When a deep dependency breaks, multiple tests fail — harder to pinpoint the root cause immediately
- Less guidance on interface design — the interfaces emerge after the fact rather than being driven by the test

## London School (Mockist / Interaction-Based)

Associated with Steve Freeman and Nat Pryce's "Growing Object-Oriented Software, Guided by Tests" (GOOS).

### Core Principles

- **Interaction-based verification**: assert that the unit under test called its collaborators with the correct arguments
- **Outside-in direction**: start with an acceptance test at the outermost layer, then drive inward, discovering interfaces as you go
- **Mocked collaborators**: every direct dependency of the unit under test is replaced with a mock or stub
- **Interface-driven design**: because you must define collaborator interfaces before implementing them, TDD drives the API design

### Workflow

1. Write a failing acceptance test for a user-facing feature
2. Starting from the outermost layer (controller, handler), write a unit test that mocks the next layer's interface
3. Define the interface that the mock represents — this is the "discovered" design
4. Implement the outer layer to pass the test
5. Move inward: the mocked interface becomes the next unit to test, with its own mocked collaborators
6. Repeat until you reach the innermost layer, then implement the real infrastructure

### Strengths

- Each unit test is focused — tests exactly one class with all collaborators mocked, making failures precise
- Drives interface design — forces you to think about collaborator contracts before implementing them
- Natural fit for outside-in development — you build the system from the user's perspective
- Encourages small, focused classes with clear roles

### Weaknesses

- Tests are coupled to implementation — renaming a method, extracting a class, or changing call order breaks tests even if behavior is unchanged
- Refactoring is expensive — internal restructuring often requires rewriting tests
- Risk of "mock hell" — excessive mock setup makes tests harder to read than the production code
- False positives — tests pass because mocks behave as programmed, even if the real integration would fail

## Side-by-Side Comparison

| Aspect | Chicago | London |
|---|---|---|
| Verification style | State/output | Interactions/calls |
| Design direction | Inside-out | Outside-in |
| Collaborators in test | Real objects | Mocks and stubs |
| Refactoring cost | Low | High |
| Failure localization | Broad (many tests may fail) | Precise (one test fails) |
| Interface discovery | After implementation | During test writing |
| Setup complexity | Can be high (deep object graphs) | Moderate (mock configuration) |
| Best for | Domain logic, calculations, transformations | Coordination logic, workflow orchestration |

## When to Use Which

### Prefer Chicago When

- The code is logic-heavy: calculations, validations, transformations, state machines
- You want maximum freedom to refactor internals
- Collaborators are fast, deterministic, and easy to construct
- You are working on domain/core layers with few external dependencies

### Prefer London When

- The code primarily coordinates between collaborators (orchestration, delegation)
- You want to discover and refine interfaces during the design process
- You are building from the outside in, starting with user-facing behavior
- The collaborator graph is complex and constructing real objects would be impractical

## Hybrid Approach

Most experienced practitioners blend both schools:

- **Domain layer**: Chicago style — real objects, state-based assertions, maximum refactoring safety
- **Application/service layer**: London style — mock infrastructure ports, verify coordination logic
- **Infrastructure adapters**: integration tests with real external systems — neither school, just verify the wiring

This pragmatic hybrid gives you:
- Resilient domain tests that survive refactoring
- Focused service tests that drive interface design
- Integration tests that verify real-world behavior at the boundaries

## Key Takeaway

The choice is not ideological — it is contextual. Match the approach to the nature of the code you are testing. Logic-heavy code benefits from classical state-based testing. Coordination-heavy code benefits from interaction-based testing. A healthy test suite typically contains both.
