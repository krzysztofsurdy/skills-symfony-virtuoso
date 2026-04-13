---
name: agent-creator
description: Interactive tool to design a well-scoped sub-agent definition -- specialist, role, or team-lead -- with the right frontmatter, tool permissions, isolation, memory, and system prompt. Use when the user asks to create a sub-agent, write an agent file, design a specialized worker, scaffold a role agent, bootstrap an agent team, or turn a repeated delegation pattern into a reusable agent. Runs a six-phase questionnaire and outputs a ready-to-commit agent markdown file plus marketplace registration.
user-invocable: true
argument-hint: "[optional: archetype -- specialist, role, team-lead]"
---

# Agent Creator

Create a sub-agent that earns its context window. Most agents fail not because the model is weak but because the definition is vague -- unclear trigger, sprawling tool list, a body that mixes persona and procedure, and no output contract. This skill walks you through a six-phase design so the resulting agent is focused, least-privileged, and predictable.

## Core Principles

| Principle | Meaning |
|---|---|
| **One job, one agent** | An agent that does two things does neither well. Split the responsibility before writing. |
| **Least privilege** | Grant the smallest tool set that lets the agent finish its job. Read-only by default. |
| **Trigger-first description** | The `description` field is the only thing read before delegation. Pack it with keywords and "when to use". |
| **Contract over conversation** | Define explicit input, process, and output. Agents are not chat sessions. |
| **Isolation when writing** | If the agent edits files, run it in a worktree so the orchestrator can review before merging. |
| **Portable body, platform frontmatter** | Keep the system prompt agent-agnostic. Adapt frontmatter fields per target platform. |

---

## Agent vs Skill -- Quick Disambiguation

Before creating an agent, confirm it is the right primitive.

| Use a Skill | Use an Agent |
|---|---|
| Reference material (patterns, checklists, schemas) | Work to perform (investigate, review, implement) |
| Loaded into an existing session | Runs in its own context window |
| Passive knowledge | Active actor with tools and a workflow |
| "Where do I learn about X" | "Do X for me and return a result" |

If the answer is reference material, stop and use the `skill-creator` skill instead. If the answer is work, continue.

---

## Archetype Selection

Agents fall into three archetypes. Pick one before designing.

| Archetype | Scope | Memory | Modifies files | Typical examples |
|---|---|---|---|---|
| **Specialist** | Single, repeatable task type | Stateless | Rarely (doc writer, implementer) | Investigator, Reviewer, Refactor Scout, Dependency Auditor, Test Gap Analyzer |
| **Role** | Entire domain of responsibility | Often persistent (project-level) | Dev roles yes, others no | Product Manager, Architect, Backend Dev, QA Engineer, Project Manager |
| **Team-Lead** | Coordinates multiple workers in parallel | Shared task list | No (delegates) | Orchestrator, release-train lead, review dispatcher |

### Decision tree

1. Does the agent do **one repeatable task type** (review this PR, investigate this area, audit dependencies)? -> **Specialist**
2. Does the agent **own a domain** across many task types and benefit from remembering context across sessions (requirements, architecture decisions, risk register)? -> **Role**
3. Does the agent need to **spawn and coordinate other agents** working in parallel (research teams, multi-layer refactors)? -> **Team-Lead**

If the user provided an archetype as an argument, use it. Otherwise present a selectable menu using `AskUserQuestion` (or the platform's equivalent interactive prompt) with the three options from the table above.

See [references/archetypes.md](references/archetypes.md) for worked examples of each archetype and the anti-patterns to avoid.

---

## Workflow

### Phase 1: Purpose and Trigger

Ask the user, in a single batched `AskUserQuestion` call (or platform equivalent), up to four of these:

1. **What task does this agent perform?** (one sentence, imperative form)
2. **When should the orchestrator delegate to it?** (the trigger condition -- list phrases or situations)
3. **What should the agent NOT do?** (explicit out-of-scope items)
4. **What does success look like?** (the shape of the output it returns)

Write these answers down verbatim -- they feed both the `description` field and the system prompt.

If the user's answer to Q1 contains "and" joining two different actions, push back: "That looks like two agents. Pick the primary responsibility first; a second agent can be created after." Split or narrow before continuing.

### Phase 2: Name and Identity

Derive a kebab-case name that describes the role, not the task:

- Good: `investigator`, `reviewer`, `migration-planner`, `backend-dev`
- Bad: `agent1`, `helper`, `do-stuff`, `claude-assistant`

If the name collides with an existing agent in the scope (see Phase 5), append a qualifier (`reviewer-security`, `reviewer-frontend`) rather than overwriting.

Confirm the name with the user before proceeding.

### Phase 3: Capabilities

Decide four things. Present them as one batched question set.

**3.1 Tool permissions.** Start from read-only and add only what the workflow requires. See [references/tool-selection.md](references/tool-selection.md) for the full decision tree.

| Needs | Typical tool allowlist |
|---|---|
| Investigation only | Read, Grep, Glob, Bash (for running analysis commands) |
| Review / audit | Read, Grep, Glob, Bash |
| Documentation | Read, Grep, Glob, Bash, Edit, Write (docs only) |
| Implementation | Read, Grep, Glob, Bash, Edit, Write |
| Coordination | Read, Grep, Glob, Bash, plus ability to spawn sub-agents |

**3.2 Isolation.** If the agent writes source code, set `isolation: worktree` so changes land in a temporary branch the orchestrator reviews before merging. Read-only agents never need isolation.

**3.3 Memory.** Most specialist agents are stateless. Role agents that accumulate cross-session context (requirements history, ADRs, risk register) use project-level memory. Skip memory for specialists; offer it for role and team-lead archetypes.

**3.4 Preloaded skills.** List any skills whose reference content the agent needs in its context at startup. One to four is typical; more and you are loading context it will never read. Reference skills by their `name` field, not path.

### Phase 4: System Prompt

The body of the agent file is its system prompt. Structure it as a contract with five sections:

```
You are a [role]. You [one-sentence responsibility].

## Input
What the agent receives when delegated to.

## Process
Numbered steps the agent runs through.

## Rules
Constraints and guardrails. What the agent must never do.

## Output
The exact shape of what the agent returns. Include a template.
```

See [references/system-prompts.md](references/system-prompts.md) for full patterns, worked examples per archetype, and common mistakes (persona bloat, missing output contract, process without guardrails).

Do not include:

- Filler preamble ("You are a helpful AI assistant...") -- the caller already knows
- Model-specific phrasing ("As Claude...") -- the body should be portable
- Tool instructions that contradict the frontmatter allowlist
- A second responsibility "while you're at it" -- that is a different agent

### Phase 5: Placement and Scope

Ask the user where the agent file should live. Scope determines priority when multiple agents share a name.

| Scope | Location (platform-neutral) | Use when |
|---|---|---|
| **Project** | `.claude/agents/<name>.md` or the project's agent directory | Agent is specific to this codebase and should be committed |
| **User / personal** | `~/.claude/agents/<name>.md` (or platform-equivalent user dir) | Agent is personal and reused across all your projects |
| **Plugin / marketplace** | Inside the plugin's `agents/` directory | Agent ships as part of a distributable bundle |
| **Session-only** | Passed via CLI flag as inline JSON | One-off testing or automation scripts |

Project scope is the safest default for team-shared work. Personal scope is for individual preferences. Plugin scope is for redistribution.

See [references/platforms.md](references/platforms.md) for the exact path on each supported platform and for frontmatter fields that are platform-specific versus portable.

### Phase 6: Validate and Write

Before writing, run the checklist in [references/validation.md](references/validation.md). The essentials:

- [ ] Description contains both "what it does" and "when to delegate"
- [ ] Tool allowlist is the minimum needed
- [ ] `isolation: worktree` is set if and only if the agent modifies files
- [ ] System prompt has Role, Input, Process, Rules, and Output sections
- [ ] Output section contains a concrete template, not a vague description
- [ ] Body contains no persona bloat or filler
- [ ] Name matches the file name and is kebab-case

Then write the file:

1. Create the agent markdown file at the chosen path
2. If the target is a marketplace-style project, register the agent in the appropriate plugin entry of `marketplace.json` (or the platform's plugin manifest)
3. If a README or agent index exists in the project, add the agent row
4. Echo the final path and line count to the user
5. Offer: "Do you want to test-invoke this agent now?"

---

## Reference Files

| Reference | Contents |
|---|---|
| [archetypes.md](references/archetypes.md) | Worked examples of specialist, role, and team-lead agents, plus anti-patterns |
| [frontmatter-fields.md](references/frontmatter-fields.md) | Full field reference, portable vs platform-specific, and examples |
| [tool-selection.md](references/tool-selection.md) | Least-privilege tool allowlists, per-archetype defaults, and denylist patterns |
| [system-prompts.md](references/system-prompts.md) | System prompt patterns: role-input-process-rules-output contract, worked examples |
| [platforms.md](references/platforms.md) | Scope paths, platform-specific frontmatter fields, and agent-team considerations |
| [validation.md](references/validation.md) | Pre-publish checklist and common rejection reasons |

---

## Integration with Other Skills

| Situation | Recommended Skill |
|---|---|
| Creating a reference skill instead of an agent | `skill-creator` |
| Writing AI rules files for an agent platform | `agentic-rules-writer` |
| Designing how multiple agents interact in a workflow | See `archetypes.md` team-lead section |
| Authoring a ticket or PRD that spawns the agent | `ticket-writer` |
