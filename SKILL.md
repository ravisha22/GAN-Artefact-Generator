---
name: gan-refinement
description: >
  Iterative adversarial refinement skill that uses a Generator-Discriminator loop to produce
  high-quality outputs. The Generator creates or refines artifacts (PRDs, code, strategies,
  documents) and the Discriminator evaluates them against configurable priority rubrics
  (security, compliance, code quality, bug threshold, ease of use, etc.), providing scored
  feedback until convergence. Use this skill whenever: the user wants to iteratively refine
  any artifact to a high quality bar; the user says "make this perfect", "refine this",
  "iterate until good", "GAN loop", "adversarial refinement"; the user wants a PRD, code,
  or document that meets specific quality thresholds; the user provides an outcome and wants
  the skill to iterate toward it. Trigger even when the user simply provides an outcome
  description and expects polished output — this skill IS the iteration engine.
---

# GAN Refinement Skill

An adversarial refinement engine that iterates artifacts toward a defined quality bar using
a Generator → Discriminator → Feedback loop, inspired by Generative Adversarial Networks.

## Architecture Overview

```
┌─────────────┐     artifact      ┌───────────────┐
│  GENERATOR   │ ───────────────→ │ DISCRIMINATOR  │
│  (Creator)   │                  │  (Evaluator)   │
│              │ ←─────────────── │                │
└─────────────┘   scored feedback └───────────────┘
       ↑                                  │
       │          convergence?            │
       │         ┌──────────┐             │
       └─────────│ ARBITER  │←────────────┘
                 └──────────┘
                   ↓ YES
              FINAL OUTPUT
```

**Three agents:**
1. **Generator** — Produces or refines the artifact based on the outcome spec and discriminator feedback
2. **Discriminator** — Evaluates the artifact against weighted priority rubrics, returns structured scores and actionable feedback
3. **Arbiter** — Decides whether to converge (accept), iterate, or select best-of-N

## When to Use

- User provides a desired outcome and wants iterative refinement to reach it
- User explicitly requests "GAN", "adversarial refinement", or "iterate until perfect"
- User wants a PRD, code module, strategy doc, or any artifact held to a quality bar
- User says "make this production-ready" or "refine this"

## Quick Start

When triggered, follow this sequence:

### Step 0: Parse the Outcome Spec

Extract from the user's request:
1. **Artifact type** — What are we producing? (PRD, code, architecture doc, etc.)
2. **Outcome definition** — What does "done" look like?
3. **Priority configuration** — Which discriminator priorities matter? (read `references/priorities.md`)
4. **Convergence strategy** — How do we know when to stop? (default: score threshold ≥ 8/10)

If any of these are ambiguous, ask the user before starting the loop. Do NOT assume.

### Step 1: Configure the Discriminator

Load the appropriate rubric from `references/priorities.md`. The user can specify priorities
in one of three ways:

**Explicit list:** "Priorities: security > compliance > code quality"
**Preset profile:** "Use the production-code profile"
**Default:** If unspecified, use the artifact-type default from `references/priorities.md`

Build the discriminator prompt using the weighted rubric. Each priority gets:
- A weight (1-5, where 5 = hard gate / deal-breaker)
- Scoring criteria (what constitutes a 1 vs 5 vs 10)
- Pass/fail threshold per dimension

### Step 2: Configure Convergence

Read `references/convergence.md` for full details. Three strategies are available, all
configurable per run:

| Strategy | Default | When to Use |
|---|---|---|
| **Score threshold** | ≥ 8/10 weighted average | Standard quality bar |
| **Delta-based** | Stop when improvement < 5% | Diminishing returns detection |
| **Best-of-N** | Select highest-scoring from N iterations | When score threshold isn't reached by max iterations |

**Default configuration:**
- Max iterations: **3**
- Primary strategy: **Score threshold** (≥ 8/10)
- Fallback strategy: **Best-of-N** (if threshold not met by max iterations)
- Delta exit: **enabled** (stop early if improvement < 5% between iterations)

### Step 3: Run the Loop

#### Iteration Flow

```
FOR iteration = 1 to max_iterations:

  1. GENERATOR produces/refines artifact
     - iteration 1: generate from outcome spec
     - iteration 2+: incorporate discriminator feedback from previous iteration

  2. DISCRIMINATOR evaluates artifact
     - Score each priority dimension (1-10)
     - Calculate weighted average
     - Identify top 3 specific issues with fix recommendations
     - Flag any hard-gate failures (weight-5 priorities scoring < 6)

  3. ARBITER checks convergence
     - IF weighted_avg ≥ threshold → CONVERGE, output final artifact
     - IF hard_gate_failure → MUST iterate (override other convergence)
     - IF delta < 5% from previous → EARLY EXIT, select best-of-N
     - IF iteration = max → select best-of-N from all iterations
     - ELSE → feed discriminator report to generator, continue
```

#### Hybrid Execution Strategy

**Pass 1 (inline, no API cost):**
- Generator and Discriminator both run in the current context
- If the discriminator scores ≥ threshold on pass 1 → output immediately
- This handles ~70% of cases for experienced users providing clear specs

**Pass 2+ (API calls if available, otherwise continued inline):**
- If API calls are available (Claude-in-Claude / Anthropic API):
  - Each iteration gets a CLEAN context window (no drift)
  - Generator receives: outcome spec + latest discriminator feedback only
  - Discriminator receives: artifact + rubric only (no generator history)
- If API calls are NOT available (VS Code / Copilot):
  - Continue inline but use structured XML blocks to separate concerns
  - Compress previous iterations to just: score + top 3 issues + resolution status

#### Progress Reporting

After each iteration, output a structured progress block:

```
## Iteration [N] of [max]
| Priority | Score | Δ from prev | Status |
|---|---|---|---|
| Security | 8/10 | +2 | ✅ Pass |
| Code Quality | 6/10 | +1 | ⚠️ Below threshold |
| ... | | | |

**Weighted Average:** 7.2/10 (threshold: 8.0)
**Decision:** ITERATE — 2 issues remaining
**Top Issues:**
1. [Issue] → [Recommended fix]
2. [Issue] → [Recommended fix]
```

### Step 4: Output Final Artifact

When converged, output:
1. The final artifact (full content)
2. A convergence summary:
   - Total iterations used
   - Final scores per dimension
   - Key improvements made across iterations
   - Any residual risks or trade-offs accepted

## Domain-Specific Behavior

### PRD Mode

When the artifact type is a PRD or product document:
- Read `references/prd-rubric.md` for the PRD-specific discriminator rubric
- Generator writes in PM voice (problem-first, outcome-oriented, measurable)
- Discriminator checks: problem clarity, user story completeness, success metrics
  measurability, scope definition, edge case coverage, technical feasibility signals
- Hard gates: missing success metrics, undefined user personas, no scope boundaries

### Code Mode

When the artifact type is code:
- Read `references/code-rubric.md` for the code-specific discriminator rubric
- Generator produces functional code with tests
- Discriminator checks: correctness, security, performance, readability, test coverage,
  error handling, dependency hygiene
- Hard gates: known security vulnerabilities, no error handling, missing input validation
- **Bonus agent (Code mode only):** If bash/terminal is available, the Arbiter can run
  linting, type checking, or test execution as OBJECTIVE signal alongside the
  Discriminator's LLM-based evaluation

## Configuration Reference

All defaults are overridable per run. The user can say:
- "Max 5 iterations" → overrides max_iterations
- "Threshold 9/10" → overrides score_threshold
- "Priorities: security=5, performance=4, readability=3" → overrides rubric weights
- "Skip delta check" → disables delta-based early exit
- "Code profile" → loads code preset from priorities.md

### Full Parameter Table

| Parameter | Default | Range | Description |
|---|---|---|---|
| max_iterations | 3 | 1-7 | Hard ceiling on iteration count |
| score_threshold | 8.0 | 1.0-10.0 | Weighted average to converge |
| delta_threshold | 0.05 | 0.01-0.20 | Min improvement to continue |
| delta_enabled | true | true/false | Enable delta-based early exit |
| best_of_n | true | true/false | Select best if threshold not met |
| execution_mode | hybrid | inline/api/hybrid | How to run the loop |
| progress_display | verbose | verbose/compact/silent | Iteration reporting detail |

## Anti-Patterns and Safeguards

### Mode Collapse Prevention
The Discriminator must vary its evaluation emphasis across iterations. If the same issue
persists for 2+ iterations, the Discriminator should:
1. Escalate its severity weight
2. Provide a MORE SPECIFIC fix recommendation (not just repeat the feedback)
3. If the Generator still can't fix it, flag it as a residual risk in the final output

### Oscillation Detection
If the Generator's score oscillates (goes up then down then up), the Arbiter should:
1. Detect the oscillation pattern
2. Lock in the highest-scoring version
3. Only allow changes that don't regress on previously-passing dimensions

### Context Window Management (Inline Mode)
When running inline without API calls:
- Compress each completed iteration to ~200 tokens (score table + top issues only)
- Never carry forward the full artifact from previous iterations
- Only carry forward: latest artifact + compressed feedback history
- If context is running low, force-converge with best-of-N

## Reference Files

Read these files for detailed rubrics and configuration:

| File | When to Read |
|---|---|
| `references/priorities.md` | Always — contains all priority definitions and presets |
| `references/convergence.md` | When configuring convergence strategy |
| `references/prd-rubric.md` | When artifact type is PRD or product document |
| `references/code-rubric.md` | When artifact type is code |
| `templates/discriminator-prompt.md` | Template for constructing the discriminator evaluation prompt |
| `templates/progress-report.md` | Template for iteration progress reporting |
