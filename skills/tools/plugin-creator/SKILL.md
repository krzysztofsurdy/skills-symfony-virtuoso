---
name: plugin-creator
description: Interactive tool to scaffold a complete Claude Code plugin -- plugin.json manifest, skills, agents, hooks, MCP servers, LSP servers, and an optional marketplace.json catalog entry. Use when the user asks to create a plugin, build a Claude Code plugin, scaffold a plugin marketplace, convert an existing .claude/ configuration into a plugin, or package skills and agents for distribution. Runs a guided questionnaire, writes all required files to disk, and prints test instructions.
user-invocable: true
argument-hint: "[optional: plugin-name]"
---

# Plugin Creator

Scaffold a well-formed Claude Code plugin with exactly the components the user wants -- no more, no less. A plugin is a self-contained directory with a manifest (`.claude-plugin/plugin.json`) plus any of: skills, agents, hooks, MCP servers, LSP servers, bin executables, output styles, default settings. This tool generates the correct structure, writes a valid manifest, adds a marketplace entry when requested, and explains how to test locally with `--plugin-dir`.

## Core Principles

| Principle | Meaning |
|---|---|
| **Manifest is optional, but recommended** | If omitted, the directory name becomes the plugin name and components auto-discover at default locations. Provide one whenever metadata, versioning, or custom paths matter. |
| **Default locations first** | Prefer `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json` at plugin root. Only override paths in `plugin.json` when there is a real reason. |
| **Components live at the root, not in `.claude-plugin/`** | Only `plugin.json` belongs inside `.claude-plugin/`. Everything else (`skills/`, `agents/`, etc.) is at the plugin root. This is the single most common mistake. |
| **Use `${CLAUDE_PLUGIN_ROOT}` for every plugin-internal path** | Absolute paths break when the plugin is cached. `${CLAUDE_PLUGIN_ROOT}` resolves to the installed plugin directory at runtime. Use `${CLAUDE_PLUGIN_DATA}` for state that must survive updates. |
| **Namespacing is automatic** | Plugin skills are always invoked as `/plugin-name:skill-name`. Names are derived from the `name` field in `plugin.json` (or directory name if no manifest). |
| **Semantic versioning in one place** | Set `version` in `plugin.json` OR in the marketplace entry -- not both. When present in both, `plugin.json` wins. |

---

## Workflow

The tool runs six phases. Each phase uses a structured interactive menu (`AskUserQuestion` or the agent CLI equivalent) -- never plain-text prompts the user must type into. Batch up to 4 independent questions per call where the tool supports it.

1. **Phase 1** -- Plugin identity (name, description, version, author)
2. **Phase 2** -- Component selection (which of: skills, agents, hooks, MCP, LSP, bin, output styles, settings)
3. **Phase 3** -- Per-component details (one sub-questionnaire per selected component type)
4. **Phase 4** -- Distribution decision (standalone plugin or plugin + marketplace)
5. **Phase 5** -- Write files to disk (manifest, components, optional marketplace, optional README)
6. **Phase 6** -- Print test & install instructions

If the user aborts at any phase, discard progress and exit without writing a partial plugin.

---

## Phase 1: Plugin Identity

Collect the plugin's core metadata. If `$ARGUMENTS` is provided, use it as the default plugin name (still confirm with the user).

### Questions (batch of 4)

**Q1. Plugin name** (free text, required)
Must be kebab-case, no spaces. This becomes the namespace for skills: `/plugin-name:skill-name`. Reject anything containing spaces, uppercase, or non-alphanumeric characters other than `-`.

**Q2. Short description** (free text, required)
One sentence. Shown in the plugin manager when browsing marketplaces.

**Q3. Starting version** (options)
- `1.0.0` -- first stable release (recommended default)
- `0.1.0` -- pre-stable, signalling breaking changes are expected
- `Other` -- free text, must match `MAJOR.MINOR.PATCH`

**Q4. Author** (free text, optional)
Format: `Name <email>` or just `Name`. Leave blank to omit the `author` block entirely.

### Optional metadata (ask only if the user wants extras)

After Q1-Q4, ask a single yes/no: **"Add optional metadata (homepage, repository, license, keywords)?"** If yes, batch these:

- Homepage URL (free text, optional)
- Repository URL (free text, optional)
- License SPDX identifier (options: `MIT`, `Apache-2.0`, `GPL-3.0`, `BSD-3-Clause`, `UNLICENSED`, `Other`)
- Keywords (free text, comma-separated, optional)

See [references/plugin-manifest.md](references/plugin-manifest.md) for the complete field list and path-behavior rules.

---

## Phase 2: Component Selection

Present a **multi-select** menu asking which components this plugin includes. At least one must be selected, otherwise the plugin has no functionality.

| Component | Default Location | Purpose |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | User- or model-invokable capabilities. Appear as `/plugin-name:skill-name`. |
| Agents | `agents/<name>.md` | Specialized subagents with their own tool allow-lists and system prompts. |
| Hooks | `hooks/hooks.json` | Event handlers (PreToolUse, PostToolUse, SessionStart, etc.). |
| MCP servers | `.mcp.json` | External tool integrations via Model Context Protocol. |
| LSP servers | `.lsp.json` | Language Server Protocol for code intelligence. |
| Bin executables | `bin/` | Shell scripts or binaries added to the Bash tool's `PATH` while the plugin is enabled. |
| Output styles | `output-styles/` | Custom response styles the user can activate. |
| Default settings | `settings.json` | Pre-configured `agent` override applied when the plugin is enabled. |

For each selected component type, Phase 3 runs a sub-questionnaire.

---

## Phase 3: Per-Component Details

For each component type the user selected, run the matching sub-questionnaire below. Loop until the user signals "no more" for that component type.

See [references/component-templates.md](references/component-templates.md) for ready-to-use file templates for every component type.

### 3A. Skills

For each skill:

1. **Skill name** (kebab-case) -- becomes the directory name under `skills/`
2. **Description** (free text) -- goes into the `description` frontmatter. Claude uses this to decide when to invoke the skill.
3. **Invocation model** (options):
   - `Model-invoked` (default) -- Claude activates automatically based on description
   - `User-only` -- add `disable-model-invocation: true` frontmatter so only `/plugin-name:skill-name` triggers it
4. **Needs arguments?** (yes/no) -- if yes, add `argument-hint` frontmatter and include `$ARGUMENTS` in the skill body template
5. **Add references directory?** (yes/no) -- pre-create `skills/<name>/references/` for progressive-disclosure content

After each skill, ask: "Add another skill?" (yes/no).

### 3B. Agents

For each agent:

1. **Agent name** (kebab-case) -- becomes `agents/<name>.md`
2. **Description** (free text) -- one sentence on when Claude should delegate to this agent
3. **Isolation** (options):
   - `None` (default)
   - `worktree` -- agent operates in an isolated git worktree (only valid value)
4. **Tool allow-list** (options):
   - `Read-only` -- `Read, Grep, Glob, Bash`
   - `Full access` -- omit `tools` field (inherits all)
   - `Custom` -- free text (comma-separated tool names)
5. **Memory** (options): `none` / `project`
6. **Preload skills?** (free text, comma-separated skill names, optional)

Plugin agents do not support `hooks`, `mcpServers`, or `permissionMode` fields -- warn the user if they ask.

### 3C. Hooks

Ask once: **"Which lifecycle events should trigger hooks?"** (multi-select)

Common events: `SessionStart`, `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `FileChanged`, `CwdChanged`. The full list is in [references/component-templates.md](references/component-templates.md).

For each selected event, collect:
1. **Matcher pattern** (free text, optional) -- regex matching tool names (e.g. `Write|Edit`) or filenames for `FileChanged`
2. **Hook type** (options): `command` / `http` / `prompt` / `agent`
3. **Command/URL/prompt body** (free text)

Default scripts land in `scripts/<hook-name>.sh` and the command uses `${CLAUDE_PLUGIN_ROOT}/scripts/<hook-name>.sh`. Remind the user: scripts need `chmod +x` and a shebang.

### 3D. MCP Servers

For each MCP server:
1. **Server key** (kebab-case) -- identifier used in the `mcpServers` object
2. **Command** (free text) -- the executable to run (e.g. `npx`, `${CLAUDE_PLUGIN_ROOT}/servers/db-server`)
3. **Args** (free text, comma-separated, optional)
4. **Environment variables** (free text, KEY=VALUE per line, optional)

If the command references bundled files, remind the user to use `${CLAUDE_PLUGIN_ROOT}`.

### 3E. LSP Servers

Only scaffold an LSP plugin when no official marketplace plugin covers the target language. For each LSP server:
1. **Language identifier** (free text) -- e.g. `go`, `typescript`
2. **Binary** (free text) -- must be available on user's `$PATH` (e.g. `gopls`, `pyright-langserver`)
3. **Args** (free text, comma-separated, optional)
4. **File extensions** (free text, comma-separated) -- e.g. `.go` maps to `go`

Remind the user: LSP plugins configure the connection but do not bundle the language server binary. Users must install it separately.

### 3F. Bin Executables

For each bin entry:
1. **Executable name** (free text)
2. **Language** (options): `bash` / `node` / `python` / `other`
3. **Short description of what it does** (free text)

Scaffold a shebang-appropriate stub at `bin/<name>` and remind the user to `chmod +x` it.

### 3G. Output Styles

For each output style:
1. **Style name** (kebab-case) -- becomes `output-styles/<name>.md`
2. **Style description** (free text)

Scaffold a minimal template; the user fills in the voice/tone themselves.

### 3H. Default Settings

Only one key is currently supported: `agent`. Ask: **"Which of the plugin's agents should be activated as the main thread by default?"** (single-select from agents added in 3B; include `None` option to skip).

---

## Phase 4: Distribution Decision

Ask a single question: **"How will this plugin be distributed?"** (options)

1. **Standalone** -- just the plugin directory, tested locally with `--plugin-dir`
2. **New marketplace** -- create a sibling `.claude-plugin/marketplace.json` listing this plugin
3. **Add to existing marketplace** -- append the plugin entry to an existing `marketplace.json` the user points to

### If option 2 (new marketplace)

Collect:
- Marketplace name (kebab-case; reject reserved names -- see [references/marketplace-manifest.md](references/marketplace-manifest.md))
- Marketplace owner name (free text)
- Marketplace owner email (free text, optional)
- Marketplace directory layout:
  - `Flat` -- plugin lives at repo root, marketplace entry uses `"source": "./"` and `strict: false` (single-plugin repos)
  - `Nested` -- plugin lives at `./plugins/<plugin-name>/`, marketplace references it by relative path (multi-plugin repos; recommended)

### If option 3 (existing marketplace)

Ask for the path to the existing `marketplace.json`. Read it, preserve all existing fields, append the new plugin entry, bump `metadata.version` (minor bump for a new plugin).

See [references/marketplace-manifest.md](references/marketplace-manifest.md) for the complete marketplace schema, plugin source types (relative path, github, url, git-subdir, npm), and strict-mode rules.

---

## Phase 5: Write Files

Write all generated files in a single pass. Before writing:

1. **Validate the plugin name** -- kebab-case, no spaces, not a reserved marketplace name
2. **Validate JSON** -- parse generated `plugin.json` and `marketplace.json` before writing
3. **Confirm the destination** -- show the target directory path and ask for final approval

### Directory structure to produce

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
├── skills/                (if any skills)
│   └── <skill-name>/
│       ├── SKILL.md
│       └── references/    (if requested in 3A)
├── agents/                (if any agents)
│   └── <agent-name>.md
├── hooks/                 (if any hooks)
│   └── hooks.json
├── .mcp.json              (if any MCP servers)
├── .lsp.json              (if any LSP servers)
├── bin/                   (if any bin executables)
│   └── <name>
├── output-styles/         (if any output styles)
│   └── <name>.md
├── scripts/               (if hooks reference bundled scripts)
│   └── <hook-name>.sh
├── settings.json          (if default settings were set)
├── LICENSE                (if license was chosen, skip for UNLICENSED)
└── CHANGELOG.md           (seeded with version 1.0.0 entry)
```

### If a marketplace was also requested

For `Nested` layout:

```
<marketplace-name>/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── <plugin-name>/
        └── [plugin contents above]
```

For `Flat` layout:

```
<marketplace-name>/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
└── [plugin contents at root]
```

Use the templates in [references/component-templates.md](references/component-templates.md) for each file. Never invent fields that are not in the schema -- the schema references are the source of truth.

### Seed a CHANGELOG.md

```markdown
# Changelog

## 1.0.0 -- YYYY-MM-DD

- Initial release
```

### Seed a LICENSE (if chosen)

Write the standard SPDX text for the chosen license. For `UNLICENSED`, skip the file.

---

## Phase 6: Test & Install Instructions

After writing, print:

1. **Full tree of what was created** (relative paths only)
2. **Local test command**:
   ```
   claude --plugin-dir ./<plugin-name>
   ```
3. **Reload during development**:
   ```
   /reload-plugins
   ```
4. **Validation command**:
   ```
   claude plugin validate
   ```
5. **Next steps**:
   - If standalone: "Push to a git host, then share `git@host:owner/repo.git` with users."
   - If marketplace: "Push the marketplace repo, then users run `/plugin marketplace add <source>` followed by `/plugin install <plugin-name>@<marketplace-name>`."
   - If adding to existing marketplace: "Commit the updated `marketplace.json`, push, and users can `/plugin marketplace update` to pick up the new entry."
6. **Distribution considerations** (only if relevant):
   - Semantic versioning rules -- see [references/distribution.md](references/distribution.md)
   - How to pin to branch/tag/sha -- see [references/marketplace-manifest.md](references/marketplace-manifest.md)
   - Plugin caching caveat -- files referenced with `../` outside the plugin root will not work; use symlinks if sharing code across plugins

---

## Rules & Guardrails

- **Never put components inside `.claude-plugin/`**. Only `plugin.json` lives there.
- **Never use absolute paths** in `plugin.json`, hooks, or MCP configs. All plugin-internal paths must start with `./` or use `${CLAUDE_PLUGIN_ROOT}`.
- **Never reference files outside the plugin directory** via `../` -- the plugin cache will not copy them. Symlinks are preserved, so use those if cross-plugin sharing is truly needed.
- **Never set `hooks`, `mcpServers`, or `permissionMode` on a plugin-shipped agent** -- these are blocked for security.
- **Never set both `version` in `plugin.json` and in the marketplace entry.** Pick one authoritative location.
- **Always bump the version when the plugin content changes.** The Claude Code cache uses the version to decide whether to update. Forgetting this is why users do not see plugin updates.
- **Reject reserved marketplace names** (`claude-code-marketplace`, `anthropic-marketplace`, etc. -- full list in [references/marketplace-manifest.md](references/marketplace-manifest.md)).
- **Validate JSON before writing**. A corrupt `plugin.json` breaks the plugin silently in some cases and loudly in others -- both waste the user's time.

---

## Quick Reference: Minimal Plugin

The smallest valid plugin is a directory with one SKILL.md:

```
my-plugin/
└── skills/
    └── hello/
        └── SKILL.md
```

No `plugin.json` is required -- the directory name becomes the plugin name. Add a manifest only when you need metadata, versioning, or custom paths.

---

## Reference Files

| Reference | Contents |
|---|---|
| [plugin-manifest.md](references/plugin-manifest.md) | Complete `plugin.json` schema: required + metadata + component path fields, `userConfig`, `channels`, path behavior rules, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` usage. |
| [marketplace-manifest.md](references/marketplace-manifest.md) | Complete `marketplace.json` schema: owner, plugins array, all source types (relative, github, url, git-subdir, npm), strict mode, reserved names. |
| [component-templates.md](references/component-templates.md) | Ready-to-use templates for `plugin.json`, `SKILL.md`, agent files, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `settings.json`, `bin/` scripts, and output styles. |
| [distribution.md](references/distribution.md) | Hosting options (git hosts, local, URL, npm), semantic versioning, release workflow, auto-update behavior, team marketplace configuration via `extraKnownMarketplaces`. |

---

## Integration with Other Skills

| Situation | Recommended Skill |
|---|---|
| Creating the actual skill content inside a plugin | `skill-creator` |
| Writing the agent body for a plugin-shipped agent | Check existing agent definitions in `agents/` for patterns |
| Generating rules files to pair with a plugin | `agentic-rules-writer` |
| Writing tickets for plugin-related backlog items | `ticket-writer` |
