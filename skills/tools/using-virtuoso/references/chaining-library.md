# Chaining Library

Named multi-step chains. Use when a single skill or agent is not enough. Each chain lists what it produces, when to use it, and when to skip it.

## Investigation Flow

```
investigator → architect → implementer → reviewer
```

**When:** Changing code in an unfamiliar area. You need to understand before you change.

**Produces:** Mapped code area, design decision, implemented change, reviewed diff.

**Skip if:** You already know the area well — jump straight to `implementer`.

**Watch out for:** Giving the investigator a goal instead of a question. Investigators map; architects decide.

---

## Feature Flow

```
product-manager → architect → backend-dev / frontend-dev → qa-engineer
```

**When:** Building a new feature from scratch with acceptance criteria.

**Produces:** PRD, component design and API contract, implementation in a worktree, test plan and sign-off.

**Skip if:** The feature is trivial (obvious spec, single file) — go direct to a dev role agent.

**Watch out for:** Letting the dev role negotiate scope. Scope belongs to the product manager. If a dev role thinks the spec is wrong, it must escalate back to the product manager, not rewrite silently.

---

## Review Flow

```
refactor-scout → reviewer → implementer
```

**When:** Improving code health in a module without a specific bug in mind.

**Produces:** Smell inventory, validated findings with priority, applied refactorings with TDD.

**Skip if:** The refactoring is a one-liner — just do it.

**Watch out for:** Refactor scouts can be noisy. Let the reviewer filter the list to what actually matters before handing to the implementer.

---

## Pre-Migration Flow

```
migration-planner → reviewer → implementer
```

**When:** Non-trivial schema change, framework upgrade, or data transformation.

**Produces:** Risk-classified migration plan, compatibility review of application code, implementation of both migration and any code changes.

**Skip if:** The migration is a mechanical additive change (new nullable column, new table) with no code touching it.

**Watch out for:** Forward-only migrations without a rollback path. The migration planner must surface the rollback; do not accept a plan that handwaves it.

---

## Coverage Improvement Flow

```
test-gap-analyzer → implementer → reviewer
```

**When:** Raising coverage in a specific module before a refactor or release.

**Produces:** Prioritized list of missing tests, written tests with TDD, reviewed tests.

**Skip if:** You are raising coverage for its own sake — that rarely pays. Target a module you are about to change.

**Watch out for:** Tests written to hit lines, not behaviors. The reviewer must check that each test asserts meaningful behavior.

---

## Idea-to-Ship Flow

```
brainstorming → writing-plans → subagent-driven-development → finishing-branch
```

**When:** The user walks in with a vague idea and wants to ship something.

**Produces:** Approved spec, ordered plan, implementation task-by-task with review gates, finished branch ready to merge.

**Skip if:** The idea is already specced — jump in at `writing-plans` or later.

**Watch out for:** Skipping the approval gate in brainstorming. Without it, the plan can drift from the idea before a line of code is written.

---

## Parallel-Research Flow

```
orchestrator (dispatch fan-out) → [investigator × N in parallel] → synthesis
```

**When:** A single investigation would be slow because it spans multiple independent areas.

**Produces:** Parallel research results from each investigator, synthesized into one report.

**Skip if:** The investigations are not truly independent. Sequential dependencies kill parallel speedup.

**Watch out for:** Duplicate work. Define crisp, non-overlapping scopes per investigator in the brief. See `dispatching-parallel-agents` for decomposition patterns.

---

## Pre-PR Flow

```
verification-before-completion → finishing-branch → pr-message-writer
```

**When:** You think you are done and want to push.

**Produces:** Verified evidence that tests and lints pass, clean branch finishing procedure, well-structured PR message.

**Skip if:** The change is a documentation-only edit — verification is lighter.

**Watch out for:** Claiming done before verification. Every phase in this chain exists because someone once shipped a broken thing.

---

## Chain Principles

| Principle | Why |
|---|---|
| **Skip what does not apply** | Chains are guidelines, not rituals |
| **Do not let scope expand mid-chain** | Finish the task; file follow-ups for discovered issues |
| **Escalate across chain boundaries** | If an implementer finds an architectural problem, it escalates back to the architect, not forward to the reviewer |
| **One agent per step** | Do not combine roles — a reviewer that also implements is a reviewer with a conflict of interest |
| **Name your chain** | Before dispatching, say which chain you are running. It keeps you honest about which step you are on |
