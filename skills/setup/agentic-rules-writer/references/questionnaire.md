# Questionnaire Reference

Detailed reference for each question in the global-agentic-rules-writer workflow. Covers question text, purpose, available options, answer-to-rule mappings, and example generated output.

---

## Q1. Primary Stack

**Question:** What is your primary tech stack?

**Purpose:** Generates stack-specific conventions (coding standards, type systems, common patterns) that apply globally across all projects using this stack.

| Option | Description |
|---|---|
| PHP+Symfony | PHP 8.x with Symfony framework |
| TypeScript+React | TypeScript with React (Next.js, Vite, etc.) |
| Python+Django | Python 3.x with Django framework |
| Go | Go standard library or common frameworks |
| Rust | Rust with Cargo |
| Java+Spring | Java with Spring Boot |
| Other | User specifies their stack |

**Generated rules by answer:**

- **PHP+Symfony** — "Use strict types in every file. Follow PSR-12 coding standard. Use PHP 8.3+ features (readonly, enums, named arguments). Prefer constructor injection."
- **TypeScript+React** — "Use strict TypeScript — no `any` types. Prefer functional components with hooks. Use named exports."
- **Python+Django** — "Follow PEP 8. Use type hints. Prefer class-based views for complex logic, function-based for simple endpoints."
- **Go** — "Follow Go conventions: short variable names, error returns, `gofmt`. Handle every error explicitly."
- **Rust** — "Prefer `Result` over `unwrap`. Use `clippy` lints. Follow Rust API guidelines."
- **Java+Spring** — "Follow Java naming conventions. Use constructor injection. Prefer records for DTOs."
- **Other** — "Follow the project's established coding standards and conventions."

---

## Q2. Planning Discipline

**Question:** How much planning before implementation?

**Purpose:** Controls when the agent enters plan mode vs. jumping straight to code.

| Option | Description |
|---|---|
| Always plan first | Enter plan mode for every task, regardless of size |
| Plan for 3+ steps | Plan mode only when the task requires 3 or more distinct steps |
| Minimal planning | Skip plan mode, proceed directly to implementation |

**Generated rules by answer:**

- **Always plan first:**
  ```
  - Enter plan mode before starting any task
  - Write a numbered step list before touching code
  - Get user approval on the plan before implementing
  ```

- **Plan for 3+ steps:**
  ```
  - Enter plan mode for any task that requires 3 or more steps
  - For simple changes (single file, obvious fix), proceed directly
  - When in doubt, plan — it's cheaper than rework
  ```

- **Minimal planning:**
  ```
  - Proceed directly to implementation for most tasks
  - Only pause to plan for architectural changes or multi-system modifications
  ```

---

## Q3. Testing Philosophy

**Question:** What is your testing approach?

**Purpose:** Defines when and how tests are written relative to implementation.

| Option | Description |
|---|---|
| Strict TDD | Write failing tests first, then implement to make them pass |
| Test alongside | Write tests and implementation together in the same pass |
| Test after | Implement first, then add tests to cover the change |
| Minimal | Only test critical paths and business logic |

**Generated rules by answer:**

- **Strict TDD:**
  ```
  - Write failing tests before any implementation code
  - Red-green-refactor cycle for every change
  - Never skip the refactor step
  - Aim for high coverage — unit, integration, and edge cases
  ```

- **Test alongside:**
  ```
  - Write tests alongside implementation — alternate between code and tests
  - Every new feature or fix should include corresponding tests
  - Cover happy paths, error cases, and boundary conditions
  ```

- **Test after:**
  ```
  - Implement the solution first, then add tests
  - At minimum, cover the changed behavior with regression tests
  - Focus on integration tests that verify end-to-end behavior
  ```

- **Minimal:**
  ```
  - Test critical business logic and complex algorithms
  - Skip tests for trivial getters/setters, simple CRUD, and framework boilerplate
  - Prioritize integration tests over unit tests
  ```

---

## Q4. Branch Conventions

**Question:** What branch naming convention do you follow?

**Purpose:** Generates rules for how the agent creates and names branches.

| Option | Description |
|---|---|
| Type prefix | `feature/`, `fix/`, `chore/`, `hotfix/` + description (e.g. `feature/add-user-auth`) |
| Ticket prefix | Ticket ID + description (e.g. `PROJ-123/add-user-auth` or `PROJ-123-add-user-auth`) |
| Flat descriptive | Just a descriptive name, no prefix (e.g. `add-user-auth`) |
| Other | User specifies their convention |

**Generated rules by answer:**

- **Type prefix:**
  ```
  - Name branches with type prefix: feature/, fix/, chore/, hotfix/
  - Use kebab-case for the description part
  - Example: feature/add-user-auth, fix/payment-timeout
  ```

- **Ticket prefix:**
  ```
  - Name branches with the ticket ID: PROJ-123/description or PROJ-123-description
  - Use kebab-case for the description part
  - Always include the ticket ID for traceability
  ```

- **Flat descriptive:**
  ```
  - Name branches with a clear, descriptive kebab-case name
  - Keep names short but meaningful
  - Example: add-user-auth, fix-payment-timeout
  ```

- **Other** — User's specified convention is included as-is.

---

## Q5. Commit Conventions

**Question:** What commit message format do you use?

**Purpose:** Ensures generated commit rules match the user's conventions.

| Option | Description |
|---|---|
| Conventional commits | Structured format: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:` |
| Ticket prefix | Ticket ID prefix: `PROJ-123: description` |
| Freeform | No enforced format — use clear, descriptive messages |

**Generated rules by answer:**

- **Conventional commits:**
  ```
  - Use conventional commit format: feat:, fix:, chore:, docs:, refactor:, test:
  - Keep subject line under 72 characters
  - Use body for context when the change is non-trivial
  ```

- **Ticket prefix:**
  ```
  - Prefix every commit with the ticket ID: PROJ-123: description
  - Keep subject line under 72 characters
  - Reference the ticket for context rather than repeating it in the body
  ```

- **Freeform:**
  ```
  - Write clear, descriptive commit messages
  - Start with a verb in imperative mood (Add, Fix, Update, Remove)
  - Keep subject line under 72 characters
  ```

---

## Q6. Code Quality Bar

**Question:** What level of code quality do you target?

**Purpose:** Calibrates how thorough the agent is with edge cases, documentation, and defensive coding.

| Option | Description |
|---|---|
| Staff engineer rigor | Exhaustive edge cases, defensive coding, thorough documentation, consider concurrency |
| Senior pragmatic | Solid quality with practical trade-offs — handle likely edge cases, document non-obvious decisions |
| Ship fast | Working code with minimal ceremony — get it done, iterate later |

**Generated rules by answer:**

- **Staff engineer rigor:**
  ```
  - Handle all edge cases including unlikely ones
  - Add defensive checks at boundaries
  - Document every non-trivial decision
  - Consider concurrency, race conditions, and failure modes
  - Never mark done without proving it works (tests, manual verification, or both)
  ```

- **Senior pragmatic:**
  ```
  - Write clean, well-structured code with practical trade-offs
  - Handle edge cases that are likely to occur in production
  - Document non-obvious decisions with brief inline comments
  - Never mark done without proving it works
  ```

- **Ship fast:**
  ```
  - Focus on working code that solves the immediate problem
  - Handle obvious error cases, skip unlikely edge cases
  - Minimal comments — code should be self-explanatory
  - Verify the happy path works before moving on
  ```

---

## Q7. Autonomy Level

**Question:** How much should the agent do without asking?

**Purpose:** Controls the agent's freedom to make decisions and take actions independently.

| Option | Description |
|---|---|
| Autonomous | Fix bugs, lint errors, failing CI, and minor issues without asking |
| Semi-autonomous | Act freely for safe operations, ask before destructive or risky actions |
| Conservative | Confirm everything — every file change, every command, every decision |

**Generated rules by answer:**

- **Autonomous:**
  ```
  - Fix lint errors, type errors, and failing tests without asking
  - Fix minor bugs discovered during implementation without asking
  - Only ask for: architectural decisions, scope changes, or ambiguous requirements
  ```

- **Semi-autonomous:**
  ```
  - Fix lint errors, type errors, and failing tests without asking
  - Ask before: force-pushing, deleting branches, modifying CI/CD, running destructive commands
  - Ask before making architectural changes not covered by the current task
  ```

- **Conservative:**
  ```
  - Confirm before modifying any file
  - Confirm before running any command with side effects
  - Present options and wait for explicit approval before proceeding
  ```

---

## Q8. Task Tracking

**Question:** How do you want to track tasks during a session?

**Purpose:** Determines whether to maintain a todo file, use built-in tracking, or skip formal tracking.

| Option | Description |
|---|---|
| Todo files | Maintain a `TODO.md` or similar file in the project |
| Built-in tasks | Use the agent's built-in task/todo system (if available) |
| No formal tracking | Work through tasks naturally without formal tracking |

**Generated rules by answer:**

- **Todo files:**
  ```
  - Maintain a TODO.md file at the project root
  - Update it at the start and end of each task
  - Mark completed items, add new items as discovered
  ```

- **Built-in tasks:**
  ```
  - Use the built-in task tracking for multi-step work
  - Create tasks for each distinct step before starting
  - Mark tasks complete as you finish them
  ```

- **No formal tracking:**
  ```
  - Work through tasks naturally
  - Summarize completed work at the end of each session
  ```

---

## Q9. Self-Improvement

**Question:** Should the agent maintain a lessons-learned file?

**Purpose:** Controls whether the agent tracks corrections and mistakes for future reference.

| Option | Description |
|---|---|
| Lessons file | Maintain a lessons-learned file, update after every correction or mistake |
| No formal tracking | Learn implicitly from conversation context, no persistent file |

**Generated rules by answer:**

- **Lessons file:**
  ```
  - After any correction or mistake, update the lessons-learned file
  - Review lessons file at the start of each session
  - Organize lessons by category (debugging, architecture, testing, etc.)
  ```

- **No formal tracking:**
  (No rules generated for this section.)
