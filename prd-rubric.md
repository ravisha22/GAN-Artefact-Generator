# PRD Discriminator Rubric

This rubric is used when the artifact type is a PRD or product document. The Discriminator
evaluates each section against these criteria.

## Required PRD Sections

The Generator MUST produce all of these sections. Missing sections = automatic score
penalty on the relevant dimension.

| Section | Maps to Priority | Hard Gate? |
| --- | --- | --- |
| Problem Statement | Code Quality (clarity) | No |
| User Personas | Ease of Use | No |
| User Stories / Jobs to Be Done | Code Quality (completeness) | No |
| Success Metrics | Bug Threshold (measurability) | Yes — if metrics are unmeasurable |
| Scope (In/Out) | Bug Threshold (consistency) | Yes — if scope is undefined |
| Requirements (Functional) | Code Quality | No |
| Requirements (Non-Functional) | Performance, Security, Scalability | Depends on weights |
| Edge Cases & Error States | Bug Threshold | No |
| Dependencies & Risks | Compliance | No |
| Timeline / Phasing | Ease of Use (actionability) | No |
| Open Questions | — (meta, not scored) | No |

## Scoring Details per Section

### Problem Statement (weight in Code Quality dimension)

| Score | Criteria |
| --- | --- |
| 1-3 | Solution-first thinking, no clear problem articulation, or problem is actually a feature request |
| 4-6 | Problem exists but is vague ("users struggle with X"), no data or evidence |
| 7-8 | Specific problem with evidence (user research, metrics, support tickets), quantified impact |
| 9-10 | Problem + root cause analysis, quantified opportunity size, strategic alignment articulated |

**Discriminator should flag:**

- "We need to build X" without explaining why → score ≤ 4
- Problem defined in terms of the solution → score ≤ 5
- No user evidence → cap at 6

### User Personas

| Score | Criteria |
| --- | --- |
| 1-3 | No personas, or generic "users" |
| 4-6 | Named personas but no behavioral differentiation |
| 7-8 | Distinct personas with goals, pain points, and usage context |
| 9-10 | Personas grounded in research data with prioritization (primary vs secondary) |

### Success Metrics

| Score | Criteria |
| --- | --- |
| 1-3 | No metrics, or vanity metrics only ("increase engagement") |
| 4-6 | Metrics present but not measurable or no baselines |
| 7-8 | SMART metrics with baselines and targets, instrumentation plan noted |
| 9-10 | Leading and lagging indicators, measurement methodology, statistical significance considerations |

**Hard gate trigger:** If success metrics are completely absent or unmeasurable, this
section triggers the Bug Threshold hard gate (a PRD without measurable outcomes is
inherently defective).

### Scope Definition

| Score | Criteria |
| --- | --- |
| 1-3 | No scope boundaries, or scope = "everything" |
| 4-6 | In-scope defined but out-of-scope missing or vague |
| 7-8 | Clear in/out scope with rationale for exclusions |
| 9-10 | Scope tied to phasing strategy, explicit deferral list with reasoning |

**Hard gate trigger:** If there is no scope boundary at all, this triggers the Bug
Threshold hard gate (unbounded scope = project risk).

### Functional Requirements

| Score | Criteria |
| --- | --- |
| 1-3 | Feature list without user context or acceptance criteria |
| 4-6 | Requirements present but mixed abstraction levels, some missing acceptance criteria |
| 7-8 | Structured requirements with user stories, acceptance criteria, and priority (MoSCoW or similar) |
| 9-10 | All of 7-8 plus: dependency mapping between requirements, technical feasibility signals |

### Edge Cases & Error States

| Score | Criteria |
| --- | --- |
| 1-3 | Not mentioned |
| 4-6 | Some edge cases listed but no handling strategy |
| 7-8 | Edge cases identified with expected behavior and graceful degradation |
| 9-10 | Comprehensive edge case matrix, error state flows, fallback behaviors |

---

## PRD Anti-Patterns the Discriminator Must Catch

These are common PM writing mistakes. Flag any of these and deduct from the relevant score:

1. **Solution-first thinking** — Requirements describe implementation, not outcomes
   → Deduct from Problem Statement score
2. **Metric-free success** — "Improve user experience" without measurement
   → Deduct from Success Metrics, trigger hard gate consideration
3. **Scope creep signals** — "And also...", "While we're at it...", "Nice to have" in core requirements
   → Deduct from Scope Definition score
4. **Missing the 'who'** — Requirements without persona attribution
   → Deduct from User Personas score
5. **Implementation leakage** — "Use React", "Deploy on K8s" in a product PRD
   → Deduct from Code Quality (PRD should be implementation-agnostic unless there's a specific constraint)
6. **Orphan requirements** — Requirements that don't trace back to a user story or problem
   → Deduct from Functional Requirements score
7. **Undifferentiated personas** — All personas want the same thing
   → Deduct from User Personas score

---

## PRD Generator Voice Guidelines

The Generator should write PRDs in this voice:

- Problem-first, outcome-oriented
- Specific over vague ("reduce page load from 3.2s to <1s" not "make it faster")
- User-centric framing (who benefits, how)
- Measurable claims (every assertion should be testable)
- Honest about unknowns (Open Questions section should be substantive, not performative)
- No implementation bias unless a constraint exists

The Discriminator should penalize:

- Marketing language in a product spec
- Passive voice hiding ownership ("it was decided" — by whom?)
- Weasel words ("significantly", "greatly", "much better")
