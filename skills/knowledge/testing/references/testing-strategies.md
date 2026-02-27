# Testing Strategies by Architecture Layer

## Overview

Different layers of an application have different responsibilities, dependencies, and failure modes. An effective test strategy matches the test type to the layer, pushing verification to the lowest level that provides confidence while using higher-level tests sparingly for integration assurance.

## Domain / Business Logic

The core of your application — rules, calculations, state machines, validations.

**Test type:** Unit tests
**Approach:**
- State-based verification — call a method, assert on the result or resulting state
- No I/O, no databases, no network — pure logic
- Use real collaborators (value objects, domain services) — avoid mocks
- Test edge cases thoroughly: boundary values, empty inputs, overflow, invalid combinations

**What to assert:**
- Return values and output state
- Exceptions and error conditions
- Invariants that must always hold

**Goal:** Fast, comprehensive coverage of all business rules. This layer should have the most tests.

## Application Services / Use Cases

Orchestration layer that coordinates domain objects and infrastructure.

**Test type:** Unit tests with test doubles for infrastructure ports
**Approach:**
- Stub or fake infrastructure dependencies (repositories, message buses, external service clients)
- Use real domain objects — do not mock the domain layer
- Verify that the service orchestrates correctly: calls the right ports with the right data

**What to assert:**
- Correct domain objects are created/modified
- Infrastructure ports are called with expected arguments
- The right events or commands are dispatched
- Error scenarios are handled (not found, conflicts, authorization failures)

**Goal:** Verify coordination logic without slow infrastructure.

## Repositories / Data Access

The layer that persists and retrieves data from databases, file systems, or external stores.

**Test type:** Integration tests with a real database
**Approach:**
- Use test containers, in-memory databases, or dedicated test database instances
- Each test starts with a clean state (truncate tables or use transactions that roll back)
- Test actual queries, mappings, and constraints — not mock behavior

**What to assert:**
- Data is persisted correctly and can be retrieved
- Query filters, sorting, and pagination work as expected
- Database constraints (unique, foreign key) are enforced
- Concurrent access scenarios if relevant

**Goal:** Catch query bugs, mapping errors, and schema mismatches that unit tests cannot detect.

## API Endpoints / Controllers

The layer that accepts external requests and returns responses.

**Test type:** Integration tests and contract tests
**Approach:**
- Send real HTTP requests to the application (or use an in-process test client)
- Test the full request/response cycle: serialization, validation, routing, status codes, headers
- Use contract tests (consumer-driven or provider-driven) for APIs consumed by other services

**What to assert:**
- Correct HTTP status codes for success and error scenarios
- Response body structure and content
- Input validation and error messages
- Authentication and authorization enforcement
- Content negotiation and headers

**Goal:** Verify the API contract is correct and stable. Catch serialization, routing, and validation bugs.

## UI Components

Interactive elements that users see and interact with.

**Test type:** Component tests and interaction tests
**Approach:**
- Render components in isolation with controlled props/inputs
- Simulate user interactions (clicks, typing, navigation)
- Assert on the rendered output and triggered events
- Avoid asserting on CSS classes or DOM structure — assert on visible text and behavior

**What to assert:**
- Correct rendering for different states (loading, error, empty, populated)
- User interaction triggers the expected behavior
- Accessibility attributes are present
- Conditional display logic works

**Goal:** Verify component behavior without a full browser or backend.

## Cross-Cutting / End-to-End

Complete user journeys through the entire system.

**Test type:** End-to-end tests
**Approach:**
- Automate critical business workflows (sign up, purchase, core CRUD flows)
- Run against a fully deployed environment (or realistic local stack)
- Keep the number small — 5-15 critical paths, not hundreds
- Use stable selectors and explicit waits to reduce flakiness

**What to assert:**
- The user can complete the journey from start to finish
- Data flows correctly across all layers
- Integrations with real external services work (or use sandboxed test accounts)

**Goal:** Final confidence check that the system works as a whole. Not the place to test edge cases.

## Test Data Management

Consistent, reliable test data is critical across all layers.

### Builders

Programmatic construction of test objects with sensible defaults and fluent overrides:
- Each test overrides only the fields relevant to its scenario
- Defaults cover all required fields so tests stay focused

### Factories

Pre-defined templates for common test scenarios:
- "valid order," "expired subscription," "admin user"
- Reusable across tests, but each test gets its own instance (no sharing)

### Fixtures

Static data loaded before tests run:
- Useful for reference data (countries, currencies, roles)
- Dangerous for mutable data — leads to coupling between tests
- Prefer builders/factories for test-specific data

## Continuous Testing

Testing is only valuable if it runs consistently and provides fast feedback.

### Pre-Commit / Pre-Push Hooks
- Run unit tests and linting before code reaches the repository
- Must complete in under 30 seconds to avoid friction

### CI Pipeline
- Run the full test suite on every push and pull request
- Separate fast tests (unit) from slow tests (integration, e2e) into parallel stages
- Fail fast: run the fastest tests first

### Test Parallelization
- Unit tests should be parallelizable by default (no shared state)
- Integration tests may need isolated databases or namespaced resources
- E2E tests are hardest to parallelize — use independent user accounts or data sets

### Monitoring Test Health
- Track test suite duration over time — alert on regressions
- Track flaky test rates — quarantine and fix flaky tests immediately
- Track coverage trends — not as a target, but as a signal of untested areas
