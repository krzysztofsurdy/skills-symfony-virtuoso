# Skill Specification

This document defines the conventions for skills in the code-virtuoso marketplace. It extends the [Agent Skills Specification](https://agentskills.io/specification) with project-specific rules.

## Directory Structure

```
skill-name/
  SKILL.md              # Required
  references/            # Optional - detailed reference material
  agents/                # Optional - agents that use this skill
  scripts/               # Optional - executable code
  assets/                # Optional - static resources
```

## SKILL.md Format

### Frontmatter

```yaml
---
name: skill-name
description: What this skill does and when to use it.
user-invocable: false
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Must match the parent directory name. Lowercase, hyphens only, 1-64 chars. |
| `description` | Yes | What the skill does and when to use it. Max 1024 chars. Include trigger keywords. |
| `user-invocable` | No | Set to `false` for knowledge/reference skills not meaningful as slash commands. Omit for interactive skills. |
| `argument-hint` | No | Hint text shown after the slash command (e.g. `"[optional: agent-name]"`). |
| `license` | No | License name or reference to a bundled license file. |
| `metadata` | No | Arbitrary key-value mapping for additional metadata. |

### Body Content

The markdown body after frontmatter contains skill instructions. Keep under 500 lines. Move detailed content to `references/`.

## Categories

Skills are organized into three categories:

| Category | Path | Purpose |
|----------|------|---------|
| `knowledge` | `skills/knowledge/` | Reference material on concepts, patterns, and practices |
| `frameworks` | `skills/frameworks/` | Framework-specific knowledge and component guides |
| `tools` | `skills/tools/` | Interactive workflows and setup utilities |

## References

- Place in `references/` subdirectory
- Keep each file under 250 lines and focused on a single topic
- Use relative markdown links from SKILL.md: `[Topic](references/topic.md)`
- Agents load these on demand, so smaller files mean less context usage

## Agents

Agents that belong to a skill live in the skill's `agents/` subdirectory. See [agent-spec.md](agent-spec.md) for the agent format.

## Progressive Disclosure

Skills load in three levels:

1. **Metadata** (~100 tokens) - `name` and `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens) - Full SKILL.md body loaded when skill is activated
3. **Resources** (as needed) - Files in references/, scripts/, assets/ loaded only when required

## Content Guidelines

- Write original content. External sources serve as inspiration only.
- Do not mention authors, books, or specific sources by name.
- Do not copy content verbatim from external resources.
- Use generic template names (e.g. "Focus / Impact / Confirmation" not "Author's Template").
- Keep language concise and actionable.

## Naming Conventions

- Lowercase letters, numbers, and hyphens only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens
- Name must match the parent directory name
