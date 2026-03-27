# GitHub Copilot (VS Code) Integration

> **Status: TESTED** — Extensively validated across 8 tests (2 rounds), 6 artifact types. 87.5% win rate over one-shot, +3.3 mean quality improvement.

This folder contains the GAN Refinement skill packaged for GitHub Copilot in VS Code.

## Installation

### User-Level (available in all workspaces)

```bash
mkdir -p ~/.copilot/skills/gan-refinement
cp SKILL.md priorities.md convergence.md prd-rubric.md code-rubric.md discriminator-prompt.md progress-report.md ~/.copilot/skills/gan-refinement/
```

### Workspace-Level (available in one project)

```bash
mkdir -p .copilot/skills/gan-refinement
cp SKILL.md priorities.md convergence.md prd-rubric.md code-rubric.md discriminator-prompt.md progress-report.md .copilot/skills/gan-refinement/
```

## How It Works

Copilot auto-discovers the skill via the SKILL.md frontmatter `description` field. When you say any of these triggers, the skill activates:

- "refine this PRD"
- "iterate until perfect"
- "GAN loop on this code"
- "adversarial refinement"
- "make this production-ready"

## Context Isolation

The skill uses Copilot's `runSubagent` mechanism for context isolation:
- Generator runs as a subagent (fresh context, no rubric knowledge)
- Discriminator runs as a subagent (fresh context, no Generator history)
- Arbiter runs in the main thread (orchestrates, checks convergence)

Each subagent invocation is stateless — the Discriminator literally cannot see the Generator's reasoning.

## Configuration

Override defaults by telling Copilot:
- "Max 5 iterations"
- "Threshold 9/10"
- "Priorities: security=5, compliance=4"
- "Use enterprise profile"
- "Skip delta check"

## Files

All 7 files from the repo root are the skill files:
- `SKILL.md` — Main skill definition
- `priorities.md` — Priority dimensions and scoring criteria
- `convergence.md` — Convergence strategies
- `prd-rubric.md` — PRD-specific evaluation rubric
- `code-rubric.md` — Code-specific evaluation rubric
- `discriminator-prompt.md` — Discriminator prompt template
- `progress-report.md` — Iteration progress report templates
