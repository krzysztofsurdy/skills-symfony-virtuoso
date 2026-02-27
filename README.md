# Code Virtuoso

AI agent skill sets for software engineering — built on the [Agent Skills](https://agentskills.io) open standard. Knowledge, Setup, and Frameworks.

Three categories of plugins, installable independently or as bundles:

- **Knowledge** — Design Patterns, Refactoring, SOLID Principles, Debugging. Reference material with progressive disclosure.
- **Setup** — Agentic Rules Writer. Agent configuration and bootstrapping tools.
- **Frameworks** — Symfony. Component-level reference for framework-specific development.

---

## Knowledge Skills

### Design Patterns Virtuoso (26 patterns)

Covers all Gang of Four patterns plus Null Object, Object Pool, and Private Class Data — organized as creational, structural, and behavioral with PHP 8.3+ implementations.

See [skills/knowledge/design-patterns/SKILL.md](skills/knowledge/design-patterns/SKILL.md) for the full pattern index.

### Refactoring Virtuoso (89 skills)

Covers 67 refactoring techniques (composing methods, moving features, organizing data, simplifying conditionals, simplifying method calls, dealing with generalization) and 22 code smells (bloaters, OO abusers, change preventers, dispensables, couplers).

See [skills/knowledge/refactoring/SKILL.md](skills/knowledge/refactoring/SKILL.md) for the full technique and smell index.

### SOLID Virtuoso (5 principles)

Covers all five SOLID principles — Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion — with original explanations, violation detection, before/after PHP 8.3+ examples, and multi-language examples (Java, Python, TypeScript, C++).

See [skills/knowledge/solid/SKILL.md](skills/knowledge/solid/SKILL.md) for the full principle index.

### Debugging

Systematic debugging methodology — root cause analysis, bug category strategies (logic, data, state, integration, performance, environment, intermittent), evidence-based diagnosis, escalation criteria, and post-mortem templates. Stack-agnostic.

See [skills/knowledge/debugging/SKILL.md](skills/knowledge/debugging/SKILL.md) for the full methodology.

---

## Setup Skills

### Agentic Rules Writer

Generate a rules file for any AI coding agent at global, project team-shared, or project dev-specific scope. Runs an interactive questionnaire about your workflow preferences, scans installed skills at runtime, and writes a tailored instruction file in the correct format and location for Claude Code, Cursor, Windsurf, GitHub Copilot, Gemini CLI, Roo Code, or Amp.

See [skills/setup/agentic-rules-writer/SKILL.md](skills/setup/agentic-rules-writer/SKILL.md) for the full interactive flow.

---

## Framework Skills

### Symfony Virtuoso (38 components)

Covers all Symfony components — HTTP handling, dependency injection, forms, validation, caching, messaging, console commands, event dispatching, workflows, serialization, testing, filesystem operations, configuration, and utility components. PHP 8.3+ and Symfony 7.x.

See [skills/frameworks/php/symfony/SKILL.md](skills/frameworks/php/symfony/SKILL.md) for the full component index.

---

## Installation

Clone (or add as a submodule) and copy the skills you need into the location your tool expects.

```bash
git clone https://github.com/krzysztofsurdy/code-virtuoso.git
```

### Claude Code

**Via plugin marketplace (recommended):**

```bash
# Add the marketplace
/plugin marketplace add krzysztofsurdy/code-virtuoso

# Bundle installs (recommended)
/plugin install knowledge-virtuoso@krzysztofsurdy-code-virtuoso
/plugin install setup-rules-writer@krzysztofsurdy-code-virtuoso
/plugin install symfony-virtuoso@krzysztofsurdy-code-virtuoso

# Or install individually
/plugin install knowledge-design-patterns@krzysztofsurdy-code-virtuoso
/plugin install knowledge-refactoring@krzysztofsurdy-code-virtuoso
/plugin install knowledge-solid@krzysztofsurdy-code-virtuoso
/plugin install knowledge-debugging@krzysztofsurdy-code-virtuoso
```

Or browse interactively: run `/plugin`, go to **Discover**, and install individual plugins.

**Manual install:**

```bash
# Project-level (committed to your repo)
cp -r code-virtuoso/skills/knowledge/design-patterns .claude/skills/

# User-level (available in all projects)
cp -r code-virtuoso/skills/knowledge/design-patterns ~/.claude/skills/
```

Skills are discovered automatically — just mention a component in conversation.

### OpenAI Codex CLI

```bash
cp -r code-virtuoso/skills/knowledge/design-patterns .codex/skills/
```

### Gemini CLI

```bash
cat code-virtuoso/skills/knowledge/design-patterns/SKILL.md >> GEMINI.md
```

### GitHub Copilot

```bash
mkdir -p .github/instructions
cp code-virtuoso/skills/knowledge/design-patterns/SKILL.md .github/instructions/design-patterns.instructions.md
```

### Amp / OpenCode / Kimi

```bash
cp -r code-virtuoso/skills/knowledge/design-patterns .agents/skills/
cp -r code-virtuoso/skills/knowledge/refactoring .agents/skills/
```

### Cursor

```bash
mkdir -p .cursor/rules
cp code-virtuoso/skills/knowledge/design-patterns/SKILL.md .cursor/rules/design-patterns.mdc
```

### Windsurf

```bash
mkdir -p .windsurf/rules
cp code-virtuoso/skills/knowledge/design-patterns/SKILL.md .windsurf/rules/design-patterns.md
```

## Repository Structure

```
code-virtuoso/
├── skills/
│   ├── knowledge/
│   │   ├── design-patterns/
│   │   │   ├── SKILL.md           # Overview + pattern index
│   │   │   └── references/        # 26 individual pattern docs
│   │   ├── refactoring/
│   │   │   ├── SKILL.md           # Overview + technique/smell index
│   │   │   └── references/        # 89 individual technique/smell docs
│   │   ├── solid/
│   │   │   ├── SKILL.md           # Overview + principle index
│   │   │   └── references/        # 5 individual principle docs
│   │   └── debugging/
│   │       ├── SKILL.md           # Systematic debugging methodology
│   │       └── references/        # Bug categories + post-mortem template
│   ├── setup/
│   │   └── agentic-rules-writer/
│   │       ├── SKILL.md           # Interactive rules file generator
│   │       └── references/        # Questionnaire + agent targets
│   └── frameworks/
│       └── php/
│           └── symfony/
│               ├── SKILL.md       # Overview + component index
│               └── references/    # 38 individual component docs
├── spec/
│   └── agent-skills-spec.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or improving skills.

## License

MIT
