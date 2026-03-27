# ChatGPT Smoke Test Checklist (Pass/Fail)

Use this after creating your Custom GPT or Project.

## Preconditions

- [ ] `custom-gpt-instructions.md` is copied into the ChatGPT instructions field.
- [ ] `priorities.md` is uploaded.
- [ ] `convergence.md` is uploaded.
- [ ] `prd-rubric.md` is uploaded.
- [ ] `code-rubric.md` is uploaded.
- [ ] `discriminator-prompt.md` is uploaded.

## Test 1: PRD Refinement

### Test 1 Prompt

```text
Refine this PRD using enterprise profile:

We need a rate limiting middleware for our API gateway.
```

### Test 1 Pass Criteria

- [ ] Output includes a scored discriminator block containing all fields:
- [ ] `SCORES:`
- [ ] `WEIGHTED_AVERAGE:`
- [ ] `HARD_GATE_STATUS:`
- [ ] `TOP_ISSUES:`
- [ ] `CONVERGENCE:`
- [ ] Output includes a revised artifact, not only critique.

## Test 2: Iteration Behavior

### Test 2 Prompt

```text
Run one more iteration. Resolve all top issues and re-score.
```

### Test 2 Pass Criteria

- [ ] New response updates the artifact.
- [ ] A new score block is generated.
- [ ] At least one previously listed issue is addressed.
- [ ] If hard gates fail, response does not falsely declare convergence.

## Test 3: Code Profile and Hard Gates

### Test 3 Prompt

```text
Write production-ready TypeScript input validation code and refine it using production-code profile.
```

### Test 3 Pass Criteria

- [ ] Security and Bug Threshold are treated as hard gates.
- [ ] Convergence is blocked if hard gate score is below 6.
- [ ] Recommendations are concrete (specific issue plus fix), not vague.

## Test 4: Threshold Control

### Test 4 Prompt

```text
Use threshold 9.0 and max 3 iterations.
```

### Test 4 Pass Criteria

- [ ] Response acknowledges tighter threshold behavior.
- [ ] If threshold is not met, output indicates iterate or best-of-N fallback.
- [ ] Final summary reports iteration count and final scores.

## Failure Conditions

Mark setup as failed if any of these occur:

- [ ] Missing one or more required score block fields.
- [ ] No discriminator evidence tied to specific content.
- [ ] Always claims convergence regardless of hard gate failures.
- [ ] Ignores explicit profile settings (`enterprise`, `production-code`, `mvp`, `prd-default`).

## Final Verdict

- [ ] PASS: All tests pass and no failure conditions are checked.
- [ ] FAIL: Any required test criterion fails.
