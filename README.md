# Code Virtuoso

AI agent skill sets for software engineering — built on the [Agent Skills](https://agentskills.io) open standard.

Three categories of plugins, installable independently:

- **Knowledge** — Design Patterns, Refactoring, SOLID Principles. Reference material with progressive disclosure.
- **Workflows** — Ticket Workflow, PR Message Writer, Report Generator, Agentic Rules Writer. Opinionated workflows that adapt to your environment.
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

---

## Workflow Skills

### Ticket Workflow

End-to-end ticket lifecycle — from ticket analysis through investigation, planning, TDD implementation, committing, and PR creation. On first run, creates a supplement file by asking about your environment: ticket system, VCS, error tracking, logging, database, CI/CD hooks, testing framework, architecture, and PR conventions. All subsequent runs adapt automatically.

See [skills/workflows/ticket-workflow/SKILL.md](skills/workflows/ticket-workflow/SKILL.md) for the full workflow phases.

### PR Message Writer

Write comprehensive pull request messages with structured technical documentation, testing instructions, and database verification queries. Framework-agnostic with a customizable template and real examples covering features, bug fixes, and schema changes.

See [skills/workflows/pr-message-writer/SKILL.md](skills/workflows/pr-message-writer/SKILL.md) for usage and templates.

### Report Generator

Generate polished standalone HTML reports summarizing changes, findings, debug investigations, or architectural decisions. Dark theme design system with collapsible sections, copy-to-clipboard code blocks, timeline components, impact grids, and print-friendly output. Single self-contained file with no external dependencies.

See [skills/workflows/report-generator/SKILL.md](skills/workflows/report-generator/SKILL.md) for report types and components.

### Agentic Rules Writer

Generate a rules file for any AI coding agent at global, project team-shared, or project dev-specific scope. Runs an interactive questionnaire about your workflow preferences, scans installed skills at runtime, and writes a tailored instruction file in the correct format and location for Claude Code, Cursor, Windsurf, GitHub Copilot, Gemini CLI, Roo Code, or Amp.

See [skills/workflows/agentic-rules-writer/SKILL.md](skills/workflows/agentic-rules-writer/SKILL.md) for the full interactive flow.

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

# Knowledge skills
/plugin install design-patterns-virtuoso@krzysztofsurdy-code-virtuoso
/plugin install refactoring-virtuoso@krzysztofsurdy-code-virtuoso
/plugin install solid-virtuoso@krzysztofsurdy-code-virtuoso

# Workflow skills
/plugin install ticket-workflow@krzysztofsurdy-code-virtuoso
/plugin install pr-message-writer@krzysztofsurdy-code-virtuoso
/plugin install report-generator@krzysztofsurdy-code-virtuoso
/plugin install agentic-rules-writer@krzysztofsurdy-code-virtuoso

# Framework skills
/plugin install symfony-virtuoso@krzysztofsurdy-code-virtuoso
```

Or browse interactively: run `/plugin`, go to **Discover**, and install individual plugins.

**Manual install:**

```bash
# Project-level (committed to your repo)
cp -r code-virtuoso/skills/knowledge/design-patterns .claude/skills/
cp -r code-virtuoso/skills/workflows/ticket-workflow .claude/skills/

# User-level (available in all projects)
cp -r code-virtuoso/skills/workflows/ticket-workflow ~/.claude/skills/
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
│   │   └── solid/
│   │       ├── SKILL.md           # Overview + principle index
│   │       └── references/        # 5 individual principle docs
│   ├── workflows/
│   │   ├── ticket-workflow/
│   │   │   ├── SKILL.md           # Full ticket lifecycle workflow
│   │   │   └── references/        # Supplement question reference
│   │   ├── pr-message-writer/
│   │   │   ├── SKILL.md           # PR message creation guide
│   │   │   └── references/        # Template + example PRs
│   │   ├── report-generator/
│   │   │   ├── SKILL.md           # HTML report generation guide
│   │   │   └── references/        # HTML template
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
