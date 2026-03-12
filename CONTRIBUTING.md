# Contributing

Code Virtuoso is a collection of AI agent skills and sub-agent definitions built on the [Agent Skills](https://agentskills.io) open standard. Contributions include new skills, new agents, improvements to existing content, and structural fixes.

## Getting Started

There is no build step, test suite, or runtime. "Development" means writing and editing markdown files that follow specific conventions. To contribute:

1. Clone the repository
2. Read this guide and the [README](README.md) for project context
3. Browse existing skills in `skills/` and agents in `agents/` to understand the format and depth expected
4. Check the `template/` directory for starter templates (`SKILL.md`, `agent.md`)
5. Check the `spec/` directory for format specifications (`skill-spec.md`, `agent-spec.md`, `agent-skills-spec.md`)

## Project Structure

```
agents/              -- Sub-agent definitions (specialist and role agents)
skills/
  knowledge/         -- Conceptual reference material (SOLID, testing, debugging, etc.)
  tools/             -- Interactive tools (agentic-rules-writer)
  playbooks/         -- Step-by-step operational procedures (PHP upgrade, etc.)
  roles/             -- Team role reference skills (product manager, architect, etc.)
  frameworks/{name}/ -- Framework-specific skills (Symfony, Django, LangChain)
spec/                -- Format specifications
template/            -- Starter templates
.claude-plugin/      -- Marketplace configuration (Claude Code format; adaptable to other platforms)
```

See the [README](README.md) for the full directory tree and skill tables.

## Adding a New Skill

### 1. Choose the Right Category

| Category | When to use | Example |
|---|---|---|
| `skills/knowledge/` | Concepts, principles, reference material | SOLID, design patterns, testing theory |
| `skills/tools/` | Interactive tools that generate output | Rules writer |
| `skills/playbooks/` | Step-by-step procedures for recurring tasks | PHP upgrade, dependency updates |
| `skills/roles/` | Team role definitions with responsibilities and workflows | Product manager, QA engineer |
| `skills/frameworks/{name}/` | Framework-specific component references or upgrade guides | Symfony components, Django components |

### 2. Create the Directory Structure

```
skills/{category}/your-skill-name/
  SKILL.md
  references/
    topic-a.md
    topic-b.md
```

Every skill has a `SKILL.md` at the root and a `references/` directory for deep-dive content. Reference files do not have frontmatter.

### 3. Write SKILL.md

#### Frontmatter Fields

```yaml
---
name: your-skill-name          # Kebab-case, matches directory name
description: What this skill does. Use when {trigger condition}.
user-invocable: false           # true only if the skill is meant to be called directly by users
allowed-tools: Read Grep Glob Bash  # Optional: restrict tool access (platform-specific, see note below)
---
```

The `description` field is the most important field for discoverability. It controls when AI agents activate the skill. Write it to be keyword-rich and trigger-oriented.

**Note on platform-specific frontmatter:** The `name`, `description`, and `user-invocable` fields are part of the [Agent Skills](https://agentskills.io) open standard and work across platforms. The `allowed-tools` field is a platform-specific extension (e.g., Claude Code uses tool names like `Read`, `Grep`, `Glob`, `Bash`; other platforms may use different names or not support tool restrictions). If your skill needs tool restrictions, document them and adapt to your platform.

#### user-invocable Guidelines

The `user-invocable` field controls whether a skill appears as a runnable command (e.g., `/skill-name` or `@skill-name` depending on platform). Set it based on the skill category:

| Category | `user-invocable` | Reason |
|---|---|---|
| `knowledge/` | `false` | Background reference, auto-loaded by context or agents |
| `frameworks/` | `false` | Background reference, auto-loaded |
| `roles/` | `false` | Background reference, loaded by agents |
| `playbooks/` | `true` | User runs these as step-by-step procedures |
| `tools/` | `true` | User runs these directly to generate output |

Every SKILL.md **must** include this field. If omitted, behavior varies by platform.

#### No Provider-Specific Models

Do not include a `model` field in skill or agent definitions. Model selection is a user/platform decision, not a content decision. Hardcoding provider-specific model names (e.g., `sonnet`, `gpt-4o`, `gemini-pro`) makes skills and agents non-portable. Users configure model preferences in their own platform settings.

#### Description Guidelines

Descriptions should be 1-3 sentences that pack in relevant keywords and trigger conditions. The pattern is: what it covers + when to use it.

Good example (language-specific skill):

> Comprehensive skill for all 26 Gang of Four design patterns with idiomatic implementations and real-world examples. Use when the user asks to apply a design pattern, refactor code using patterns, choose between competing patterns, or review existing pattern usage.

Good example (procedural skill):

> Version upgrade guide -- step-by-step process for upgrading runtime/framework versions, automated refactoring, compatibility checking, breaking changes per version, and testing strategies. Use when planning or executing a version upgrade.

Bad example:

> A skill about design patterns.

#### SKILL.md Structure

Follow this order:

1. **Title** -- one paragraph summary of core philosophy
2. **Core Principles** -- table with `| Principle | Meaning |` columns
3. **Main sections** -- tables, commands, pattern indexes (varies by skill type)
4. **Quick Reference: Checklist** -- step-by-step checklist with `- [ ]` items
5. **Reference Files** -- table linking to `references/` files with `| Reference | Contents |` columns
6. **Integration with Other Skills** -- table with `| Situation | Recommended Skill |` columns

Minimal example:

```markdown
---
name: my-skill
description: One-line description. Use when {trigger condition}.
user-invocable: false
---

# My Skill

One paragraph summary.

## Core Principles

| Principle | Meaning |
|---|---|
| **Principle one** | What it means in practice |

## Reference Files

| Reference | Contents |
|---|---|
| [topic-a](references/topic-a.md) | Deep dive into topic A |

## Integration with Other Skills

| Situation | Recommended Skill |
|---|---|
| When you need X | `other-skill` |
```

**Note on skill references:** In the Integration table, reference skills by name. How users invoke skills depends on their platform (e.g., `/skill-name` as a slash command in Claude Code, `@skill-name` in other tools, or automatic activation based on context).

### 4. Add Reference Files

Reference files live in `references/` and contain the deep content: code examples, detailed workflows, comparison tables. SKILL.md provides the overview; references provide the depth. This is the **progressive disclosure** pattern -- agents load SKILL.md first and only read reference files when they need detail on a specific topic.

### 5. Update marketplace.json (MANDATORY)

Every skill change requires a marketplace.json update. This is non-negotiable.

Add your skill path to the appropriate plugin's `skills` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "knowledge-virtuoso",
  "skills": [
    "./skills/knowledge/existing-skill",
    "./skills/knowledge/your-new-skill"
  ]
}
```

If no existing plugin fits your skill, create a new plugin entry. See [Marketplace Configuration](#marketplace-configuration) for details.

### 6. Update README.md

Add your skill to the appropriate table in `README.md` and update the Repository Structure tree if you created a new directory.

## Adding a New Agent

Agents are sub-agent definitions that can be used by AI coding agents that support delegation (e.g., Claude Code [sub-agents](https://code.claude.com/docs/en/sub-agents), Cursor agents, GitHub Copilot). There are two types:

- **Specialist agents** -- focused on a single task (investigation, code review, refactoring). Typically read-only.
- **Role agents** -- embody a team position (architect, QA engineer). May have persistent memory and preloaded skills.

### 1. Create the Agent Definition File

Create a markdown file in `agents/`:

```
agents/your-agent-name.md
```

### 2. Agent Frontmatter

```yaml
---
name: your-agent-name           # Kebab-case identifier
description: What this agent does. Delegate when {trigger condition}.
tools: Read, Grep, Glob, Bash   # Comma-separated list of allowed tools (platform-specific)
                                 # Do NOT specify a model -- let users choose based on their platform
isolation: worktree              # Optional: worktree for agents that modify files
memory: project                  # Optional: project-level persistent memory
skills:
  - related-skill-name           # Optional: preload specific skills
---
```

**Note on platform-specific fields:** The `name`, `description`, and `skills` fields are portable across agent platforms. The `tools`, `isolation`, and `memory` fields are platform-specific extensions. Adapt tool names to your platform. The same [no provider-specific models](#no-provider-specific-models) rule applies to agents.

| Field | Required | Portable | Notes |
|---|---|---|---|
| `name` | Yes | Yes | Matches the filename without `.md` |
| `description` | Yes | Yes | Keyword-rich, explains when to delegate to this agent |
| `tools` | Yes | No | Limit to minimum needed. Read-only agents should not have write/edit access |
| `model` | No | No | **Do not include.** Let users choose models via their platform settings |
| `isolation` | No | No | Set to `worktree` if the agent creates or modifies files |
| `memory` | No | No | Set to `project` for role agents that need context across sessions |
| `skills` | No | Yes | List skill names to preload when the agent starts |

### 3. Agent Body

After the frontmatter, define:

- **Role statement** -- one sentence: "You are a [role]. You [core responsibility]."
- **Input** -- what the agent receives
- **Process** -- numbered steps for the agent's workflow
- **Rules** -- constraints and guardrails
- **Output** -- what the agent returns when finished

See `agents/investigator.md` or `agents/implementer.md` for complete examples.

### 4. Update marketplace.json and README.md

Add the agent path to the appropriate plugin's `agents` array and to the `agents-virtuoso` plugin. Update the agent tables in README.md.

## Updating Existing Skills

- Make your content changes
- Bump the version in `marketplace.json` (see [Version Bumping Rules](#version-bumping-rules))
- Test that the skill activates correctly after your changes

## Marketplace Configuration

The file `.claude-plugin/marketplace.json` defines how skills and agents are packaged for installation. Each plugin groups related skills and/or agents that users can install together.

```json
{
  "name": "plugin-name",
  "description": "What this plugin provides",
  "source": "./",
  "strict": false,
  "skills": ["./skills/category/skill-name"],
  "agents": ["./agents/agent-name.md"]
}
```

**When to create a new plugin vs. add to an existing one:**

- Add to an existing plugin when your skill fits its theme (e.g., a new knowledge skill goes into `knowledge-virtuoso`)
- Create a new plugin when you are adding a new framework, a new tool category, or a standalone bundle that users would install independently
- Individual role plugins (e.g., `role-backend-dev`) exist so users can install a single role with its agent -- follow this pattern for new roles

### Plugin Naming Convention

| Type | Pattern | Example |
|---|---|---|
| Category bundle | `{category}-virtuoso` | `knowledge-virtuoso`, `agents-virtuoso` |
| Individual role | `role-{name}` | `role-architect` |
| Individual agent | `agent-{name}` | `agent-reviewer` |
| Individual tool | `tool-{name}` | `tool-agentic-rules-writer` |
| Framework bundle | `{framework}-virtuoso` | `symfony-virtuoso`, `django-virtuoso` |

### Plugin Distribution Tiers

The marketplace uses a tiered model for maximum installation flexibility:

| Tier | Pattern | Example | Contains | Use case |
|---|---|---|---|---|
| Individual | `role-{name}` or `agent-{name}` | `role-architect`, `agent-reviewer` | 1 skill + 1 agent (roles) or 1 agent (specialists) | Install a single role or agent |
| Category bundle | `{category}-virtuoso` | `knowledge-virtuoso`, `playbooks-virtuoso` | All skills in a category | Install all skills in a category |
| Agents bundle | `agents-virtuoso` | `agents-virtuoso` | All 15 agents + all 7 role skills | Full agent team with role context |

**Key design decisions:**
- `agents-virtuoso` is the complete package -- all agents plus all role skills
- Individual `role-{name}` plugins contain both the skill and agent for that role
- Individual `agent-{name}` plugins contain a single specialist agent
- Knowledge, playbooks, and frameworks have their own category bundles (skills only, no agents)

When adding a new role:
- Create the role skill in `skills/roles/{name}/`
- Create the agent in `agents/{name}.md`
- Add to `agents-virtuoso` (skill + agent)
- Create an individual `role-{name}` plugin (skill + agent)

When adding a new specialist agent:
- Create the agent in `agents/{name}.md`
- Add to `agents-virtuoso`
- Create an individual `agent-{name}` plugin

## Version Bumping Rules

The version field lives in `metadata.version` inside `marketplace.json`.

| Change type | Version bump | Example |
|---|---|---|
| Content updates to existing skills | Patch | 7.13.0 -> 7.13.1 |
| New skills or agents added | Minor | 7.13.0 -> 7.14.0 |
| Restructuring, renames, breaking changes | Major | 7.13.0 -> 8.0.0 |

## Commit Conventions

- No AI co-author lines in commits
- Descriptive commit messages summarizing what was added or changed
- One logical change per commit
- Example: `Add Kubernetes deployment skill with 5 reference files`
- Example: `Update design-patterns skill with Specification pattern`

## Quality Standards

Skills should be production-grade reference material, not tutorials. They are consumed by AI agents that need precise, actionable information.

| Guideline | Target |
|---|---|
| Reference files | 100-700 lines each |
| SKILL.md | Under 500 lines (use progressive disclosure) |
| Tables | Use for all structured data (comparisons, commands, options) |
| Cross-references | Include an Integration section linking to related skills |
| Code examples | Idiomatic for the target language/framework, using current stable versions |
| Principles table | Required in every SKILL.md -- sets the mindset before details |
| Frontmatter | Only in SKILL.md and agent files, never in reference files |

### Language and Provider Agnosticism

All content must be **language-agnostic** and **LLM provider-agnostic** by default. Do not assume a specific programming language, framework, or AI provider unless the skill explicitly targets one.

| Content type | Rule |
|---|---|
| Knowledge skills | Fully language-agnostic. Use pseudocode or multi-language examples. |
| Role skills | Fully agnostic. No language-specific code. |
| Agent definitions | No provider-specific model names. No platform-specific tool names in the body. |
| Framework skills (`frameworks/`) | Language/framework-specific by definition. Target latest stable version. |
| Playbooks | May be language-specific if the procedure is (e.g., PHP upgrade). State the scope clearly. |

**The only exceptions** are skills that explicitly exist for a specific language, framework, or LLM provider (e.g., `symfony-components`, `django-components`, `php-upgrade`). These should state their scope in the description.

### Content Guidelines

- Show realistic, production-quality examples -- not toy code
- Include both the "happy path" and error handling where relevant
- Keep instructions actionable -- tell the agent what to do, not just what exists

### Research Process for New Skills

Before writing a new skill:

1. Search for existing skills: `npx skills find "{topic}"`
2. Search the web for official documentation and community best practices
3. Read 2-3 existing skills in this project to match structure and depth
4. Use the template in `template/SKILL.md` as a starting point
