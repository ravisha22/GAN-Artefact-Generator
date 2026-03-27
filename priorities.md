# Discriminator Priority Reference

## Priority Dimensions

Each priority has a weight (1-5) and scoring criteria. Weight 5 = hard gate (artifact
CANNOT converge if this dimension scores below 6/10).

### Security (Default weight: 5 — HARD GATE)

Evaluates the artifact for security vulnerabilities, data exposure risks, and
authentication/authorization gaps.

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | No security considerations mentioned | Known vulnerabilities, no input validation, secrets in code |
| 4-6 | Security mentioned but vague or incomplete | Basic validation present, some gaps in auth/authz |
| 7-8 | Specific security requirements with acceptance criteria | Proper validation, parameterized queries, no secrets, OWASP top 10 addressed |
| 9-10 | Threat model included, security testing requirements defined | All of 7-8 plus: CSP headers, rate limiting, audit logging, dependency scanning |

### Compliance (Default weight: 4)

Evaluates adherence to regulatory, organizational, and industry standards.

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | No compliance context | No license headers, regulatory requirements ignored |
| 4-6 | Compliance mentioned but requirements not specific | Basic compliance but gaps in data handling or logging |
| 7-8 | Specific regulatory requirements listed with validation approach | Proper data handling, logging, consent flows, audit trails |
| 9-10 | Compliance matrix with testing strategy | All of 7-8 plus: automated compliance checks, documentation |

### Code Quality (Default weight: 4)

For code artifacts: structure, readability, maintainability, patterns.
For PRDs: clarity, structure, completeness, actionability.

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | Unstructured, ambiguous, missing key sections | Spaghetti code, no separation of concerns, magic numbers |
| 4-6 | Structured but gaps in detail or clarity | Reasonable structure but inconsistent patterns, some duplication |
| 7-8 | Clear sections, specific requirements, measurable outcomes | Clean architecture, DRY, consistent naming, proper abstractions |
| 9-10 | Publication-ready, every section actionable and testable | All of 7-8 plus: documentation, design patterns, extensibility |

### Bug Threshold (Default weight: 5 — HARD GATE)

For code: functional correctness, edge case handling, error states.
For PRDs: logical consistency, contradictions, impossible requirements.

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | Contradictory requirements, logical impossibilities | Crashes on basic inputs, unhandled exceptions, race conditions |
| 4-6 | Minor inconsistencies, some edge cases unaddressed | Works for happy path, some edge cases fail, error handling gaps |
| 7-8 | Internally consistent, edge cases identified | Handles edge cases, proper error handling, no known bugs |
| 9-10 | All paths traced and validated, no ambiguity | All of 7-8 plus: defensive coding, graceful degradation, chaos-tested |

### Ease of Use (Default weight: 3)

For code: developer experience, API ergonomics, documentation.
For PRDs: stakeholder readability, implementation clarity for engineers.

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | Only the author can understand it | No comments, cryptic API, no README, unclear setup |
| 4-6 | Readable but requires domain expertise to act on | Some docs, reasonable API but rough edges |
| 7-8 | Any PM/engineer can pick up and execute | Clear API, good docs, intuitive naming, easy setup |
| 9-10 | Self-explanatory, includes onboarding notes | All of 7-8 plus: examples, migration guides, troubleshooting |

### Performance (Default weight: 3)

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | No performance requirements | O(n³) where O(n) exists, memory leaks, no caching consideration |
| 4-6 | "Should be fast" — no measurable targets | Reasonable but unoptimized, no benchmarks |
| 7-8 | Specific SLAs (p50, p99 latency, throughput) | Appropriate algorithms, resource-conscious, measured |
| 9-10 | Performance budget with monitoring strategy | All of 7-8 plus: profiled, optimized hot paths, load tested |

### Test Coverage (Default weight: 3)

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | No acceptance criteria | No tests |
| 4-6 | Some acceptance criteria but not comprehensive | Unit tests for happy path only |
| 7-8 | Acceptance criteria for all user stories, edge cases noted | Unit + integration tests, edge cases covered, mocking strategy |
| 9-10 | Full test strategy including regression and exploratory | All of 7-8 plus: property-based tests, contract tests, CI integration |

### Scalability (Default weight: 2)

| Score | PRD Criteria | Code Criteria |
|---|---|---|
| 1-3 | No growth consideration | Hardcoded limits, single-threaded assumptions, no pagination |
| 4-6 | Growth mentioned but no quantified targets | Basic pagination, some configurability |
| 7-8 | Capacity requirements with growth projections | Stateless design, connection pooling, configurable limits |
| 9-10 | Scaling strategy with fallback plans | All of 7-8 plus: horizontal scaling ready, circuit breakers |

---

## Priority Presets

### PRD Default Profile
```
security: 4
compliance: 3
code_quality: 5 (maps to "document quality" for PRDs)
bug_threshold: 4 (maps to "logical consistency")
ease_of_use: 4 (stakeholder readability)
performance: 2
test_coverage: 3 (acceptance criteria completeness)
scalability: 2
```

### Production Code Profile
```
security: 5 (HARD GATE)
compliance: 4
code_quality: 4
bug_threshold: 5 (HARD GATE)
ease_of_use: 3
performance: 3
test_coverage: 4
scalability: 3
```

### MVP / Prototype Profile
```
security: 3
compliance: 2
code_quality: 3
bug_threshold: 4
ease_of_use: 4
performance: 1
test_coverage: 2
scalability: 1
```

### Enterprise / Regulated Profile
```
security: 5 (HARD GATE)
compliance: 5 (HARD GATE)
code_quality: 4
bug_threshold: 5 (HARD GATE)
ease_of_use: 3
performance: 4
test_coverage: 5 (HARD GATE)
scalability: 4
```

---

## Custom Priority Syntax

Users can specify priorities in natural language. Parse these patterns:

- "security is critical" → weight 5, hard gate
- "compliance > code quality > ease of use" → weights 5, 4, 3 respectively
- "security=5, compliance=4, performance=2" → exact weights
- "use production profile but bump test coverage to 5" → preset + override
- "ignore scalability" → weight 0, excluded from scoring

### Weighted Average Calculation

```
weighted_avg = Σ(priority_score × priority_weight) / Σ(priority_weight)
```

Hard gate check runs BEFORE weighted average. If any weight-5 priority scores < 6,
the artifact CANNOT converge regardless of weighted average.
