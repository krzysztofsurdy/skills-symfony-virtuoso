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

## Guided Phases

Interactive skills with 3+ phases where LLMs tend to rush through steps can use a **guided phase** structure. This is an internal pattern -- users experience better-paced interactions without knowing about the underlying file organization.

### When to use

- The skill has 3+ distinct phases that each need user input before proceeding
- LLMs tend to merge, skip, or rush through the phases when they are inline
- Each phase has a natural checkpoint where the user should confirm before continuing

Skills with phases that share heavy context or where inline flow works well should keep phases inline in SKILL.md. Guided phases add value when phase separation prevents rushing, not when it just reorganizes.

### Directory structure

```
skill-name/
  SKILL.md              # Shared rules, principles, phase listing
  phases/               # One file per phase
    01-phase-name.md
    02-phase-name.md
    03-phase-name.md
  references/           # Deep-dive material (unchanged)
```

### SKILL.md role

In a guided-phase skill, SKILL.md holds shared rules, principles, and context ONCE. It does NOT duplicate phase instructions. It lists phases with one-line descriptions and links. On activation, the agent loads SKILL.md first, then enters phases sequentially.

### Phase file structure

Each phase file is lean (40-80 lines). It contains:

1. **Header** with phase number, name, and progress indicator
2. **Purpose** -- one sentence describing what this phase accomplishes
3. **Steps** -- numbered execution instructions
4. **Gate** -- conditions for advancing, and the question to ask the user

The gate is the key mechanism. Every phase file ends with a gate that forces the agent to stop and wait for user confirmation before loading the next phase.

See `template/phase-template.md` for the starter template.

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
