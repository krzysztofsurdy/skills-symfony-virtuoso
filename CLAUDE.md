# Code Virtuoso - Project Instructions

## Project Overview

Agent AI skill sets organized into six categories: Knowledge, Tools, Frameworks, Playbooks, Roles, and Agents.

## Directory Structure

```
agents/                 -- Sub-agent definitions (Anthropic standard, NOT skills)
  investigator.md       -- 8 specialist agents (read-only analysis, TDD, review, etc.)
  product-manager.md    -- 7 role agents (team positions with memory and skill preloading)
  ...
skills/
  knowledge/            -- Conceptual reference material (SOLID, testing, debugging, etc.)
  tools/                -- Interactive tools (agentic-rules-writer)
  playbooks/            -- Repeatable operational procedures (PHP upgrade, Composer dependencies)
  roles/                -- Role reference skills (product-manager, architect, backend-dev, etc.)
  frameworks/
    symfony/
      symfony-components/   -- Symfony component references (38 components)
      symfony-upgrade/      -- Symfony version upgrade guide
    django/
      django-components/    -- Django component references (33 components)
    langchain/
      langchain-components/ -- LangChain component references (17 components)
```

## Creating New Skills

### Research Process

When creating a new skill, follow this research workflow:

1. **Search skills.sh** for existing skills: `npx skills find "{topic}"`
2. **Fetch skill details** from skills.sh URLs to understand what others have built
3. **Search the web** for official documentation, best practices, and community guides
4. **Use parallel research agents** to gather information on multiple subtopics simultaneously
5. **Read existing skills** in this project to match the structure and depth

### Skill Structure

Every skill follows the same pattern:

```
skill-name/
  SKILL.md              -- Overview, principles table, quick reference, checklist, integration links
  references/
    topic-a.md          -- Deep-dive reference with code examples and detailed workflows
    topic-b.md          -- Additional reference material
```

### SKILL.md Template

```markdown
---
name: skill-name
description: One-line description. Use when {trigger condition}.
user-invocable: false
---

# Skill Title

One paragraph summary of the core philosophy.

## Core Principles
| Principle | Meaning |
|---|---|

## [Main Sections with tables, commands, patterns]

## Quick Reference: Checklist
- [ ] Step-by-step checklist

## Reference Files
| Reference | Contents |
|---|---|

## Integration with Other Skills
| Situation | Recommended Skill |
|---|---|
```

### Key Conventions

- Principles tables go first -- they set the mindset before the details
- Use tables for structured data (comparisons, commands, options)
- Reference files contain the deep content with code examples
- Cross-reference related skills in the Integration section
- For upgrade/update skills: always include "Changelog first" as the top principle

### Skill Categories

| Category | Purpose | Example |
|---|---|---|
| `knowledge/` | Concepts to understand | SOLID, design patterns, testing theory |
| `tools/` | Interactive tools that generate output | Rules writer |
| `playbooks/` | Step-by-step procedures to follow | PHP upgrade, dependency updates |
| `roles/` | Team role reference material | Product manager, architect, QA engineer |
| `frameworks/{name}/` | Framework-specific skills | Symfony components, Symfony upgrade |
| `agents/` (top-level) | Sub-agent definitions (not skills) | Investigator, implementer, reviewer |

## Marketplace Configuration

File: `.claude-plugin/marketplace.json`

**MANDATORY:** Any change to skills MUST include a marketplace.json update. This is non-negotiable.

- When adding a new skill: update skill paths in the appropriate plugin, bump **minor** version (e.g., 7.9.0 -> 7.10.0)
- When updating an existing skill's content: bump **patch** version (e.g., 7.10.0 -> 7.10.1)
- When renaming skills, reorganizing directories, or changing plugin structure: bump **major** version (e.g., 7.10.0 -> 8.0.0)
- Each plugin groups related skills
- Skill paths point to directories containing SKILL.md
- Update the metadata description to reflect all current categories
- Also update README.md skill tables and repository structure when adding/renaming/moving skills

## Commit Conventions

- No AI co-author lines in commits
- Descriptive commit messages summarizing what was added/changed

## Resources

Reference documentation for the skills ecosystem and agent architecture:

- [Vercel Agent Skills](https://github.com/vercel-labs/skills/tree/main) -- example skills from Vercel Labs
- [Anthropic Skills](https://github.com/anthropics/skills) -- official Anthropic skills repository
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) -- how skills work in Claude Code
- [Claude Code Sub-Agents Docs](https://code.claude.com/docs/en/sub-agents) -- sub-agent architecture and patterns
