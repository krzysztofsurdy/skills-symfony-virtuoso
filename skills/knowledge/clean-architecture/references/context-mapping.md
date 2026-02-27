# Context Mapping

Strategic DDD patterns for defining boundaries between parts of a system and managing how those parts interact. Context mapping is about making integration decisions explicit.

## Bounded Context

A Bounded Context is a boundary within which a particular domain model is defined, consistent, and meaningful. It is the fundamental unit of ownership in a complex system.

**Key principles:**
- Each Bounded Context has its own **Ubiquitous Language** — the same word can (and often does) mean different things in different contexts
- A context should be owned by one team
- Each context has its own data storage — shared databases between contexts is an antipattern
- The model inside a context is internally consistent but makes no guarantees about matching models in other contexts

**Identifying boundaries:**
- Listen for vocabulary conflicts — when "Order" means different things to Sales and Fulfillment, that signals two contexts
- Align with business capabilities (billing, shipping, inventory) rather than technical layers (web, service, data)
- Follow team structure — Conway's Law suggests system boundaries reflect organizational boundaries
- Look for natural seams where consistency requirements change (immediate vs. eventual)

**Signs a context should be split:**
- The model has become so large that no single person can understand it
- Different parts of the model change at different rates or for different reasons
- The team struggles to find names that satisfy all stakeholders
- Conflicting business rules apply to what appears to be the same concept

**Signs contexts should merge:**
- Two contexts share most of their model and always change together
- The overhead of integration exceeds the benefit of separation
- A single team owns both and finds the boundary more painful than helpful

## Context Map Patterns

A Context Map documents the relationships and integration strategies between Bounded Contexts. Each relationship has a pattern that describes the power dynamic and coupling approach.

### Shared Kernel

Two contexts share a small, explicitly defined subset of the domain model. Both teams must agree on changes to the shared portion.

- **Use when:** Two teams are closely collaborating and a small overlap is natural
- **Risk:** The shared portion can grow uncontrollably; requires discipline and joint governance
- **Guidance:** Keep the shared kernel as small as possible; consider splitting it into its own module with explicit versioning

### Customer-Supplier

The upstream context (supplier) provides data or services that the downstream context (customer) depends on. The downstream team can negotiate requirements with the upstream team.

- **Use when:** There is a clear producer-consumer relationship and the upstream team is willing to accommodate downstream needs
- **Dynamic:** The upstream team plans work considering downstream impact; the downstream team provides requirements and timelines

### Conformist

The downstream context conforms entirely to the upstream context's model. There is no negotiation — the downstream team adopts whatever the upstream provides.

- **Use when:** The upstream team has no motivation or capacity to support downstream needs (e.g., a large external platform)
- **Trade-off:** Simpler integration but the downstream model is constrained by upstream decisions
- **Mitigation:** If conforming becomes painful, introduce an Anti-Corruption Layer

### Anti-Corruption Layer (ACL)

A translation layer that the downstream context builds to protect its model from the upstream context's model. The ACL converts between external and internal representations.

- **Use when:** Integrating with legacy systems, external vendors, or contexts with a model that would pollute the downstream domain
- **Structure:** Adapter (handles protocol/transport) + Translator (maps between models) + Facade (simplifies the external interface)
- **Placement:** Infrastructure layer of the downstream context, implementing a port defined by the application or domain layer

### Open Host Service

The upstream context exposes a well-defined protocol (API, event schema) designed to serve multiple consumers. The protocol is a deliberate, maintained interface.

- **Use when:** Multiple downstream contexts need access to the same upstream capabilities
- **Guidance:** Version the protocol; changes must be backward-compatible or clearly communicated
- **Combines well with:** Published Language

### Published Language

A shared, well-documented data format used for communication between contexts. Both sides agree on the schema independently of their internal models.

- **Examples:** Standard event schemas, canonical data formats, industry-standard exchange formats
- **Use when:** Multiple contexts need a common interchange format that neither context's internal model should dictate

## Integration Patterns Between Contexts

### Event-Based Integration (Preferred)

Contexts communicate by publishing and consuming domain events. Each context decides independently how to react.

- **Advantages:** Loose coupling, temporal decoupling, independent deployability
- **Challenges:** Eventual consistency, event ordering, idempotency
- **Guidance:** Events should be part of the Published Language; version them carefully

### Synchronous API Calls

One context calls another's API directly. Simpler but creates runtime coupling.

- **Advantages:** Immediate consistency, simpler mental model
- **Challenges:** Cascading failures, latency coupling, availability dependency
- **Guidance:** Use circuit breakers and timeouts; consider whether eventual consistency would suffice

### Shared Database (Antipattern)

Multiple contexts read from and write to the same database tables. This creates tight coupling and eliminates the benefits of bounded contexts.

- **Problems:** Schema changes affect all contexts simultaneously; no clear ownership of data; implicit coupling through data rather than explicit contracts
- **Migration path:** Assign table ownership to one context; other contexts integrate through events or APIs; eventually separate the storage
