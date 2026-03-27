# ChatGPT Integration (Custom GPT / Projects)

This folder contains the GAN Refinement system adapted for ChatGPT.

## Option 1: Custom GPT

### Custom GPT Setup

1. Go to [ChatGPT → Explore GPTs → Create](https://chatgpt.com/gpts/editor)
2. Set **Name**: "GAN Artifact Refiner"
3. Set **Description**: "Adversarial refinement engine for PRDs, code, architecture docs"
4. Copy the contents of `custom-gpt-instructions.md` into the **Instructions** field
5. Upload these files as **Knowledge**:
   - `priorities.md` (from repo root)
   - `convergence.md` (from repo root)
   - `prd-rubric.md` (from repo root)
   - `code-rubric.md` (from repo root)
   - `discriminator-prompt.md` (from repo root)
6. Save and publish (private or public)

### Usage

Start a conversation with the GPT and say:

- "Refine this PRD" + paste your document
- "Write production-ready code for [description] and refine it"
- "Use the enterprise profile" for stricter evaluation

### Context Isolation Limitation

ChatGPT does NOT support subagents or isolated contexts. The system uses the inline XML-block mode (same as Claude Desktop). The Generator and Discriminator share context — this reduces isolation rigor but still produces measurable improvement through structured separation.

## Option 2: ChatGPT Projects

### Project Setup

1. Create a new Project in ChatGPT
2. Upload the same knowledge files listed above
3. Set Project Instructions to the contents of `custom-gpt-instructions.md`

### Advantage over Custom GPT

Projects persist context across conversations, so the rubric files stay loaded.

## Local Validation (One Command)

Run this from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\platforms\chatgpt\validate-chatgpt-setup.ps1
```

This script validates:

- Required files exist
- Instruction schema markers are present
- README references all required knowledge files
- Upload bundle is generated at `platforms/chatgpt/chatgpt-knowledge-bundle.zip`

## Manual Smoke Test

Use the strict pass/fail checklist in `SMOKE-CHECKLIST.md` after creating your Custom GPT or Project.

## Files in This Folder

- `custom-gpt-instructions.md` — Instructions for the Custom GPT / Project
- `validate-chatgpt-setup.ps1` — One-command local validator + bundle creator
- `SMOKE-CHECKLIST.md` — Manual ChatGPT runtime verification checklist
- `README.md` — This file
