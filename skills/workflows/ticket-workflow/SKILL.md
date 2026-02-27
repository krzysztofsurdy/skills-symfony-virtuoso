---
name: ticket-workflow
description: End-to-end ticket workflow — from ticket analysis through investigation, planning, TDD implementation, committing, and PR creation. Adapts to your environment via a supplement file created on first run.
argument-hint: "<ticket-id>"
---

# Ticket Workflow

End-to-end workflow that takes a ticket ID and drives it through analysis, codebase investigation, planning, TDD implementation, committing, and PR creation. Adapts to your stack via an interactive supplement created on first run.

## Phase 0: Environment Supplement

Before anything else, check for the supplement file at `~/.claude/skills/ticket-workflow/.supplement.md`.

### If supplement exists
Read the file and load all `$VARIABLE` values for use throughout the workflow.

### If supplement is missing
Run an interactive setup. Ask the developer each question, wait for the answer, then proceed to the next. Save all answers to `~/.claude/skills/ticket-workflow/.supplement.md`.

**Questions to ask** (see [supplement reference](references/supplement-questions.md) for full details):

1. **Ticket system** — Jira / Linear / GitHub Issues / GitLab Issues / Other? MCP tool name for fetching tickets?
2. **Version control** — GitHub / GitLab / Bitbucket? CLI tool (`gh`, `glab`)? Main branch name?
3. **Error tracking** — Sentry / Datadog / Bugsnag / none? MCP tool name?
4. **Logging** — Grafana / CloudWatch / Datadog / ELK / none? MCP access or manual paste?
5. **Database** — ORM (Doctrine / Eloquent / ActiveRecord / Prisma / TypeORM / none)? Read-only query command?
6. **CI/CD hooks** — Pre-commit hooks to skip? (e.g., `SKIP=lint,test git commit`)
7. **Testing framework** — PHPUnit / Jest / pytest / RSpec / Go test / other? TDD style preference (London / Chicago)?
8. **Architecture** — Monolith / microservices? Admin panel? API layer (REST / GraphQL / both)?
9. **PR conventions** — Branch naming pattern? Commit message format?

After saving, confirm: "Supplement saved. You can edit it anytime at `~/.claude/skills/ticket-workflow/.supplement.md` or delete it to re-run setup."

---

## Agent Team Strategy

This workflow uses a multi-agent team when available. The lead agent coordinates specialized sub-agents for parallel investigation.

### Team Roles
| Role | Purpose |
|---|---|
| **Lead** | Orchestrates the full workflow, delegates investigation, reviews results |
| **Investigator (x1-3)** | Explores specific codebase layers in parallel during Phase 3 |
| **Implementer** | Executes TDD cycles during Phase 6 (or lead does this directly) |

Use teams only when the ticket scope justifies parallel investigation. For small bug fixes, the lead agent can handle everything alone.

---

## Phase 1: Ticket Intelligence Gathering

### Step 1.1 — Fetch Ticket Details

**If `$TICKET_MCP_TOOL` is configured:**
```
Use $TICKET_MCP_TOOL to fetch ticket $TICKET_ID
```

**If no MCP tool:**
Ask the developer: "Please paste the ticket title, description, and acceptance criteria."

### Step 1.2 — Parse Ticket Information
Extract and organize:
- **Title** and **description**
- **Acceptance criteria** (numbered list)
- **Ticket type** (bug / feature / improvement / refactor)
- **Priority** and **linked tickets**
- **Attachments or screenshots** (note them for later)

### Step 1.3 — Fetch Error Context (bugs only)

**If `$ERROR_TRACKING_MCP_TOOL` is configured and ticket is a bug:**
```
Use $ERROR_TRACKING_MCP_TOOL to fetch error details linked in the ticket
```
Extract: stack trace, affected file paths, frequency, first/last seen.

**If no MCP tool:** Ask developer to paste relevant error details or stack traces.

### Step 1.4 — Fetch Log Context (if applicable)

**If `$LOGGING_TOOL` is configured:**
Fetch relevant log entries around the error timeframe.

**If manual:** Ask developer to paste relevant log snippets if available.

### Step 1.5 — Summarize Findings
Present a structured summary:
```
TICKET: $TICKET_ID
TYPE: [bug|feature|improvement|refactor]
SUMMARY: [one-line summary]
ACCEPTANCE CRITERIA: [numbered list]
ERROR CONTEXT: [if bug — stack trace summary, affected files]
INITIAL HYPOTHESES: [2-3 possible approaches]
```

Ask the developer: "Does this look correct? Any additional context before I investigate the codebase?"

---

## Phase 2: Branch Setup

```bash
git fetch origin
git checkout $MAIN_BRANCH
git pull origin $MAIN_BRANCH
```

Do NOT create a feature branch yet — that happens in Phase 5 after planning.

---

## Phase 3: Codebase Investigation

Investigate the codebase to understand the area affected by the ticket. Adapt the investigation to your project's architecture (`$ARCHITECTURE`).

### Investigation Areas

Run these in parallel when using agent teams, or sequentially as a single agent:

#### 3a — Entity / Model Layer
- Find domain models or entities related to the ticket
- Check properties, relationships, validation rules
- If using an ORM (`$ORM`): check mappings, migrations, schema

#### 3b — Service / Business Logic Layer
- Find services, handlers, use cases related to the ticket
- Trace the execution flow from entry point to persistence
- Identify dependencies and collaborators

#### 3c — API Layer (if applicable)
- **REST**: Find controllers, routes, request/response DTOs
- **GraphQL**: Find types, resolvers, mutations related to the feature
- Check authentication/authorization on relevant endpoints

#### 3d — Admin Panel (if configured)
- If the ticket involves admin functionality, investigate admin controllers or configuration
- Check how admin interfaces relate to the underlying models

#### 3e — Repository / Data Access Layer
- Find repositories, query builders, or data access objects
- Understand existing query patterns for the affected area
- If read-only queries are available (`$DB_QUERY_COMMAND`): verify current data state if relevant

#### 3f — Test Layer
- Find existing tests for the affected area
- Identify test patterns used (unit, integration, functional)
- Note any test fixtures, factories, or helpers

### Investigation Summary
After all areas are explored, compile:
```
AFFECTED FILES: [list of files that will likely need changes]
DEPENDENCIES: [services, classes, interfaces involved]
EXISTING TESTS: [test files covering the affected area]
DATABASE IMPACT: [schema changes needed, if any]
API IMPACT: [endpoint changes, if any]
RISK AREAS: [parts of the codebase that could break]
```

---

## Phase 4: Implementation Planning

Create a detailed plan before writing any code.

### Step 4.1 — Plan Structure
```
## Implementation Plan for $TICKET_ID

### Changes Required
1. [File path] — [What changes and why]
2. [File path] — [What changes and why]
...

### New Files
1. [File path] — [Purpose]
...

### Test Plan
1. [Test file] — [What to test]
2. [Test file] — [What to test]
...

### Migration / Schema Changes
[If applicable]

### Order of Operations
1. [First step — typically write failing tests]
2. [Second step]
...
```

### Step 4.2 — Design Consultation
If the implementation involves design decisions, consider consulting specialized skills:

| Situation | Recommended Skill |
|---|---|
| Design patterns needed | Install `design-patterns-virtuoso` from `krzysztofsurdy/code-virtuoso` |
| Code smells / refactoring | Install `refactoring-virtuoso` from `krzysztofsurdy/code-virtuoso` |
| SOLID principles | Install `solid-virtuoso` from `krzysztofsurdy/code-virtuoso` |
| PR message writing | Use `pr-message-writer` from `krzysztofsurdy/code-virtuoso` |
| Work summary report | Use `report-generator` from `krzysztofsurdy/code-virtuoso` |

### Step 4.3 — Plan Approval
Present the plan to the developer and wait for approval before proceeding.
"Here is my implementation plan. Shall I proceed, or would you like changes?"

---

## Phase 5: Branch Creation

After plan approval, create the feature branch.

**Using `$BRANCH_PATTERN` from supplement:**
```bash
git checkout -b $BRANCH_PATTERN
```

Example patterns:
- `feat/PROJ-123-short-description`
- `fix/PROJ-123-short-description`
- `PROJ-123/short-description`

---

## Phase 6: TDD Implementation

Follow a strict TDD cycle. Use `$TEST_COMMAND` from supplement.

### Step 6.1 — Write Failing Tests First
For each item in the test plan:
1. Write the test
2. Run it to confirm it fails: `$TEST_COMMAND path/to/TestFile`
3. Confirm the failure is for the RIGHT reason (not a syntax error)

### Step 6.2 — Implement to Make Tests Pass
Write the minimum code to make each test pass:
1. Implement the change
2. Run the specific test: `$TEST_COMMAND path/to/TestFile`
3. Confirm it passes

### Step 6.3 — Refactor
After tests pass:
1. Look for duplication, unclear naming, or structural improvements
2. Refactor while keeping tests green
3. Re-run tests after each refactor step

### Step 6.4 — Run Full Test Suite
Run the broader test suite to catch regressions:
```bash
$TEST_COMMAND [relevant test directory or suite]
```

Fix any failures before proceeding.

### Step 6.5 — Commit Changes
Commit using the project's conventions (`$COMMIT_FORMAT`):

```bash
$SKIP_HOOKS git add [specific files]
git commit -m "$COMMIT_FORMAT"
```

For large changes, make multiple focused commits rather than one monolithic commit.

---

## Phase 7: Implementation Summary

After all changes are committed, generate a summary:

```
## Implementation Summary for $TICKET_ID

### Changes Made
- [File]: [What changed and why]
- [File]: [What changed and why]

### Tests Added/Modified
- [Test file]: [What is tested]

### Commits
- [hash]: [message]

### Verification
- All new tests pass: YES/NO
- Existing tests pass: YES/NO
- Schema changes applied: YES/NO/N/A

### Notes
- [Any caveats, follow-up work, or decisions made during implementation]
```

---

## Phase 8: PR Creation

Use the `pr-message-writer` skill if available, or create the PR directly.

### Using pr-message-writer skill
Invoke the skill with the implementation summary and ticket context to generate a well-structured PR description.

### Direct PR creation
Use `$VCS_CLI` (e.g., `gh`, `glab`) to create the PR:

```bash
git push -u origin HEAD
$VCS_CLI pr create --title "$TICKET_ID: [short description]" --body "[PR body]"
```

The PR body should include:
- Link to the ticket
- Summary of changes
- Test plan / how to verify
- Screenshots (if UI changes)
- Any deployment notes

---

## Phase 9: Report Generation

If the `report-generator` skill is available, invoke it to create a work summary report covering:
- Ticket details and acceptance criteria
- Investigation findings
- Implementation decisions
- Test coverage
- PR link

This is optional but recommended for complex tickets.

---

## Critical Rules

1. **Never skip Phase 0.** The supplement ensures the workflow adapts to your stack. Without it, the skill cannot function correctly.

2. **Always get plan approval before coding.** Phase 4 must end with explicit developer approval.

3. **TDD is not optional.** Write tests first. If the project has no test infrastructure, flag this to the developer and discuss before proceeding.

4. **Commit granularity matters.** One logical change per commit. Do not bundle unrelated changes.

5. **Never force-push to the main branch.** Always work on feature branches.

6. **Ask when uncertain.** If the ticket is ambiguous, ask the developer rather than guessing. Wrong assumptions waste more time than a quick question.

7. **Respect existing patterns.** Match the project's coding style, naming conventions, and architectural patterns — even if you would do it differently.

8. **Keep the developer informed.** At the end of each phase, provide a brief status update. Do not silently proceed through multiple phases.

9. **Handle failures gracefully.** If tests fail unexpectedly, if the codebase does not match expectations, or if the ticket requirements are unclear — stop and communicate rather than pushing through.

10. **Security first.** Never commit secrets, credentials, or sensitive data. If a ticket requires configuration changes, use environment variables or configuration files that are in `.gitignore`.
