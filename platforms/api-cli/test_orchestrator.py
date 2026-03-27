"""Test the GAN orchestrator parser and convergence logic."""
import sys
import json
sys.path.insert(0, "c:/Users/ranandag/Documents/VSCodeProjects/GAN-Prompting/platforms/api-cli")
from gan_orchestrator import parse_discriminator_output, compute_weighted_avg, check_hard_gates, PROFILES

test_output = """
SCORES:
- Security: 8/10 — mTLS, RBAC, JWT validation
- Compliance: 7/10 — SOC 2 mentioned, no GDPR
- Document Quality: 9/10 — All sections present
- Logical Consistency: 8/10 — Requirements trace to personas
- Ease of Use: 8/10 — Clear for all audiences
- Performance: 9/10 — Specific SLAs
- Test Coverage: 6/10 — Basic acceptance criteria only
- Scalability: 8/10 — Horizontal scaling addressed

WEIGHTED_AVERAGE: 7.9/10
HARD_GATE_STATUS: PASS
TOP_ISSUES:
1. [Test Coverage] No security testing → FIX: Add security test suite
2. [Compliance] No GDPR mapping → FIX: Add compliance matrix
3. [Document Quality] Missing open questions → FIX: Add unknowns
CONVERGENCE: ITERATE
REASONING: Score 7.9 below 8.0 threshold
"""

parsed = parse_discriminator_output(test_output)
profile = PROFILES["prd-default"]
computed = compute_weighted_avg(parsed["scores"], profile)
gates_pass, gates_failed = check_hard_gates(parsed["scores"], profile)

assert len(parsed["scores"]) == 8, f"Expected 8 scores, got {len(parsed['scores'])}"
assert parsed["weighted_avg"] == 7.9, f"Expected 7.9, got {parsed['weighted_avg']}"
assert parsed["hard_gate"] == "PASS"
assert parsed["convergence"] == "ITERATE"
assert len(parsed["top_issues"]) == 3
assert gates_pass is True, f"Gates should pass, failed: {gates_failed}"

# Test hard gate failure
fail_scores = {"Security": 4, "Bug Threshold": 8}
fail_pass, fail_dims = check_hard_gates(fail_scores, PROFILES["production-code"])
assert fail_pass is False, "Should fail Security hard gate"
assert "Security=4" in fail_dims[0]

print("Scores:", json.dumps(parsed["scores"], indent=2))
print(f"Reported avg: {parsed['weighted_avg']}")
print(f"Computed avg: {computed}")
print(f"Hard gates: {'PASS' if gates_pass else 'FAIL'}")
print(f"Convergence: {parsed['convergence']}")
print(f"Issues found: {len(parsed['top_issues'])}")
print()
print("✅ ALL PARSER + CONVERGENCE TESTS PASSED")
