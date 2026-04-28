---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans Recipe

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## The 6-Step Process

### Step 1: Scope Check
If the spec covers multiple independent subsystems, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

### Step 2: File Structure Mapping
Map out which files will be created or modified:

- Design units with clear boundaries and well-defined interfaces
- Each file should have one clear responsibility
- Prefer smaller, focused files over large ones
- Files that change together should live together
- Follow established patterns in existing codebases

This structure informs the task decomposition.

### Step 3: Bite-Sized Task Granularity
Break work into steps that take 2-5 minutes each:

- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

### Step 4: Plan Document Header
Every plan MUST start with this header:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Step 5: Define Tasks
For each component, create a task with this structure:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

### Step 6: Self-Review
After writing the complete plan, check:

**1. Spec Coverage:**
- Skim each section/requirement in the spec
- Can you point to a task that implements it?
- List any gaps

**2. Placeholder Scan:**
- Search for red flags:
  - "TBD", "TODO", "implement later", "fill in details"
  - "Add appropriate error handling" / "add validation" / "handle edge cases"
  - "Write tests for the above" (without actual test code)
  - "Similar to Task N" (repeat the code)
  - Steps that describe what to do without showing how (code blocks required)
  - References to types, functions, or methods not defined in any task

**3. Type Consistency:**
- Do the types, method signatures, and property names match across tasks?
- A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug

Fix any issues inline.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:"**

**1. Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration
   - **REQUIRED SUB-SKILL:** Use `superpowers:subagent-driven-development`

**2. Inline Execution** - Execute tasks in this session, batch execution with checkpoints
   - **REQUIRED SUB-SKILL:** Use `superpowers:executing-plans`

**"Which approach?"**

## Critical Rules

### NO PLACEHOLDERS (Plan Failures):
Never write these:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code)
- Steps that describe what to do without showing how (code blocks required)
- References to types, functions, or methods not defined in any task

### Must Have:
- Exact file paths always
- Complete code in every step
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Key Principles

- **Granularity:** Each step is one action (2-5 minutes)
- **Specificity:** No placeholders, no assumptions
- **Completeness:** Every step must contain the actual content needed
- **Clarity:** The engineer has zero context and questionable taste
