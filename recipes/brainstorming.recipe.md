---
name: brainstorming
description: Use when you have a rough idea but need design refinement before implementation
---

# Brainstorming Recipe

**Announce at start:** "I'm using the brainstorming skill to refine this idea."

**Goal:** Refine rough ideas through Socratic questions, explore alternatives, present design in sections for validation, and produce a spec ready for implementation planning.

**Required sub-skills:**
- `superpowers:writing-plans` (after spec is approved)

## The 9-Step Process

### Step 1: Explore Context
Ask about:
- What problem are we solving?
- Why is this important?
- Who benefits? How?
- What are the constraints?
- What's the deadline?
- Are there existing solutions or patterns?

### Step 2: Offer Visual Companion
If helpful, draw or describe:
- System architecture
- User flow
- Data flow
- Component relationships

### Step 3: Ask Questions
Use Socratic questioning to clarify:
- What happens at the boundaries?
- What are the failure modes?
- What assumptions are we making?
- What are the non-goals?
- What would failure look like?

### Step 4: Propose Approaches
Offer 2-3 different approaches:
- **Option A:** Simple, direct solution
- **Option B:** Modular, extensible solution
- **Option C:** Hybrid approach

For each option:
- What are the trade-offs?
- What are the advantages?
- What are the disadvantages?
- What tools/technologies would be involved?

### Step 5: Present Design for Validation
Break design into logical sections for review:
- Core architecture
- Key decisions
- Component responsibilities
- Interfaces between components
- Error handling strategy
- Testing approach

Present sections one at a time. For each section:
- State what this does
- Why this approach
- Alternatives considered
- Trade-offs

Wait for approval before moving to next section.

### Step 6: Write Spec Document
Save spec to: `docs/superpowers/specs/YYYY-MM-DD-<feature-name>.md`

Spec must include:
- **Goal:** One sentence describing what this builds
- **Architecture:** 2-3 sentences about approach
- **Tech Stack:** Key technologies/libraries
- **Requirements:** Detailed list of behaviors
- **Non-requirements:** What this doesn't do
- **Assumptions:** What we're assuming
- **Constraints:** Limitations we must work within
- **Error Handling:** How errors are managed
- **Testing Strategy:** How we verify it works

### Step 7: Self-Review
Before presenting to user, check:
- Does the spec cover all the requirements?
- Are there contradictions?
- Are assumptions documented?
- Is the scope too broad? (should have been broken into sub-projects)
- Is the scope too narrow? (missing key behaviors)

### Step 8: User Review
Present spec to user with:
- Clear summary of what we're building
- High-level approach
- Key decisions
- Options that were considered but rejected
- Estimated complexity

Ask for:
- Approval of spec
- Changes or additions needed
- Confirmation to proceed to implementation planning

### Step 9: Transition to Plans
After spec approval, offer:

**"Spec complete and saved to `docs/superpowers/specs/<filename>.md`. Ready to create implementation plan?"**

If yes, use `superpowers:writing-plans` skill.

If no, return to Step 3 (more questions) or Step 5 (design refinement).

## When to Use

Use brainstorming when:
- You have a rough idea but unclear details
- Multiple implementation approaches are possible
- The problem has multiple stakeholders or requirements
- You need to explore trade-offs before committing
- The scope is complex enough to benefit from planning

## When NOT to Use

Skip brainstorming when:
- Requirements are already complete and detailed
- You're fixing a bug (use systematic-debugging + TDD)
- You're making small, obvious improvements
- The solution is straightforward and uncontroversial

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Skipping questions | Ask until you can't think of more questions |
| Presenting too much at once | Break into logical sections |
| Rushing to implementation | Stop and validate spec before plans |
| Not documenting trade-offs | Explicitly list alternatives and why they were rejected |
| Letting user make all decisions | Guide with options, don't present blank canvas |

## Example Dialogue

**User:** "I want to build a user authentication system."

**You:** "I'm using the brainstorming skill to refine this idea. Let me ask some questions to understand what we're building..."

Continue through all 9 steps, documenting in the spec as you go.

## Key Principles

- **YAGNI:** Don't build features that aren't required
- **Incremental validation:** Don't build a complete design before validation
- **Specific over vague:** Replace "database" with "PostgreSQL for user accounts, Redis for sessions"
- **Trade-off awareness:** Every decision has costs, make them explicit
