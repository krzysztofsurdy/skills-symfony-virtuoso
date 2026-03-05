# Agent Specification

This document defines the conventions for agents in the code-virtuoso marketplace. Agents are Claude Code subagents that use skills to perform specialized tasks.

## Location

Agents live inside their parent skill's `agents/` subdirectory:

```
skills/knowledge/scrum/
  SKILL.md
  references/
  agents/
    scrum-master.md
```

## File Format

Agent files use YAML frontmatter followed by markdown content.

### Frontmatter

```yaml
---
name: agent-name
description: What this agent does and when to use it.
tools: Read, Grep, Glob, Bash
model: sonnet
skills:
  - parent-skill-name
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase, hyphens only. Should describe the agent's role. |
| `description` | Yes | What the agent does and when to delegate to it. Include trigger phrases. |
| `tools` | Yes | Comma-separated list of tools the agent can use. |
| `model` | No | Model to use (e.g. `sonnet`, `opus`). Defaults to the caller's model. |
| `skills` | No | List of skill names the agent has access to. Referenced by `name` field, not path. |

### Body Content

The markdown body is the agent's system prompt. Structure it with clear sections:

```markdown
You are a [role]. You [core responsibility].

## Core Responsibilities

1. First responsibility
2. Second responsibility

## Workflow

When asked to [task]:
1. Step one
2. Step two

## Communication Style

- Style guideline one
- Style guideline two
```

## Conventions

- One agent file per role
- Agent references skills by their `name` field, not by file path
- Keep the system prompt focused and actionable
- Define clear workflows for each type of task the agent handles
- Include a communication style section to set tone and behavior

## Naming Conventions

- Lowercase letters, numbers, and hyphens only
- Name should describe the role (e.g. `scrum-master`, `code-reviewer`)
- File name should match the `name` field (e.g. `scrum-master.md`)

## Marketplace Registration

Agents are registered in `.claude-plugin/marketplace.json` under their plugin's `agents` array:

```json
{
  "name": "plugin-name",
  "skills": ["./skills/knowledge/scrum"],
  "agents": ["./skills/knowledge/scrum/agents/scrum-master.md"]
}
```
