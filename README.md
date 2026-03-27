# GAN Artifact Generator

**Adversarial refinement engine for producing high-quality LLM-generated artifacts.**

An open-source system that applies Generative Adversarial Network (GAN) principles to LLM artifact generation — using a Generator → Discriminator → Arbiter loop to iteratively refine PRDs, code, architecture docs, and security assessments to a configurable quality bar.

## How It Works

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

### Three Agents, Isolated Contexts

| Agent | Role | Sees | Does NOT See |
|-------|------|------|-------------|
| **Generator** | Produces/refines the artifact | Task spec + Discriminator feedback (iter 2+) | Rubric, scoring criteria, Discriminator reasoning |
| **Discriminator** | Evaluates against weighted rubric | Artifact + rubric only | Generator prompt, reasoning, task framing |
| **Arbiter** | Decides: converge, iterate, or exit | Both outputs, score history | Orchestrates the loop |

**Context isolation is critical.** Each agent runs in a fresh, stateless context (separate subagent call / API call / thread). The Discriminator can't be lenient because it never saw the Generator's reasoning. The Generator can't game the rubric because it only sees feedback, not scoring criteria.

### Convergence Strategies

The system uses three convergence strategies (configurable per run):

1. **Score Threshold** (default ≥ 8.0/10) — converge when weighted average meets the bar
2. **Delta-Based Early Exit** — stop when improvement < 5% between iterations (diminishing returns)
3. **Best-of-N Fallback** — if max iterations hit without convergence, select the highest-scoring version

**Hard gates** prevent critical dimensions (e.g., Security, Bug Threshold) from being masked by high scores elsewhere. A hard-gate failure blocks convergence regardless of weighted average.

## Empirical Results (8 Tests, 6 Artifact Types)

Tested across PRDs, code (TypeScript, Python, Go), architecture docs, product plans, and security assessments:

| Metric | Value |
|--------|-------|
| **GAN win rate** | **87.5%** (7/8 tests) |
| **Mean score improvement** | **+3.3 points** (5.0 → 8.3 on 10-point scale) |
| **One-shot hard-gate failure rate** | **75%** (6/8 failed production-readiness gates) |
| **GAN hard-gate pass rate** | **100%** (8/8) |
| **Mean iterations to converge** | **1.9** |
| **Ties (GAN = one-shot)** | 1/8 (product plans — LLMs already produce good plans) |

### Per-Dimension Improvement

| Dimension | One-Shot | GAN | Improvement |
|-----------|----------|-----|-------------|
| Test Coverage | 4.0 | 8.6 | **+4.6** |
| Logic / Bug Threshold | 4.6 | 8.8 | **+4.3** |
| Security | 4.3 | 8.4 | **+4.2** |
| Compliance | 4.0 | 8.0 | **+4.0** |
| Ease of Use | 5.4 | 8.5 | **+3.1** |
| Document Quality | 5.8 | 8.9 | **+3.1** |
| Scalability | 5.1 | 8.0 | **+2.9** |
| Performance | 5.8 | 7.8 | **+2.0** |

### Real Bugs Found by the Discriminator

| Test | Defect | Severity |
|------|--------|----------|
| TypeScript validation lib | `maxLength` truncation corrupts HTML entities (`&lt;l`) | Data corruption |
| Python rate limiter | PEXPIRE missing on Redis reject path | Memory leak |
| Python rate limiter | Sync `check()` in async middleware | Event loop blocking |
| Go CLI tool | Docker/K8s names passed raw to `exec.Command` | **Remote code execution** |
| Architecture doc | Service subscriptions say choreography, saga says orchestration | Fatal contradiction |
| Healthcare security assessment | 3 subprocessors missing BAAs | HIPAA violation |

## Token Cost & ROI

| Metric | Value |
|--------|-------|
| One-shot cost | ~$0.15-0.30 per artifact |
| GAN loop cost | ~$0.65-1.30 per artifact |
| Additional spend | ~$0.50-1.00 |
| Human review time saved | ~2-4 hours per artifact |
| **Effective ROI** | **~$200 saved per $1 spent** |

The +3.3 point improvement moves artifacts from "needs significant rework" (score 5.0, ~2-4 hrs editing) to "ship-ready with light review" (score 8.3, ~15-30 min polish).

## When to Use (and When Not To)

| Artifact Type | Recommendation | Expected Improvement |
|--------------|----------------|---------------------|
| Architecture docs | **Full GAN loop** | +4.8 pts (highest) |
| Security-critical code | **Full GAN loop** | +4.8 pts |
| PRDs / Specs | **Full GAN loop** | +3.8 pts |
| Security assessments | **Full GAN loop** (regulated profile) | +2.9 pts |
| General code | Single Discriminator review pass | +2-3 pts |
| Product / launch plans | **One-shot only** | +0.0 pts (no benefit) |
| Prototype code | Supercharged prompt only | N/A |

## Installation

### GitHub Copilot (VS Code)

```bash
# Copy to user-level skills directory
cp -r platforms/copilot-vscode/* ~/.copilot/skills/gan-refinement/

# Or workspace-level
cp -r platforms/copilot-vscode/* .copilot/skills/gan-refinement/
```

Copilot will auto-discover the skill. Trigger with: "refine this", "GAN loop", "iterate until perfect", or any artifact generation request.

### Claude Desktop / Claude Code

```bash
# Copy the Claude-specific prompt files
cp platforms/claude/* ~/claude-projects/gan-refinement/
```

See [platforms/claude/README.md](platforms/claude/README.md) for setup instructions.

### ChatGPT (Custom GPT / Projects)

```bash
# Upload the knowledge files to your Custom GPT or ChatGPT Project
# See platforms/chatgpt/README.md for detailed steps
```

### API / CLI (Any LLM)

```bash
# Use the standalone orchestration script
cd platforms/api-cli/
npm install  # or pip install -r requirements.txt
node gan-orchestrator.js --task "Write a PRD for..." --profile prd-default
```

See [platforms/api-cli/README.md](platforms/api-cli/README.md) for full API configuration.

## Project Structure

```
GAN-Artefact-Generator/
├── SKILL.md                    # Core skill definition (architecture, loop logic)
├── priorities.md               # 8 priority dimensions with scoring criteria
├── convergence.md              # 3 convergence strategies
├── prd-rubric.md               # PRD-specific Discriminator rubric
├── code-rubric.md              # Code-specific Discriminator rubric
├── discriminator-prompt.md     # Discriminator prompt template
├── progress-report.md          # Iteration reporting templates
├── platforms/
│   ├── copilot-vscode/         # GitHub Copilot (VS Code) integration
│   ├── claude/                 # Claude Desktop / Claude Code
│   ├── chatgpt/                # ChatGPT Custom GPT / Projects
│   └── api-cli/                # Standalone API orchestration
├── test-archive/               # Test artifacts from validation rounds
│   ├── round1/                 # PRD + Code tests
│   ├── round2/                 # Architecture + Plan + Go + Security tests
│   └── codeclue-refinement/    # Real-world PRD refinement example
└── docs/
    └── SETUP.md                # Detailed setup guide
```

## Rubric Profiles

Four built-in profiles (all configurable):

| Profile | Best For | Hard Gates |
|---------|----------|------------|
| **PRD Default** | Product documents, specs | Logical Consistency |
| **Production Code** | Ship-ready code | Security, Bug Threshold |
| **MVP / Prototype** | Quick iterations | None |
| **Enterprise / Regulated** | HIPAA, PCI, SOC 2 | Security, Compliance, Logic, Test Coverage |

Custom profiles: `"security=5, compliance=4, performance=2"` or `"use production profile but bump test coverage to 5"`

## License

MIT License — see [LICENSE](LICENSE).

## Prior Art & References

- **Constitutional AI** (Anthropic, 2022) — AI feedback for alignment
- **Self-Refine** (Madaan et al., CMU, 2023) — iterative self-refinement for LLMs
- **Reflexion** (Shinn et al., 2023) — agent self-improvement
- **PromptBreeder** (Google DeepMind, 2023) — evolutionary prompt optimization
