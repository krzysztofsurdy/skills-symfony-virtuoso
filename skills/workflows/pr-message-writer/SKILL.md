---
name: pr-message-writer
description: Write comprehensive pull request messages with structured technical documentation, testing instructions, and verification queries. Framework-agnostic with customizable templates.
argument-hint: "[optional: branch-name or ticket-id]"
---

# PR Message Writer

Write comprehensive, well-structured pull request descriptions by analyzing code changes and following established best practices for technical documentation.

## Workflow

### Step 1: Gather Context

1. Determine the main branch:
   ```bash
   git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
   ```
   Falls back to `main` or `master` if not set.

2. Find the merge base:
   ```bash
   MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
   MERGE_BASE=$(git merge-base HEAD origin/$MAIN_BRANCH)
   ```

3. Collect all changes since the branch diverged:
   ```bash
   git log --oneline $MERGE_BASE..HEAD
   git diff --stat $MERGE_BASE..HEAD
   git diff $MERGE_BASE..HEAD
   ```

4. If a ticket ID or branch name is provided as an argument, include it in the PR title.

### Step 2: Analyze Changes

Read every changed file and understand:
- **What** was changed (new files, modified logic, deleted code)
- **Why** the change was made (bug fix, new feature, refactoring, performance)
- **Impact** on existing functionality (breaking changes, migrations, cache invalidation)
- **Dependencies** introduced or removed

### Step 3: Follow the Template

Use the PR message template for structure: [template](references/template.md)

Review real-world examples for tone and detail level: [examples](references/examples.md)

### Step 4: Match Change Type to Categories

Apply the appropriate sections based on what the PR touches:

| Category | When to Include |
|----------|----------------|
| Database and Entity/Model Changes | New tables, columns, migrations, schema changes |
| API Changes (REST/GraphQL) | New or modified endpoints, query/mutation changes |
| Admin Interface Changes | New admin pages, filters, list views, form fields |
| Caching and Performance | Cache keys, invalidation, query optimization |
| Security and Permissions | Auth rules, role checks, access control changes |
| Event Handling | New events, listeners, subscribers, message queue changes |
| Testing | New or modified test cases, fixtures, test utilities |

### Step 5: Write Testing Instructions

For every PR, include:
- **Step-by-step reproduction** — what to do in the UI or API to verify
- **API/query examples** — copy-pasteable requests with example variables
- **Database verification** — SQL queries to confirm data integrity
- **Edge cases** — boundary conditions the reviewer should test

### Step 6: Maintain Consistency

- Use the same section ordering as the template
- Write in imperative mood for descriptions ("Add product review entity" not "Added" or "Adds")
- Include code blocks with language hints for syntax highlighting
- Keep line length reasonable for readability in PR tools

## Quality Checklist

Before finalizing the PR message, verify:

- [ ] Title is concise and includes ticket ID if available
- [ ] "What have I changed" covers every file group logically
- [ ] Testing instructions are specific enough for someone unfamiliar with the feature
- [ ] Database verification queries are included for any schema changes
- [ ] Product-facing changes are called out explicitly
- [ ] No sensitive data (secrets, tokens, internal URLs) is included
- [ ] Migration steps are documented if applicable
- [ ] Breaking changes are highlighted prominently

## Common Patterns by PR Type

### New Feature
- Describe the business requirement briefly
- List new entities/models, endpoints, and admin pages
- Provide full testing flow from setup to verification
- Include database queries showing new data

### Bug Fix
- State the bug clearly: what happened vs. what should happen
- Explain root cause
- Describe the fix and why this approach was chosen
- Include regression test instructions

### Refactoring
- Explain motivation (tech debt, performance, maintainability)
- Confirm no behavioral changes (or document any intentional ones)
- List before/after comparisons if helpful
- Note any config or dependency changes

### Database Migration
- List all schema changes (new tables, columns, indexes)
- Note if migration is reversible
- Flag any data migrations that touch existing rows
- Include rollback instructions if applicable

## References

- [PR message template](references/template.md)
- [Example PR messages](references/examples.md)
