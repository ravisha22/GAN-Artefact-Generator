# Progress Report Template

Use this template after each iteration to report progress to the user.

---

## Verbose Format (default)

```
═══════════════════════════════════════════════════════
  GAN REFINEMENT — Iteration {N} of {max}
═══════════════════════════════════════════════════════

SCORES:
┌─────────────────┬───────┬──────────┬──────────┐
│ Priority        │ Score │ Δ        │ Status   │
├─────────────────┼───────┼──────────┼──────────┤
│ Security        │ 8/10  │ +2       │ ✅ Pass   │
│ Compliance      │ 7/10  │ +1       │ ✅ Pass   │
│ Code Quality    │ 6/10  │ +1       │ ⚠️ Below  │
│ Bug Threshold   │ 9/10  │ —        │ ✅ Pass   │
│ Ease of Use     │ 7/10  │ +3       │ ✅ Pass   │
└─────────────────┴───────┴──────────┴──────────┘

WEIGHTED AVERAGE: 7.4/10 (target: 8.0)
HARD GATES: All passing ✅
DELTA: +12.1% from previous iteration

DECISION: ▶ ITERATE — 1 dimension below threshold

TOP ISSUES TO RESOLVE:
1. [Code Quality] Function processPayment() handles validation, business logic,
   and persistence in a single 80-line function
   → FIX: Extract into validatePayment(), executePayment(), persistResult()

2. [Ease of Use] No README setup instructions; 3 undocumented env vars required
   → FIX: Add README with setup steps, document PAYMENT_API_KEY, DB_URL, LOG_LEVEL

═══════════════════════════════════════════════════════
```

## Compact Format

```
[GAN {N}/{max}] Score: 7.4/10 (target: 8.0) | Δ: +12.1% | Decision: ITERATE
Issues: Code Quality (6/10) — split processPayment(); Missing README
```

## Silent Format

No output between iterations. Only report on convergence or failure.

---

## Final Convergence Report

```
═══════════════════════════════════════════════════════
  GAN REFINEMENT — CONVERGED ✅
═══════════════════════════════════════════════════════

RESULT: Converged at iteration {N} of {max}
FINAL SCORE: {weighted_avg}/10

FINAL SCORES:
┌─────────────────┬───────┐
│ Priority        │ Score │
├─────────────────┼───────┤
│ Security        │ 9/10  │
│ Compliance      │ 8/10  │
│ Code Quality    │ 8/10  │
│ Bug Threshold   │ 9/10  │
│ Ease of Use     │ 8/10  │
└─────────────────┴───────┘

ITERATION HISTORY:
  Iteration 1: 6.2/10 → ITERATE
  Iteration 2: 7.8/10 (+25.8%) → ITERATE
  Iteration 3: 8.4/10 (+7.7%) → CONVERGE ✅

KEY IMPROVEMENTS MADE:
• [Iteration 1→2] Added input validation on all API endpoints
• [Iteration 1→2] Restructured monolithic handler into service layer
• [Iteration 2→3] Added comprehensive error handling with structured errors
• [Iteration 2→3] Created README with setup and configuration docs

RESIDUAL RISKS (accepted trade-offs):
• Performance not load-tested (scored 7/10, above threshold but not verified)
• Integration tests deferred (unit coverage sufficient for MVP)

═══════════════════════════════════════════════════════
```

## Non-Convergence Report

```
═══════════════════════════════════════════════════════
  GAN REFINEMENT — MAX ITERATIONS REACHED ⚠️
═══════════════════════════════════════════════════════

RESULT: Best-of-{max} selected (iteration {best_N})
FINAL SCORE: {best_weighted_avg}/10 (target was {threshold})
GAP: {threshold - best_weighted_avg} points below target

SELECTED: Iteration {best_N} (highest scoring)
RUNNER-UP: Iteration {runner_up_N} ({runner_up_score}/10)

UNRESOLVED ISSUES:
1. [{priority}] {issue description}
   Attempted fixes: {what was tried across iterations}
   Recommendation: {manual intervention or config change needed}

RECOMMENDATION:
{One of:}
• Raise max_iterations to {suggested} and re-run
• Lower threshold to {suggested} (current artifact may be acceptable)
• This issue may require manual intervention — the Generator cannot resolve
  {specific issue} within the current constraints

═══════════════════════════════════════════════════════
```
