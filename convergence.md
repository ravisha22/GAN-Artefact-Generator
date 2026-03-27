# Convergence Strategy Reference

## Strategy 1: Score Threshold

The primary convergence mechanism. The artifact converges when its weighted average
score meets or exceeds the threshold.

**Default threshold:** 8.0 / 10.0

**How it works:**
1. After each iteration, the Discriminator scores every priority dimension (1-10)
2. The Arbiter computes the weighted average using priority weights
3. If weighted_avg ≥ threshold AND no hard-gate failures → CONVERGE
4. If weighted_avg ≥ threshold BUT hard-gate failure exists → MUST ITERATE

**When to use:** Standard quality bar. Good for most artifacts where you have a clear
definition of "good enough."

**When to raise the threshold:**
- Production-critical code (use 9.0)
- Regulatory documents (use 9.0)
- Public-facing PRDs that will be shared with executives (use 8.5)

**When to lower the threshold:**
- Prototypes / MVPs (use 6.0-7.0)
- Internal drafts for iteration (use 7.0)
- Time-constrained work (use 7.0)

---

## Strategy 2: Delta-Based (Diminishing Returns)

Detects when iteration is no longer producing meaningful improvement and exits early.

**Default delta threshold:** 5% (0.05)

**How it works:**
1. After iteration N, compare weighted_avg(N) to weighted_avg(N-1)
2. Compute delta = (score_N - score_N-1) / score_N-1
3. If delta < delta_threshold → EARLY EXIT
4. Select best-scoring artifact from all iterations as final output

**When to use:** When you want to avoid wasting iterations on marginal gains. Especially
valuable when running in API mode (each iteration costs tokens).

**Edge cases:**
- If delta is NEGATIVE (score went down), this counts as an oscillation, not convergence.
  See oscillation handling in SKILL.md.
- Delta check only activates from iteration 2 onward (need at least 2 data points).
- If delta_enabled is false, this check is skipped entirely.

**Configuration:**
- `delta_threshold: 0.05` — stop if improvement < 5%
- `delta_threshold: 0.10` — more aggressive early exit (10%)
- `delta_threshold: 0.02` — more patient, allows smaller improvements (2%)

---

## Strategy 3: Best-of-N Selection

Fallback mechanism when the score threshold isn't reached within max iterations.

**How it works:**
1. Track the weighted average score for every iteration
2. When max_iterations is reached without threshold convergence:
   a. Rank all iterations by weighted average score
   b. If top 2 scores are within 0.3 of each other, prefer the one with no hard-gate failures
   c. Select the highest-scoring artifact as final output
3. Report that convergence was NOT achieved and show the gap

**When to use:** Always enabled as a safety net. Ensures the user always gets output
even if perfection isn't reached.

**Output format when best-of-N triggers:**
```
⚠️ CONVERGENCE NOT ACHIEVED
Target: 8.0/10 | Best achieved: 7.4/10 (iteration 2 of 3)
Selecting best iteration. Residual issues:
1. [Issue still present]
2. [Issue still present]
Recommendation: Consider adjusting [priority] weight or raising max_iterations.
```

---

## Combined Strategy (Default)

The default configuration uses ALL THREE strategies together:

```
1. Run iteration
2. Score artifact
3. Check: weighted_avg ≥ threshold?
   YES → CONVERGE (output final)
   NO  → continue to step 4
4. Check: iteration ≥ 2 AND delta < delta_threshold?
   YES → EARLY EXIT with best-of-N selection
   NO  → continue to step 5
5. Check: iteration = max_iterations?
   YES → FALLBACK with best-of-N selection
   NO  → feed feedback to generator, go to step 1
```

**Hard gate override:** At any point, if a weight-5 priority scores < 6, convergence
is blocked regardless of weighted average. The iteration continues (or if at max, the
best-of-N report flags the hard-gate failure prominently).

---

## Iteration Budget Guidance

| Artifact Type | Recommended Max | Reasoning |
|---|---|---|
| PRD (short, <3 pages) | 3 | Usually converges in 1-2 |
| PRD (full, 5+ pages) | 5 | More dimensions to evaluate |
| Code (single module) | 3 | Linting + tests give objective signal |
| Code (multi-file system) | 5-7 | Interdependencies need more passes |
| Strategy document | 3 | Subjective — diminishing returns hit fast |
| API design | 5 | Consistency and edge cases need passes |

---

## Convergence Logging

Every iteration MUST log to the iteration history. The Arbiter uses this log for
oscillation detection and best-of-N selection.

```
iteration_log = [
  {
    iteration: 1,
    weighted_avg: 6.2,
    scores: { security: 7, compliance: 5, code_quality: 6, ... },
    hard_gate_failures: ["compliance"],
    top_issues: ["No data retention policy", "Missing error handling for auth flow"],
    decision: "ITERATE"
  },
  {
    iteration: 2,
    weighted_avg: 7.8,
    delta: 0.258,
    scores: { security: 8, compliance: 7, code_quality: 8, ... },
    hard_gate_failures: [],
    top_issues: ["Edge case: concurrent modification not addressed"],
    decision: "ITERATE"
  },
  {
    iteration: 3,
    weighted_avg: 8.3,
    delta: 0.064,
    scores: { security: 9, compliance: 8, code_quality: 8, ... },
    hard_gate_failures: [],
    top_issues: [],
    decision: "CONVERGE — threshold met"
  }
]
```
