# Code Discriminator Rubric

This rubric is used when the artifact type is code. The Discriminator evaluates both
the code artifact AND any accompanying tests, documentation, and configuration.

## Evaluation Layers

The Discriminator evaluates code in three layers, from most to least critical:

### Layer 1: Correctness & Safety (Hard Gates)

These are binary checks. ANY failure here blocks convergence regardless of other scores.

| Check | Pass Criteria | Failure Action |
|---|---|---|
| Compiles / runs without error | Code executes on happy path | Hard fail, must iterate |
| No secrets in code | No API keys, passwords, tokens in source | Hard fail, must iterate |
| Input validation on all external inputs | User input, API params, file reads — all validated | Hard fail if public-facing |
| No known vulnerability patterns | No SQL injection, XSS, path traversal, deserialization attacks | Hard fail, must iterate |
| Error handling on all I/O | File ops, network calls, DB queries — all wrapped | Hard fail, must iterate |

### Layer 2: Quality & Maintainability (Scored 1-10)

| Dimension | Score 1-3 | Score 4-6 | Score 7-8 | Score 9-10 |
|---|---|---|---|---|
| **Structure** | Single file/function doing everything | Some separation but unclear boundaries | Clean module boundaries, SRP followed | Layered architecture, dependency injection, clear interfaces |
| **Naming** | Cryptic (`x`, `tmp`, `data2`) | Mixed — some clear, some cryptic | Consistent, intention-revealing names | Self-documenting — code reads like prose |
| **DRY** | Copy-pasted blocks throughout | Some duplication, some abstraction | Minimal duplication, appropriate abstractions | Zero unnecessary duplication, abstractions aren't premature |
| **Comments** | None, or lying comments | Some comments but stale or obvious ("increment i") | Comments explain WHY, not WHAT | Strategic comments at decision points, doc comments on public API |
| **Complexity** | Functions >50 lines, deeply nested | Some long functions, moderate nesting | Functions <20 lines, max 2 levels of nesting | Cyclomatic complexity <10 per function, flat control flow |

### Layer 3: Production Readiness (Scored 1-10)

| Dimension | Score 1-3 | Score 4-6 | Score 7-8 | Score 9-10 |
|---|---|---|---|---|
| **Test coverage** | No tests | Happy path tests only | Unit + edge case tests, mocking strategy | Unit + integration + property tests, CI-ready |
| **Error messages** | Stack traces exposed to user | Generic errors ("Something went wrong") | Specific, actionable errors with codes | Structured errors, correlation IDs, retry guidance |
| **Logging** | None or console.log everywhere | Some logging but inconsistent levels | Structured logging, appropriate levels (info/warn/error) | Observability-ready: traces, metrics, log correlation |
| **Configuration** | Hardcoded values | Some env vars but mixed with hardcoding | All config externalized, documented | Config schema with validation, defaults, env-specific overrides |
| **Dependencies** | Unpinned, unnecessary, or abandoned packages | Mostly pinned, some unnecessary | All pinned, justified, actively maintained | Minimal deps, pinned, license-checked, security-scanned |

---

## Language-Specific Checks

The Discriminator should apply these additional checks based on the language:

### TypeScript / JavaScript
- Strict mode enabled
- No `any` types (unless explicitly justified)
- Proper async/await (no unhandled promises)
- No prototype pollution vectors
- Package.json has lockfile

### Python
- Type hints on public functions
- No bare `except:` clauses
- Virtual environment / dependency pinning
- No `eval()` or `exec()` on user input
- f-strings over concatenation

### General (All Languages)
- Consistent formatting (ideally enforced by config)
- No TODO/FIXME in production code (move to issues)
- README with setup instructions
- .gitignore appropriate for the language

---

## Objective Validation (Bonus Agent)

When bash/terminal access is available, the Discriminator can delegate to objective
validation tools. These produce OBJECTIVE signal that supplements the LLM-based evaluation.

### Available Validations

| Tool | What It Checks | How to Run |
|---|---|---|
| **TypeScript compiler** | Type errors, strict mode | `npx tsc --noEmit --strict` |
| **ESLint** | Style, patterns, common bugs | `npx eslint .` |
| **Python type check** | Type errors | `mypy --strict .` |
| **Python lint** | Style, common bugs | `ruff check .` or `flake8` |
| **Test runner** | Functional correctness | `npm test` / `pytest` |
| **Security scanner** | Known vulnerabilities | `npm audit` / `pip-audit` |

### How to Use Objective Signal

1. Run the available validation tools AFTER the Discriminator's LLM evaluation
2. Objective failures OVERRIDE the LLM's score on the relevant dimension
   - Example: If the LLM scores Security at 8/10 but `npm audit` finds a critical
     vulnerability, Security drops to 3/10
3. Objective passes CONFIRM but don't inflate the LLM's score
   - Example: If `tsc` passes with no errors, this confirms but doesn't boost Code Quality
4. Log both LLM scores and objective results in the iteration report

---

## Code Generator Guidelines

The Generator should produce code that:
- Runs out of the box (include package.json, requirements.txt, etc.)
- Has a clear entry point
- Includes at least stub tests for critical paths
- Uses the project's established patterns (if modifying existing code)
- Separates concerns (don't mix business logic with I/O)
- Handles the unhappy path (what happens when things go wrong?)

The Discriminator should penalize:
- "It works on my machine" code — no setup instructions
- Clever code over clear code
- Premature optimization without profiling evidence
- Tests that test the mock, not the behavior
- Over-abstraction (3 layers of indirection for a simple operation)
