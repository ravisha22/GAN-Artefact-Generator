# API / CLI Orchestration

This folder contains a standalone orchestration approach for running the GAN refinement loop via any OpenAI-compatible API (Azure OpenAI, OpenAI, Anthropic, local models).

## How It Works

The orchestrator script makes isolated API calls:
1. **Generator call** — fresh conversation, task spec only
2. **Discriminator call** — fresh conversation, artifact + rubric only
3. **Arbiter logic** — local code, parses scores, checks convergence
4. Repeat or output final artifact

Each API call is a new conversation with no shared history — full context isolation.

## Setup

### Prerequisites

- Node.js 18+ or Python 3.10+
- An API key for your LLM provider

### Environment Variables

```bash
# For OpenAI / Azure OpenAI
export GAN_API_KEY="sk-..."
export GAN_API_BASE="https://api.openai.com/v1"  # or your Azure endpoint
export GAN_MODEL="gpt-4o"

# For Anthropic
export GAN_API_KEY="sk-ant-..."
export GAN_API_BASE="https://api.anthropic.com"
export GAN_MODEL="claude-sonnet-4-20250514"
export GAN_PROVIDER="anthropic"  # default is "openai"
```

### Configuration

Copy `gan-config.example.yaml` to `gan-config.yaml` and customize:

```yaml
provider: openai  # or anthropic
model: gpt-4o
max_iterations: 3
score_threshold: 8.0
delta_threshold: 0.05
profile: prd-default  # or production-code, mvp, enterprise
rubric_dir: ../../  # path to rubric .md files
```

## Usage

```bash
# Generate and refine a PRD
node gan-orchestrator.js --task "Write a PRD for a rate limiting middleware" --profile prd-default

# Refine an existing artifact
node gan-orchestrator.js --input my-prd.md --profile prd-default --threshold 9.0

# Code generation with production profile
node gan-orchestrator.js --task "Write a Python rate limiter with Redis" --profile production-code

# Dry run (show what would happen without API calls)
node gan-orchestrator.js --task "..." --dry-run
```

## Files

- `gan-config.example.yaml` — Example configuration
- `README.md` — This file

## Implementation Note

The orchestrator script is a reference design — not yet implemented. The architecture is:

```
gan-orchestrator.js
├── loadRubric(profile) → reads .md files, builds prompt
├── callGenerator(taskSpec, feedback?) → isolated API call
├── callDiscriminator(artifact, rubric) → isolated API call
├── parseScores(response) → extract structured scores
├── checkConvergence(scores, history) → CONVERGE/ITERATE/EXIT
└── main loop with progress reporting
```

Contributions welcome — see the main README for the architecture that must be preserved.
