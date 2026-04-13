# Plugin Tiers

How to pick what to install. Plugins in `.claude-plugin/marketplace.json` are grouped into three tiers. Install granularity matches use case.

## Tier 1: Individual Plugins

One focused unit per plugin. Install exactly what you need, nothing more.

| Pattern | Example | Contains |
|---|---|---|
| `role-{name}` | `role-architect`, `role-backend-dev`, `role-qa-engineer` | One role skill + its matching role agent |
| `agent-{name}` | `agent-investigator`, `agent-reviewer`, `agent-migration-planner` | One specialist agent |
| `tool-{name}` | `tool-agentic-rules-writer`, `tool-ticket-writer`, `tool-plugin-creator` | One tool skill |

**When to pick individual plugins:**

- Solo developer with narrow, specific need
- Adding one capability to an existing setup
- Experimenting before committing to a bundle

**Trade-off:** You manage updates per plugin. Drift across plugins is possible.

---

## Tier 2: Category Bundles

All skills in a category, grouped for cohesive installation.

| Bundle | Contents |
|---|---|
| `knowledge-virtuoso` | All knowledge skills (design patterns, refactoring, SOLID, debugging, clean architecture, testing, API design, security, scrum, performance, microservices, git workflow, CI/CD, accessibility, database design, verification-before-completion, dispatching-parallel-agents, subagent-driven-development) |
| `playbooks-virtuoso` | All playbook skills (php-upgrade, composer-dependencies, finishing-branch) |
| `symfony-virtuoso` | Symfony component reference + upgrade guide |
| `django-virtuoso` | Django component reference |
| `langchain-virtuoso` | LangChain ecosystem reference |

**When to pick a category bundle:**

- Team adopting a shared reference library
- You want coverage across a domain (all knowledge, all Symfony, etc.)
- You are uncertain which skill you will need and want the whole category at hand

**Trade-off:** A bit of surface area you may not use. The cost is metadata, not runtime — unused skills do not consume context until triggered.

---

## Tier 3: Agents Bundle

Everything agentic in one install.

| Bundle | Contents |
|---|---|
| `agents-virtuoso` | All 15 agents (8 specialists + 7 roles) plus all 7 role skills |

**When to pick the agents bundle:**

- Setting up a new project that will use multi-agent workflows
- Team that wants the full agent roster available from day one
- Any project where chaining patterns are a daily tool

**Trade-off:** Full footprint. For solo or narrow use, individual `agent-{name}` or `role-{name}` plugins are leaner.

---

## Recommended Install Sets

### Starter (narrow focus, solo)

- One or two individual tool or role plugins matching your immediate work
- Add more as needs surface

### Backend-focused team

- `knowledge-virtuoso` (reference base)
- `agents-virtuoso` (full agent roster)
- `playbooks-virtuoso` (operational procedures)
- Framework bundle matching stack (`symfony-virtuoso` or `django-virtuoso`)

### Frontend-focused team

- `knowledge-virtuoso` (includes accessibility, performance, design patterns)
- `role-frontend-dev` + `role-qa-engineer`
- Individual `agent-reviewer`, `agent-test-gap-analyzer`

### Platform / infrastructure team

- `knowledge-virtuoso` (includes cicd, security, microservices)
- `agent-dependency-auditor`, `agent-migration-planner`
- `playbooks-virtuoso`

### Meta-author (builds skills, agents, plugins)

- All four tool plugins: `tool-agentic-rules-writer`, `tool-ticket-writer`, `tool-agent-creator`, `tool-plugin-creator`
- `using-virtuoso` (this skill) for ecosystem discovery
- Optionally the full `knowledge-virtuoso` for reference while authoring

---

## Versioning Policy

The top-level marketplace version in `metadata.version` follows semantic rules:

| Change | Bump |
|---|---|
| Content edits to existing skills | Patch |
| New skills or agents added | Minor |
| Renames, directory restructures, removals | Major |

Individual plugin versions track the marketplace version when updated together.

---

## Install Commands

```bash
# Category bundle
npx skills add krzysztofsurdy/code-virtuoso --plugin knowledge-virtuoso

# Individual role
npx skills add krzysztofsurdy/code-virtuoso --plugin role-architect

# All bundles
npx skills add krzysztofsurdy/code-virtuoso --all

# List available plugins without installing
npx skills add krzysztofsurdy/code-virtuoso --list
```

---

## When to Create a New Plugin

When adding a skill or agent to the marketplace:

- Fits existing category bundle → add to the bundle, bump minor
- New role → create `role-{name}` plugin plus add to `agents-virtuoso`
- New specialist agent → create `agent-{name}` plugin plus add to `agents-virtuoso`
- New tool skill → create `tool-{name}` plugin
- New framework → create `{framework}-virtuoso` bundle
- New category entirely → restructure with a major bump

See `CONTRIBUTING.md` for the full workflow.
