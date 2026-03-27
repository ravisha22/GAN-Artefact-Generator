# Future Projects — Advanced AI/ML Patterns for Artifact Quality

> Created: 2026-03-26
> Status: Research & Planning
> Context: Derived from GAN Refinement hypothesis testing (Round 1). These patterns represent opportunities beyond the current adversarial refinement approach.

---

## Project 1: Diffusion-Style Progressive Refinement

### The Idea

Instead of generating a complete artifact and then critiquing it (GAN approach), build the artifact **progressively from coarse to fine**, evaluating at each level of detail. Like how a human writes: outline → structure → draft → polish. Each stage has a focused evaluation before proceeding to the next.

The key insight: **catching a bad foundation early is cheaper than fixing a finished building.** If the problem statement is wrong, every requirement built on it is wasted work. The GAN approach discovers this only after the full artifact exists. Progressive refinement discovers it at Stage 1.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  PROGRESSIVE PIPELINE                    │
│                                                          │
│  Stage 1: SKELETON                                       │
│  ┌──────────┐     ┌──────────────┐                       │
│  │ Generate  │────→│ Evaluate     │──→ Pass? Continue     │
│  │ Outline   │     │ Structure    │──→ Fail? Regenerate   │
│  └──────────┘     └──────────────┘                       │
│       ↓                                                  │
│  Stage 2: FOUNDATIONS                                    │
│  ┌──────────┐     ┌──────────────┐                       │
│  │ Generate  │────→│ Evaluate     │──→ Pass? Continue     │
│  │ Problem + │     │ Logic +      │──→ Fail? Regenerate   │
│  │ Personas  │     │ Consistency  │                       │
│  └──────────┘     └──────────────┘                       │
│       ↓                                                  │
│  Stage 3: REQUIREMENTS                                   │
│  ┌──────────┐     ┌──────────────┐                       │
│  │ Generate  │────→│ Evaluate     │──→ Pass? Continue     │
│  │ FRs/NFRs │     │ Traceability │──→ Fail? Regenerate   │
│  │ from above│     │ + Coverage   │                       │
│  └──────────┘     └──────────────┘                       │
│       ↓                                                  │
│  Stage 4: POLISH                                         │
│  ┌──────────┐     ┌──────────────┐                       │
│  │ Generate  │────→│ Evaluate     │──→ Final artifact     │
│  │ Security, │     │ Full rubric  │                       │
│  │ Tests,    │     │ (all dims)   │                       │
│  │ Compliance│     │              │                       │
│  └──────────┘     └──────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

**Critical UX decision**: The user provides ALL context up front (project, company, scope, style, template) in a single prompt — exactly like today. The progressive stages are **internal to the system**. The user never sees intermediate outputs unless they opt into verbose mode. They get one final artifact, but it was built foundation-first internally.

### Applicability Analysis

#### PRD Generation

**How it would work**:
- Stage 1: Generate document outline (section headers, rough structure) → Evaluate: Are all required sections present? Does the structure match the template?
- Stage 2: Generate problem statement + personas + success metrics → Evaluate: Is the problem quantified? Are personas differentiated? Are metrics SMART?
- Stage 3: Generate requirements + scope + edge cases (building on approved foundations) → Evaluate: Do FRs trace to personas/stories? Is scope bounded?
- Stage 4: Generate security, compliance, testing, phasing (building on approved requirements) → Evaluate: Full rubric across all dimensions

**Why it's better than GAN for PRDs**: The GAN approach generates a 600-line PRD, then the Discriminator says "your problem statement is solution-first" — and the Generator has to rewrite everything downstream. Progressive refinement catches this at Stage 2, before requirements exist.

**Estimated cost vs. GAN**:

| Metric | GAN (current) | Progressive | Difference |
|--------|--------------|-------------|------------|
| API calls (success path) | 4-6 (gen+disc per iter) | 8 (gen+eval per stage) | +2-4 calls |
| API calls (early failure) | Same 4-6 regardless | 2 (fails at Stage 1, regenerates) | **-2-4 calls** |
| Tokens per call | ~8-12K (full artifact) | ~2-4K (single stage) | **Smaller per call** |
| Total tokens (success) | ~47K | ~32-40K | **~15-25% cheaper** |
| Total tokens (failure/regen) | ~47K (wasted on bad foundation) | ~8-12K (regenerate just Stage 1-2) | **~70% cheaper on failures** |
| Latency | 3 sequential full-artifact generations | 4 sequential but smaller generations | Comparable |

**Key advantage**: Failures are cheap. Regenerating a 500-token outline is trivial. Regenerating a 10K-token full PRD because the outline was wrong is expensive.

#### Code Generation

**How it would work**:
- Stage 1: Generate API surface (types, interfaces, function signatures) → Evaluate: Are types correct? Is the public API ergonomic? Security patterns present?
- Stage 2: Generate implementation (function bodies, logic) → Evaluate: Correctness, edge cases, error handling
- Stage 3: Generate tests → Evaluate: Coverage, edge case tests, security tests
- Stage 4: Generate docs, config, packaging → Evaluate: Full rubric

**Why it's interesting for code**: Type-first development is already a best practice. Generating interfaces before implementations lets you catch API design problems before writing the code behind them.

**Estimated cost vs. GAN**:

| Metric | GAN (current) | Progressive | Difference |
|--------|--------------|-------------|------------|
| Total tokens (success) | ~48K | ~35-45K | **~5-15% cheaper** |
| Total tokens (bad API design) | ~48K | ~6-10K (fail at Stage 1) | **~75% cheaper** |
| Bug detection | Post-generation (full artifact reviewed) | Per-stage (catch type errors before writing logic) | **Earlier detection** |

**Key advantage for code**: The compiler/type checker can run after Stage 1 (interfaces) — objective validation at the foundation level. This is something GAN can't do because it evaluates the whole artifact.

#### Security Posture Check

**How it would work**:
- Stage 1: Generate threat model (attack surface identification) → Evaluate: Are all components covered? Is STRIDE complete?
- Stage 2: Generate controls per threat (mitigations, policies) → Evaluate: Does every threat have a control? Are controls proportional to risk?
- Stage 3: Generate test/verification plan → Evaluate: Is every control testable? Are there residual risks documented?
- Stage 4: Generate implementation guidance + compliance mapping → Evaluate: Full rubric

**Why it's compelling for security**: Security is inherently layered — identify threats BEFORE designing controls. The GAN approach mixes identification and mitigation in one pass, which often means the threat model is shaped by what mitigations the Generator already knows rather than by systematic analysis.

**Estimated cost vs. GAN**:

| Metric | GAN (current) | Progressive | Difference |
|--------|--------------|-------------|------------|
| Threat coverage | LLM generates threats it knows mitigations for (confirmation bias) | Stage 1 identifies threats without thinking about mitigations | **Better threat coverage** |
| Total tokens | ~45K | ~30-40K | **~10-20% cheaper** |
| False negatives | Higher (threats missed because no mitigation came to mind) | Lower (threats identified independent of mitigation knowledge) | **More thorough** |

#### Architecture Documentation

**How it would work**:
- Stage 1: Generate architectural drivers (constraints, quality attributes, stakeholder concerns) → Evaluate
- Stage 2: Generate component decomposition → Evaluate: Do components map to drivers?
- Stage 3: Generate interaction patterns, data flow → Evaluate: Consistency, no circular dependencies
- Stage 4: Generate deployment, operations, decision records → Evaluate: Full rubric

**Why it's natural for architecture**: Architecture IS a progressive refinement process. Architects don't start with deployment diagrams — they start with constraints and requirements. Forcing the LLM to follow this progression should produce more coherent architectures.

### Cost/Time Summary vs. GAN

| Scenario | GAN Tokens | Progressive Tokens | Progressive Advantage |
|----------|-----------|-------------------|----------------------|
| Clean success (no regen needed) | ~47K | ~35-40K | 15-25% cheaper |
| Early foundation failure | ~47K (all wasted) | ~8-12K (only failed stage) | **70-80% cheaper** |
| Multiple stage failures | ~47K × iterations | ~15-25K (targeted regen) | **50-70% cheaper** |
| Perfect one-shot would pass | ~10K (one-shot wins) | ~35-40K (overhead) | GAN is cheaper here |

**Verdict**: Progressive refinement is cheaper than GAN when the artifact has foundation problems (which Round 1 showed happens frequently). GAN is cheaper when the artifact is mostly correct and only needs polish. The optimal strategy may be: progressive refinement for generation, GAN for final quality gate.

### Open Questions

1. Does the progressive approach produce more coherent artifacts than GAN (because each stage builds on validated foundations)?
2. Can stages run with smaller, cheaper models (e.g., Stage 1 outline generation on a fast model, Stage 4 polish on a large model)?
3. What's the optimal number of stages? 4 as described, or 3 (coarse/medium/fine)?
4. Can progressive refinement and GAN be combined? (Progressive builds the artifact, then one GAN pass refines the whole thing — belt and suspenders.)

### Implementation Plan

| Step | Description | Priority |
|------|-------------|----------|
| 1 | Define stage schemas per artifact type (what's generated and evaluated at each stage) | High |
| 2 | Build stage-specific evaluation rubrics (subset of full rubric per stage) | High |
| 3 | Prototype with 2 PRD test cases — compare output quality and token cost vs. GAN | High |
| 4 | If positive, extend to code and security artifact types | Medium |
| 5 | Explore hybrid: progressive generation + GAN final pass | Medium |
| 6 | Explore stage-specific model routing (cheap model for outline, expensive for polish) | Low |

---

## Project 2: Formal Verification + LLM (Neuro-Symbolic Quality)

### The Idea

Combine LLM-based evaluation (subjective quality: "is this well-written?") with formal verification (objective correctness: "does every FR trace to a user story?" — answerable by graph traversal, not judgment). The formal verifier acts as an **objective Discriminator** alongside the LLM-based Discriminator.

### Why This Matters

Our current Discriminator is an LLM scoring artifacts against a rubric. It's good at catching missing sections and qualitative issues, but it can:
- Miss traceability gaps that require counting/matching (LLMs are bad at counting)
- Give inconsistent scores across runs (non-deterministic)
- Be fooled by confident-sounding but incorrect claims

A formal verifier is deterministic, exhaustive, and can't be fooled.

### Verifiable Properties by Artifact Type

#### PRD Formal Checks

| Property | Formal Verification Method | What It Catches |
|----------|---------------------------|-----------------|
| **Traceability completeness** | Parse FR/US/AC/TEST IDs → build directed graph → check for orphans | FR-010 with no user story (caught in T-PRD-02 by LLM, but formally checkable) |
| **ID uniqueness** | Parse all IDs (FR-001, NFR-001, etc.) → check for duplicates | Duplicate IDs that confuse implementers |
| **Section presence** | Parse headings → check against required section list | Missing Open Questions section (caught in T-PRD-02) |
| **Metric measurability** | Parse success metrics → check for: baseline + target + measurement method | "Improve user experience" without numbers |
| **Cross-reference validity** | Parse all internal references (FR-001, TEST-003) → verify referenced IDs exist | Phantom TEST-024/025/028 (caught in T-PRD-01 by LLM, formally checkable) |
| **Scope boundary** | Check for "In Scope" and "Out of Scope" sections with ≥1 item each | Unbounded scope |
| **RFC 2119 consistency** | Parse MUST/SHOULD/MAY → verify no contradictions (MUST X and MUST NOT X) | Specification contradictions |

#### Code Formal Checks

| Property | Tool | What It Catches |
|----------|------|-----------------|
| **Type safety** | `tsc --noEmit --strict` | Type errors, any-leakage |
| **Lint rules** | ESLint/Ruff | Style violations, common bugs |
| **Test pass** | `npm test` / `pytest` | Functional correctness (objective) |
| **Security patterns** | `npm audit` / `pip-audit` / Semgrep | Known CVEs, vulnerable patterns |
| **Dependency freshness** | `npm outdated` / `pip list --outdated` | Outdated dependencies |
| **Coverage** | `c8` / `coverage.py` | Untested code paths |
| **Complexity** | Cyclomatic complexity tools | Functions too complex to maintain |

#### Security Posture Formal Checks

| Property | Verification Method | What It Catches |
|----------|-------------------|-----------------|
| **STRIDE coverage** | Parse threat model → check: every component × every threat category has an entry | Missing threat analysis for a component |
| **Control-to-threat mapping** | Parse controls → verify every threat has ≥1 control | Unmitigated threats |
| **Residual risk documentation** | Parse residual risks → check they reference specific threats | "Accepted risks" without specificity |
| **Policy-as-code validation** | OPA/Sentinel policy check against IaC | Non-compliant infrastructure |

### Architecture: Dual Discriminator

```
                    ┌────────────────────┐
                    │   GENERATOR        │
                    │   (produces        │
                    │    artifact)       │
                    └────────┬───────────┘
                             │
                    ┌────────▼───────────┐
                    │   ARTIFACT         │
                    └───┬────────────┬───┘
                        │            │
           ┌────────────▼──┐    ┌───▼───────────────┐
           │ LLM           │    │ FORMAL VERIFIER    │
           │ DISCRIMINATOR │    │ (deterministic)    │
           │ (qualitative) │    │                    │
           └────────┬──────┘    └────────┬───────────┘
                    │                    │
           ┌────────▼────────────────────▼───────────┐
           │   ARBITER                                │
           │   Merges: qualitative scores +           │
           │   objective pass/fail results            │
           │   Rule: formal failures OVERRIDE         │
           │   LLM scores on the relevant dimension   │
           └──────────────────────────────────────────┘
```

**Override rule**: If the formal verifier finds FR-010 has no user story traceability, the Logical Consistency dimension drops to ≤5 regardless of what the LLM scored. Deterministic facts always win over probabilistic assessment.

### Cost/Time Implications

| Metric | LLM-only Discriminator | LLM + Formal Verifier | Impact |
|--------|----------------------|----------------------|--------|
| Token cost | Same (LLM calls unchanged) | Same + ~0 tokens (formal runs locally) | **No additional token cost** |
| Time per evaluation | ~30s (LLM call) | ~30s (LLM) + ~2s (formal) | **Negligible** |
| Consistency | Non-deterministic (varies per run) | Formal checks are 100% deterministic | **More reliable** |
| False negatives | Possible (LLM misses counting errors) | Impossible for formal checks | **Better coverage** |
| Implementation effort | Already built | Need parsers per artifact type | **Medium effort** |

**Key insight**: Formal verification adds quality at near-zero marginal cost — it runs locally, requires no API calls, and produces deterministic results. It's the highest-ROI addition to the current system.

### Implementation Plan

| Step | Description | Priority |
|------|-------------|----------|
| 1 | Build PRD ID parser (extract FR-*, NFR-*, US-*, AC-*, TEST-* from markdown) | High |
| 2 | Build traceability graph checker (verify all IDs referenced elsewhere exist) | High |
| 3 | Build section presence checker (verify required sections for artifact type) | High |
| 4 | Integrate formal results into Arbiter's convergence logic (override rules) | High |
| 5 | For code: integrate tsc/eslint/pytest results as formal Discriminator signals | Medium |
| 6 | For security: build STRIDE coverage matrix checker | Medium |
| 7 | Build metric measurability checker (regex for baseline + target + method) | Low |

---

## Project 3: Memory-Augmented Quality Learning

### The Idea

Build a persistent quality memory that accumulates learnings from past GAN loop runs. Over time, the system learns: "this pattern always scores low" → "avoid this pattern" → "substitute with this better pattern." The quality improves without changing the model.

### Why This Is High-Impact

Every GAN loop run produces valuable data:
- (artifact_section, score, feedback) tuples
- Pattern → quality correlations ("sync-in-async always gets flagged")
- Artifact type → common omissions ("PRDs always miss compliance sections initially")
- User-specific preferences ("this user values security over performance")

Currently, all this data is **thrown away** after each run. A quality memory would capture it and use it to inform future runs — making each generation better than the last.

### Architecture

```
┌────────────────────────────────────────────────────┐
│                 QUALITY MEMORY                      │
│                                                     │
│  ┌──────────────────┐  ┌────────────────────────┐  │
│  │ Pattern Library   │  │ Anti-Pattern Library    │  │
│  │ "STRIDE tables    │  │ "sync-in-async in      │  │
│  │  score +2 on      │  │  ASGI middleware        │  │
│  │  Security"        │  │  always fails Bug       │  │
│  │                   │  │  Threshold"             │  │
│  └──────────────────┘  └────────────────────────┘  │
│                                                     │
│  ┌──────────────────┐  ┌────────────────────────┐  │
│  │ Omission Registry │  │ User Preferences       │  │
│  │ "PRDs: compliance │  │ "Ravi: always wants     │  │
│  │  section missing  │  │  exec summary, STRIDE  │  │
│  │  in 80% of        │  │  table, capacity       │  │
│  │  one-shots"       │  │  planning"             │  │
│  └──────────────────┘  └────────────────────────┘  │
└──────────────────┬─────────────────────────────────┘
                   │
          Used by both:
          ┌────────▼────────┐
          │   GENERATOR     │ ← "Include STRIDE table (quality memory: +2 Security)"
          │                 │ ← "Avoid sync-in-async (quality memory: always fails)"
          └─────────────────┘
          ┌────────▼────────┐
          │   DISCRIMINATOR │ ← "Check for known anti-patterns from memory"
          │                 │ ← "Verify user-specific requirements are met"
          └─────────────────┘
```

### How It Learns

1. **After each GAN run**: Extract (pattern, dimension, score_delta) tuples
   - "Adding STRIDE table: Security +2, Compliance +1" → add to Pattern Library
   - "maxLength after escapeHtml: Bug Threshold -3" → add to Anti-Pattern Library

2. **Across runs**: Track omission frequency
   - "Compliance section missing in 4/5 PRD one-shots" → add to Omission Registry with confidence

3. **Per user**: Track what matters to each user
   - "Ravi's PRDs always get edited to add exec summaries" → add to User Preferences

4. **Decay**: Patterns not confirmed in recent runs decay in confidence (models improve, old anti-patterns get fixed)

### Storage

```json
{
  "patterns": [
    {
      "id": "PAT-001",
      "pattern": "STRIDE threat model table for security-relevant artifacts",
      "artifact_types": ["PRD", "Architecture Doc"],
      "dimension_impact": { "Security": +2.1, "Compliance": +0.8 },
      "confidence": 0.85,
      "observed_in": ["T-PRD-01", "T-PRD-02"],
      "last_confirmed": "2026-03-26"
    }
  ],
  "anti_patterns": [
    {
      "id": "ANTI-001",
      "pattern": "Synchronous Redis call inside async ASGI middleware",
      "artifact_types": ["Code (Python)"],
      "dimension_impact": { "Bug Threshold": -3, "Performance": -3 },
      "confidence": 0.90,
      "observed_in": ["T-CODE-02"],
      "detection_rule": "sync call to redis inside async def __call__"
    }
  ],
  "omissions": [
    {
      "id": "OMIT-001",
      "section": "Compliance",
      "artifact_type": "PRD",
      "frequency": 0.80,
      "observed_in": ["T-PRD-01", "T-PRD-02"],
      "remedy": "Include compliance section with data governance, DPIA, retention"
    }
  ]
}
```

### Cost Implications

| Metric | Without Memory | With Memory | Impact |
|--------|---------------|-------------|--------|
| GAN iterations to converge | 2.3 mean | ~1.5 estimated (fewer omissions → better first pass) | **~35% fewer iterations** |
| Token cost | ~47K | ~32K (fewer iterations) + ~2K (memory context) = ~34K | **~28% cheaper** |
| Quality floor (one-shot with memory-informed prompt) | 5.0/10 | ~6.5-7.0/10 estimated (memory fills the 43% checklist gap) | **+1.5-2.0 points** |
| Setup cost | Zero | Build persistence layer + extraction pipeline | **One-time investment** |

**Key insight**: Memory bridges the gap between "checklist in prompt" and "full GAN loop" — the memory IS a dynamic, self-building checklist that improves with every run. It captures the 43% of improvement that comes from completeness, without manual checklist maintenance.

### Implementation Plan

| Step | Description | Priority |
|------|-------------|----------|
| 1 | Define memory schema (patterns, anti-patterns, omissions, user prefs) | High |
| 2 | Build extraction pipeline: parse Discriminator feedback → identify patterns | High |
| 3 | Build memory injection: prepend relevant memory entries to Generator prompt | High |
| 4 | Build memory injection for Discriminator: known anti-patterns to check | Medium |
| 5 | Build confidence scoring and decay (patterns not confirmed in N runs decay) | Medium |
| 6 | Build per-user preference tracking | Low |
| 7 | Build memory dashboard (view what the system has learned) | Low |

---

## Project 4: Causal Inference for Quality Diagnostics

### The Idea

Current Discriminator says: "Security: 4/10 — no input validation." This is a **symptom**. A causal Discriminator would trace: "Security: 4/10 — no input validation ← requirements don't mention external input ← personas don't include attacker model ← problem statement doesn't reference security incidents." The fix targets the **root cause** (add attacker persona), not the symptom (add validation).

### Why This Is Transformative

In our Round 1 testing, the Discriminator's feedback was always at the symptom level:
- "No threat model" → but WHY is there no threat model? Because the problem statement didn't frame security as a concern.
- "orphan requirement FR-010" → but WHY is it orphaned? Because the user story was missing from the personas section.
- "sync-in-async" → but WHY did the Generator use sync? Because the task description didn't mention async deployment context.

**The Generator fixes symptoms. If it understood causes, it would fix root causes — requiring fewer iterations.**

### Causal Model for Artifact Quality

```
Problem Statement Quality
    │
    ├──→ Persona Completeness
    │       │
    │       ├──→ User Story Coverage
    │       │       │
    │       │       ├──→ Functional Requirement Traceability
    │       │       │       │
    │       │       │       ├──→ Test Coverage
    │       │       │       └──→ Acceptance Criteria Completeness
    │       │       │
    │       │       └──→ Edge Case Identification
    │       │
    │       └──→ Security Requirement Depth
    │               │
    │               ├──→ Threat Model Completeness
    │               └──→ Compliance Coverage
    │
    └──→ Scope Definition Clarity
            │
            ├──→ NFR Specificity
            │       │
            │       └──→ Performance Target Measurability
            │
            └──→ Scalability Projections
```

**Reading the graph**: If "Test Coverage" scores low, trace upstream — is it because "FR Traceability" is weak (requirements aren't clear enough to write tests for)? Or because "User Story Coverage" is incomplete (missing user stories = missing test scenarios)?

### How Causal Diagnostics Would Change Feedback

**Current (symptom-level)**:
```
TOP_ISSUES:
1. [Test Coverage] Only 14 tests, no security testing → FIX: Add security tests
2. [Security] No threat model → FIX: Add STRIDE table
3. [Scalability] No capacity planning → FIX: Add growth projections
```

**Causal (root-cause-level)**:
```
ROOT CAUSE ANALYSIS:
1. PRIMARY CAUSE: Problem statement does not mention security incidents or attacker scenarios
   → EFFECT CHAIN: No security framing → No attacker persona → No security user stories →
     No security requirements → No threat model → No security tests
   → ROOT FIX: Rewrite problem statement to include: "2 XSS incidents in 6 months,
     attacker model: authenticated user submitting malicious input"
   → CASCADING FIX: Once problem statement includes security, the Generator will naturally
     produce personas, stories, requirements, and tests covering it

2. SECONDARY CAUSE: No growth data provided in problem context
   → EFFECT CHAIN: No growth context → No scalability analysis → No capacity projections
   → ROOT FIX: Add to problem statement: "Current: 150 tenants. Projected: 400 in 12 months
     based on sales pipeline"
```

**The difference**: Symptom-level feedback produces 3 separate fix tasks. Causal feedback produces 1 root fix that cascades to resolve all 3. Fewer iterations, more coherent results.

### Technical Approach

1. **Build the causal DAG**: Define the dependency structure between artifact sections (as above). This is a fixed structure per artifact type — the same DAG applies to all PRDs.

2. **Score propagation**: When the Discriminator scores each dimension, propagate scores upstream through the DAG. If Test Coverage = 4 and FRs = 8, the cause is likely in test writing (direct). If Test Coverage = 4 and FRs = 4 and User Stories = 3, the cause is upstream (weak stories → weak FRs → no tests).

3. **Root cause identification**: Find the highest node in the DAG that scores below threshold — that's the root cause. All downstream low scores are effects, not independent problems.

4. **Focused feedback**: The Discriminator reports the root cause + expected cascade, not individual symptoms. The Generator fixes one thing and everything downstream improves.

### Cost Implications

| Metric | Symptom Feedback (current) | Causal Feedback | Impact |
|--------|--------------------------|-----------------|--------|
| Issues per iteration | 3 symptoms | 1 root cause | **3x more focused** |
| Generator confusion | Medium (conflicting fix priorities) | Low (single clear fix) | **Better fix quality** |
| Iterations to converge | 2.3 mean | ~1.5-2.0 estimated | **~20-35% fewer** |
| Token cost per iteration | Same | Same + ~500 tokens (causal analysis) | **Negligible overhead** |
| Total token cost | ~47K | ~35-40K (fewer iterations) | **~15-25% cheaper** |

### Implementation Plan

| Step | Description | Priority |
|------|-------------|----------|
| 1 | Define causal DAGs per artifact type (PRD, Code, Security, Architecture) | High |
| 2 | Build score propagation engine (upstream tracing from low-scoring dimensions) | High |
| 3 | Build root cause identification algorithm (highest upstream node below threshold) | High |
| 4 | Modify Discriminator prompt to include causal DAG and request root cause analysis | Medium |
| 5 | Test: compare iterations-to-converge with causal vs. symptom feedback | Medium |
| 6 | Build cascade prediction: "fixing X should improve Y and Z by ~N points" | Low |
| 7 | Validate cascade predictions against actual improvements | Low |

---

## Cross-Project Synergies

These four projects are not independent — they compose:

```
┌──────────────────────────────────────────────────────────────┐
│  COMBINED SYSTEM (Future Vision)                              │
│                                                               │
│  Quality Memory (#3) informs → Progressive Generator (#1)     │
│  "PRDs always miss compliance" → "Generate compliance at       │
│   Stage 2, not Stage 4"                                       │
│                                                               │
│  Causal Inference (#4) improves → Discriminator feedback       │
│  "Root cause: no attacker persona" instead of 3 symptoms      │
│                                                               │
│  Formal Verifier (#2) validates → Each progressive stage       │
│  "Stage 3: 2 orphan FRs detected" (deterministic, instant)    │
│                                                               │
│  Memory (#3) captures → Causal patterns                        │
│  "Root cause X → symptoms Y,Z seen in 80% of PRDs"            │
│                                                               │
│  Result: A self-improving system that generates artifacts      │
│  foundation-first, catches errors deterministically,           │
│  traces root causes, and gets better with every run.           │
└──────────────────────────────────────────────────────────────┘
```

### Priority Ranking

| Priority | Project | Rationale |
|----------|---------|-----------|
| 1 | **Formal Verification (#2)** | Highest ROI — near-zero marginal cost, deterministic, catches things LLMs reliably miss (counting, traceability). Can be added to existing GAN system immediately. |
| 2 | **Quality Memory (#3)** | Compounds over time. The data pipeline already exists (GAN loops produce scored artifacts). Bridges the checklist gap without manual maintenance. |
| 3 | **Progressive Refinement (#1)** | Better architecture for generation, but requires rethinking the entire pipeline. Higher implementation cost, but potentially superior to GAN for foundation-heavy artifacts. |
| 4 | **Causal Inference (#4)** | Most transformative long-term, but hardest to build and validate. Requires defining causal DAGs per artifact type and validating that cascade predictions are accurate. |
