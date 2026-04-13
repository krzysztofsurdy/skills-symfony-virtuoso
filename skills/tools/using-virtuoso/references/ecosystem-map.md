# Ecosystem Map

Full inventory of skills, agents, and plugins in the code-virtuoso marketplace. Use this as a lookup when you need to confirm what exists before recommending it.

## Knowledge Skills

Reference material. Auto-loaded by context. Not user-invocable as slash commands.

| Skill | Covers |
|---|---|
| `design-patterns` | 26 Gang of Four patterns with multi-language examples |
| `refactoring` | Refactoring techniques and the code smells that trigger them |
| `solid` | Single Responsibility, Open-Closed, Liskov, Interface Segregation, Dependency Inversion |
| `debugging` | Reproduce-investigate-hypothesize-fix-prevent workflow and post-mortems |
| `clean-architecture` | Clean / Hexagonal Architecture and Domain-Driven Design fundamentals |
| `testing` | Testing pyramid, TDD schools, test doubles, strategies |
| `api-design` | REST and GraphQL design, evolution, versioning |
| `security` | OWASP Top 10, authentication, authorization, secure coding |
| `scrum` | Sprint goals, events, roles, facilitation templates |
| `performance` | Profiling, caching, database optimization, N+1 prevention |
| `microservices` | Saga, CQRS, event sourcing, circuit breakers, service mesh |
| `git-workflow` | Branching strategies, commit conventions, PR patterns, release management |
| `cicd` | Pipeline design, deployment strategies, environment promotion |
| `accessibility` | WCAG compliance, ARIA patterns, keyboard navigation, a11y testing |
| `database-design` | Schema modeling, indexing, migration patterns, temporal data |
| `verification-before-completion` | Evidence-based completion discipline, tiered definition of done |
| `dispatching-parallel-agents` | Fan-out/fan-in patterns, subagent briefing, context isolation |
| `subagent-driven-development` | One-fresh-agent-per-task, two-stage review, structured hand-offs |

## Tool Skills

Interactive generators and advisors. User-invocable as slash commands.

| Skill | Does what |
|---|---|
| `agentic-rules-writer` | Generates tailored rules/instruction files for any AI coding agent |
| `ticket-writer` | Writes tickets of the right type (story, bug, subtask, epic, initiative) |
| `agent-creator` | Designs a well-scoped sub-agent definition with frontmatter and system prompt |
| `plugin-creator` | Scaffolds a complete plugin manifest and directory structure |
| `brainstorming` | Turns a vague idea into a written spec with hard approval gate |
| `using-virtuoso` | This skill. Guided tour and discovery advisor for the ecosystem |

## Playbook Skills

Step-by-step operational procedures. User-invocable.

| Skill | Covers |
|---|---|
| `php-upgrade` | PHP version upgrade process with Rector and PHPCompatibility |
| `composer-dependencies` | Safe dependency update strategies, audits, automation |
| `finishing-branch` | End-to-end branch finishing: verify, review, integrate, clean up |

## Role Skills

Team role definitions. Loaded by matching role agents.

| Skill | Role |
|---|---|
| `product-manager` | Requirements, PRDs, prioritization |
| `architect` | System design, ADRs, component boundaries |
| `backend-dev` | Backend implementation, APIs, data models |
| `frontend-dev` | UI implementation, components, state |
| `qa-engineer` | Test planning, test design, release sign-off |
| `project-manager` | PRINCE2-based delivery, risk, progress |
| `scrum-master` | Sprint facilitation, coaching, impediments |

## Framework Skills

Framework-specific component references and upgrade guides.

| Skill | Covers |
|---|---|
| `symfony-components` | 38 Symfony components for PHP 8.3+ and Symfony 7.x |
| `symfony-upgrade` | Deprecation-first upgrade guide for Symfony minor and major versions |
| `django-components` | 33 Django components for Python 3.10+ and Django 6.0 |
| `langchain-components` | 17 LangChain ecosystem references including LangGraph and Deep Agents |

## Specialist Agents

Single-task, mostly stateless, read-only except for `implementer` and `doc-writer`.

| Agent | Role |
|---|---|
| `investigator` | Deep codebase exploration, dependency mapping |
| `implementer` | TDD red-green-refactor execution (writes code; runs in a worktree) |
| `reviewer` | Structured code review against SOLID, OWASP, code smells |
| `refactor-scout` | Code smell scanning, complexity hotspots |
| `dependency-auditor` | CVE checks, outdated packages, license audit |
| `doc-writer` | Changelogs, API docs, migration guides (writes docs) |
| `migration-planner` | Migration safety analysis, rollback paths |
| `test-gap-analyzer` | Missing coverage, untested edge cases |

## Role Agents

Domain ownership. Dev roles run in worktrees. Several carry project-level memory.

| Agent | Owns |
|---|---|
| `product-manager` | Requirements and prioritization |
| `architect` | System design and trade-offs |
| `backend-dev` | Backend production code |
| `frontend-dev` | User-facing interface |
| `qa-engineer` | Quality assurance and release sign-off |
| `project-manager` | Delivery, risk, progress tracking |
| `scrum-master` | Sprint facilitation |

## Plugin Bundles

Installable units in `.claude-plugin/marketplace.json`.

| Plugin | Contains |
|---|---|
| `knowledge-virtuoso` | All knowledge skills |
| `playbooks-virtuoso` | All playbook skills |
| `symfony-virtuoso` | All Symfony framework skills |
| `django-virtuoso` | All Django framework skills |
| `langchain-virtuoso` | All LangChain framework skills |
| `agents-virtuoso` | All 15 agents plus all role skills |
| `role-{name}` | One role skill + its matching role agent (seven plugins) |
| `agent-{name}` | One specialist agent (eight plugins) |
| `tool-{name}` | One tool skill (one plugin per tool) |

Versioning follows semantic rules: patch for content edits, minor for additions, major for restructuring or breaking changes.
