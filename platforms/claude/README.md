# Claude Desktop / Claude Code Integration

This folder contains the GAN Refinement system adapted for Claude Desktop (Projects) and Claude Code.

## Claude Desktop (Projects)

### Setup

1. Create a new Project in Claude Desktop
2. Upload these files as **Project Knowledge**:
   - `system-prompt.md` (from this folder)
   - `priorities.md` (from repo root)
   - `convergence.md` (from repo root)
   - `prd-rubric.md` (from repo root)
   - `code-rubric.md` (from repo root)
   - `discriminator-prompt.md` (from repo root)
3. Set the **Project Instructions** to the contents of `system-prompt.md`

### Usage

Start a conversation and say:
- "Refine this PRD using the GAN loop" + paste your artifact
- "Generate a production-ready architecture doc for [description]"
- "Iterate on this code until it passes the production code rubric"

### Context Isolation Limitation

Claude Desktop does NOT support subagents. The Generator and Discriminator run in the same conversation context. Mitigation: the system prompt instructs Claude to use XML-delimited blocks (`<generator>`, `<discriminator>`) to separate concerns, and to compress prior iterations to scores + top issues only.

This is the "inline fallback" mode described in the skill. It's less rigorous than subagent isolation but still produces measurable improvement.

## Claude Code

### Setup

Claude Code supports the `Task` tool for spawning subtasks with isolated context. Copy the AGENTS.md file to your project root:

```bash
cp AGENTS.md /path/to/your/project/AGENTS.md
```

Also copy the rubric files to a `.gan-refinement/` directory in your project:

```bash
mkdir -p /path/to/your/project/.gan-refinement
cp priorities.md convergence.md prd-rubric.md code-rubric.md discriminator-prompt.md progress-report.md /path/to/your/project/.gan-refinement/
```

### Claude Code Context Isolation

Claude Code can achieve proper isolation via the `Task` tool:
- Generator runs as a subtask (isolated context)
- Discriminator runs as a subtask (isolated context)
- Arbiter logic runs in the main conversation

This matches the architecture's intent for full context isolation.

## Files in This Folder

- `system-prompt.md` — System prompt for Claude Desktop Projects (inline mode)
- `AGENTS.md` — Agent definitions for Claude Code (subtask mode)
