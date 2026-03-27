# Setup Guide

## Quick Start (GitHub Copilot in VS Code)

### 1. Clone the repo

```bash
git clone https://github.com/ravisha22/GAN-Artefact-Generator.git
```

### 2. Install the skill

**User-level** (available in all workspaces):
```bash
mkdir -p ~/.copilot/skills/gan-refinement
cp SKILL.md priorities.md convergence.md prd-rubric.md code-rubric.md discriminator-prompt.md progress-report.md ~/.copilot/skills/gan-refinement/
```

**Or workspace-level** (one project):
```bash
mkdir -p .copilot/skills/gan-refinement
cp SKILL.md priorities.md convergence.md prd-rubric.md code-rubric.md discriminator-prompt.md progress-report.md .copilot/skills/gan-refinement/
```

### 3. Use it

In VS Code Copilot Chat, say any of:
- "Write a PRD for [description] and refine it"
- "GAN loop on this code"
- "Make this production-ready"
- "Iterate until perfect"

Copilot will automatically discover and use the GAN refinement skill.

---

## Platform-Specific Setup

| Platform | Setup Guide | Context Isolation |
|----------|-----------|-------------------|
| GitHub Copilot (VS Code) | [platforms/copilot-vscode/README.md](platforms/copilot-vscode/README.md) | Full (subagents) |
| Claude Code | [platforms/claude/README.md](platforms/claude/README.md) | Full (Task tool) |
| Claude Desktop | [platforms/claude/README.md](platforms/claude/README.md) | Partial (inline XML) |
| ChatGPT (Custom GPT) | [platforms/chatgpt/README.md](platforms/chatgpt/README.md) | Partial (inline XML) |
| API / CLI | [platforms/api-cli/README.md](platforms/api-cli/README.md) | Full (isolated HTTP calls) |

---

## Configuration

### Rubric Profiles

The system ships with 4 profiles. Tell the system which to use:

| Profile | When to Use |
|---------|------------|
| `prd-default` | PRDs, specs, product documents |
| `production-code` | Code that will ship to production |
| `mvp` | Prototypes, quick iterations |
| `enterprise` | HIPAA, PCI DSS, SOC 2 compliance-required artifacts |

### Custom Overrides

Override any profile setting in natural language:
- "Use production profile but set compliance to 5 (hard gate)"
- "Security=5, performance=1, test coverage=5"
- "Threshold 9.5, max 5 iterations"

### Convergence Settings

| Setting | Default | What It Does |
|---------|---------|-------------|
| `max_iterations` | 3 | Hard ceiling on refinement passes |
| `score_threshold` | 8.0 | Minimum weighted average to converge |
| `delta_threshold` | 0.05 | Stop if improvement < 5% between iterations |

---

## File Reference

| File | Purpose | When It's Used |
|------|---------|---------------|
| `SKILL.md` | Architecture, loop logic, configuration | Always — entry point |
| `priorities.md` | 8 dimensions with scoring criteria | Always — defines the rubric |
| `convergence.md` | 3 convergence strategies | Always — exit conditions |
| `prd-rubric.md` | PRD-specific evaluation | When artifact is a document |
| `code-rubric.md` | Code-specific evaluation | When artifact is code |
| `discriminator-prompt.md` | Discriminator prompt template | Every Discriminator invocation |
| `progress-report.md` | Iteration reporting format | Every iteration |

---

## Troubleshooting

### "The skill isn't activating"
- Verify files are in `~/.copilot/skills/gan-refinement/` or `.copilot/skills/gan-refinement/`
- Check that `SKILL.md` has the correct YAML frontmatter with `name` and `description`
- Try explicit trigger: "Use the gan-refinement skill to..."

### "Scores seem inflated"
- The Discriminator may be sharing context with the Generator (inline mode)
- For best results, use a platform with subagent/subtask support (Copilot, Claude Code)
- Increase the threshold to 9.0 for stricter evaluation

### "Convergence takes too many iterations"
- Lower the threshold (7.0 for drafts, 8.0 for production)
- Use the MVP profile for less critical artifacts
- Check if the task is too ambiguous — provide more specific requirements
