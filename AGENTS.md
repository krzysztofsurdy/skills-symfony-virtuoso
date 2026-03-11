# Agents

@CONTRIBUTING.md

Agents are sub-agents -- standalone markdown files that define a specialized role, its allowed tools, and its system prompt. Each agent file contains YAML frontmatter for configuration and a markdown body that serves as the agent's system prompt.

Where **skills** provide reference knowledge (patterns, checklists, component docs), **agents** are the actors that use that knowledge to perform work. A skill is a book on the shelf; an agent is the specialist who reads the book and applies it. Delegate to an agent when a task is well-scoped enough that a focused sub-agent will do it better than the orchestrating model switching context mid-conversation.

## Architecture

Agents follow a two-tier model:

**Specialist agents** handle a single, repeatable task type. They are typically read-only, stateless, and operate on whatever the caller hands them. Think of them as focused tools: investigate this, review that, scan for smells.

**Role agents** embody a team position. They carry a broader mandate, preload relevant skills, and some maintain persistent project-level memory across sessions. They own a domain ("the what", "the how", "the when") rather than a single task.

| Aspect | Specialist | Role |
|--------|-----------|------|
| Scope | Single task type | Entire domain of responsibility |
| Skills | 1-4 relevant knowledge skills | Role skill + relevant knowledge skills |
| Memory | Stateless | Some use persistent memory for cross-session context |
| File modification | Mostly read-only (except Doc Writer and Implementer) | Dev roles (Backend, Frontend) write code; others are read-only |
| Isolation | Implementer uses worktree; others run in-place | Backend Dev and Frontend Dev use worktree; others run in-place |

## Specialist Agents

| Agent | Tools | Isolation | Purpose |
|-------|-------|-----------|---------|
| [Investigator](agents/investigator.md) | File reading, code search, shell | -- | Deep codebase exploration, dependency mapping |
| [Implementer](agents/implementer.md) | All | worktree | TDD red-green-refactor execution |
| [Reviewer](agents/reviewer.md) | File reading, code search, shell | -- | Structured code review (SOLID, OWASP, smells) |
| [Refactor Scout](agents/refactor-scout.md) | File reading, code search, shell | -- | Code smell scanning, complexity hotspots |
| [Dependency Auditor](agents/dependency-auditor.md) | Shell, file reading, code search | -- | CVE checks, outdated packages, license audit |
| [Doc Writer](agents/doc-writer.md) | File reading, code search, shell, file editing | -- | Changelogs, API docs, migration guides |
| [Migration Planner](agents/migration-planner.md) | File reading, code search, shell | -- | Migration safety analysis, rollback paths |
| [Test Gap Analyzer](agents/test-gap-analyzer.md) | File reading, code search, shell | -- | Missing test coverage, untested edge cases |

**Investigator** -- Delegate when you need to understand how something works before changing it. It traces code paths, maps dependencies, and returns structured findings with file paths and line numbers.

**Implementer** -- Delegate when you have a concrete plan and want strict TDD execution. It works in an isolated worktree, runs red-green-refactor cycles, and commits after each change. Hand it a plan, not a vague request.

**Reviewer** -- Delegate after implementation to get a structured code review. It checks correctness, SOLID compliance, OWASP security concerns, performance patterns (N+1 queries), code smells, and test coverage. Returns prioritized findings with severity levels.

**Refactor Scout** -- Delegate for codebase health assessments. It scans directories for bloaters, coupling issues, dispensables, and change preventers, then maps each smell to a named refactoring technique with effort estimates.

**Dependency Auditor** -- Delegate for dependency health checks. It runs `composer audit`, `npm audit`, or equivalent commands, checks for outdated packages, and flags license incompatibilities.

**Doc Writer** -- Delegate after completing features or changes that need documentation. It reads code changes and produces changelogs, API endpoint docs, or migration guides. The only specialist with file editing permissions, but it only touches documentation files.

**Migration Planner** -- Delegate before running database migrations. It classifies operations by risk (safe, caution, dangerous), evaluates zero-downtime compatibility, verifies rollback paths, and produces a step-by-step execution plan with pre-checks.

**Test Gap Analyzer** -- Delegate after implementation to find what the tests missed. It maps source files to their test files, inventories public interfaces, and identifies missing unit tests, edge cases, integration tests, and error path tests by priority.

## Role Agents

| Agent | Tools | Memory | Skills | Purpose |
|-------|-------|--------|--------|---------|
| [Product Manager](agents/product-manager.md) | File reading, code search, shell | project | product-manager | Requirements, PRDs, prioritization |
| [Architect](agents/architect.md) | File reading, code search, shell | project | architect | System design, ADRs, trade-offs |
| [Backend Dev](agents/backend-dev.md) | File reading, file editing, shell, code search | -- | backend-dev | API implementation, data models, TDD |
| [Frontend Dev](agents/frontend-dev.md) | File reading, file editing, shell, code search | -- | frontend-dev | UI components, accessibility, state |
| [QA Engineer](agents/qa-engineer.md) | File reading, code search, shell | project | qa-engineer | Test plans, bug reports, release sign-off |
| [Project Manager](agents/project-manager.md) | File reading, code search, shell | project | project-manager | PRINCE2 stages, risk, progress tracking |
| [Scrum Master](agents/scrum-master.md) | File reading, code search, shell | -- | scrum | Sprint planning, goals, retrospectives |

**Product Manager** -- Owns the "what" and "why." Delegate when requirements are unclear, user stories need writing, or scope needs prioritizing. Uses MoSCoW/RICE frameworks, writes PRDs with Given/When/Then acceptance criteria, and classifies priorities as P0/P1/P2. Does not write code or make architecture decisions.

**Architect** -- Owns the "how." Delegate for system design, component boundaries, API contracts, and technology choices. Writes ADRs (Context, Decision, Alternatives, Consequences) and evaluates trade-offs between quality attributes. Does not implement code.

**Backend Dev** -- Owns backend production code. Delegate when you need API endpoints, data models, or services built with strict TDD. Works in a worktree. Follows red-green-refactor and commits after each logical change. Escalates to the Architect when API contracts cannot satisfy requirements.

**Frontend Dev** -- Owns the user-facing interface. Delegate for UI component implementation, API integration, accessibility compliance, and responsive layouts. Works in a worktree. Builds leaf components first, composes upward, and tests rendering, interaction, and integration paths.

**QA Engineer** -- Owns quality assurance. Delegate after feature completion for test plans, test case design, exploratory testing, and release sign-off. Classifies bugs by severity (P0-P3) and blocks releases when critical bugs are open. Does not fix bugs.

**Project Manager** -- Owns the "when" and "how much." Delegate for stage plans, risk registers, highlight reports, and tolerance management. Operates on PRINCE2 principles: manage by stages, manage by exception, continued business justification. Escalates via exception reports when tolerances are forecast to breach.

**Scrum Master** -- Facilitates Scrum events. Delegate for sprint planning, sprint goal crafting, retrospective facilitation, and impediment resolution. Coaches rather than directs. Uses the FOCUS criteria for sprint goals and tracks action items from retrospectives.

## Agent Chaining Patterns

Common multi-agent workflows where the output of one agent feeds the next:

### Investigation Flow

```
Investigator -> Architect -> Implementer -> Reviewer
```

Start with the Investigator to map the relevant code area. Hand findings to the Architect for design decisions. Pass the design to the Implementer for TDD execution. Finish with the Reviewer for quality checks.

### Feature Flow

```
Product Manager -> Architect -> Backend Dev / Frontend Dev -> QA Engineer
```

The Product Manager defines requirements and acceptance criteria. The Architect translates them into component designs and API contracts. Dev agents implement in worktrees. The QA Engineer writes test plans against the original acceptance criteria and signs off.

### Review Flow

```
Refactor Scout -> Reviewer -> Implementer
```

The Refactor Scout scans for code smells and structural issues. The Reviewer validates the scout's findings against the actual code context. The Implementer applies the recommended refactorings with TDD.

### Pre-Migration Flow

```
Migration Planner -> Reviewer -> Implementer
```

The Migration Planner analyzes migration files and produces a risk-assessed execution plan. The Reviewer checks that application code is compatible with both old and new schemas. The Implementer applies any required code changes.

### Coverage Improvement Flow

```
Test Gap Analyzer -> Implementer -> Reviewer
```

The Test Gap Analyzer identifies missing test cases by priority. The Implementer writes the missing tests using TDD cycles. The Reviewer verifies the new tests are meaningful and correctly structured.

## Conventions

### Tool Permission Philosophy

Agents follow least privilege. Read-only agents get only file reading, code search, and shell tools. File editing permissions are granted only to agents that must modify files: the Implementer, Doc Writer, Backend Dev, and Frontend Dev. Shell access is universally available for running tests, audit commands, and git operations.

### Worktree Isolation

Agents that create or modify source code operate in isolated git worktrees. This prevents half-finished changes from polluting the main working tree and lets the orchestrator review changes before merging. Currently three agents use worktree isolation: Implementer, Backend Dev, and Frontend Dev.

### Memory Usage

Role agents that need cross-session context (Product Manager, Architect, QA Engineer, Project Manager) use persistent project-level memory. This allows them to accumulate project knowledge -- requirements decisions, architectural context, risk registers -- across multiple conversations. Specialist agents are stateless by design.

### Skill Preloading

Both role and specialist agents preload relevant skills. The skill name matches the `name` field in the skill's SKILL.md, not the directory path. Role agents preload their own role skill plus relevant knowledge skills (e.g., Backend Dev loads `backend-dev`, `design-patterns`, `clean-architecture`, `testing`, `api-design`). Specialist agents preload the 1-4 knowledge skills most relevant to their task (e.g., Reviewer loads `refactoring`, `solid`, `security`, `performance`).
