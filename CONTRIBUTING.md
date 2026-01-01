# Contributing to Symfony Virtuoso

## Adding a New Skill

### 1. Create the skill directory

```bash
cp -r template skills/symfony-<component-name>
```

Naming convention: `symfony-<component-name>` using the official Symfony component name in lowercase with hyphens (e.g., `symfony-messenger`, `symfony-security`, `symfony-http-kernel`).

### 2. Write SKILL.md

Every skill requires a `SKILL.md` with YAML frontmatter and Markdown instructions.

**Frontmatter** (required fields):

```yaml
---
name: symfony-messenger
description: Symfony Messenger component for async message handling. Use when implementing message buses, command/event/query patterns, message handlers, transports, or async processing in Symfony applications.
---
```

- `name` must match the directory name
- `description` should explain both what the skill covers and when to activate it

**Body content** should include:

- Overview of the component
- Key concepts and APIs
- Common patterns with PHP 8.3+ code examples
- Configuration examples (YAML preferred)
- Testing guidelines
- Common pitfalls and how to avoid them

### 3. Add references (optional)

Place detailed documentation in `references/`:

```
skills/symfony-messenger/
├── SKILL.md
└── references/
    └── REFERENCE.md
```

Keep `SKILL.md` under 500 lines. Move API details, exhaustive examples, and edge cases to reference files.

### 4. Register the skill

Add the skill path to `.claude-plugin/marketplace.json` under the appropriate plugin's `skills` array:

```json
"skills": [
  "./skills/symfony-messenger"
]
```

## Skill Quality Guidelines

- Target PHP 8.3+ and Symfony 7.x
- Use strict typing in all code examples (`declare(strict_types=1)`)
- Show realistic, production-quality code — not toy examples
- Include both the "happy path" and error handling where relevant
- Reference official Symfony documentation where appropriate
- Keep instructions actionable — tell the agent what to do, not just what exists

## Format Specification

Skills follow the [Agent Skills standard](https://agentskills.io/specification).
