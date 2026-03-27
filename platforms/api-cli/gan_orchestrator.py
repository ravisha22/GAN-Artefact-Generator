#!/usr/bin/env python3
"""
GAN Artifact Generator — API/CLI Orchestrator

Runs the Generator → Discriminator → Arbiter loop via isolated API calls.
Each call is a fresh conversation — full context isolation guaranteed.

Supports: OpenAI, Azure OpenAI, Anthropic (Claude)

Usage:
    python gan_orchestrator.py --task "Write a PRD for ..." --profile prd-default
    python gan_orchestrator.py --input my-doc.md --profile production-code --threshold 9.0
    python gan_orchestrator.py --task "..." --provider anthropic --model claude-sonnet-4-20250514
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# ─── Configuration ───────────────────────────────────────────────────────────

PROFILES = {
    "prd-default": {
        "Security": 4, "Compliance": 3, "Document Quality": 5,
        "Logical Consistency": 4, "Ease of Use": 4, "Performance": 2,
        "Test Coverage": 3, "Scalability": 2,
        "hard_gates": ["Logical Consistency"],
    },
    "production-code": {
        "Security": 5, "Compliance": 4, "Code Quality": 4,
        "Bug Threshold": 5, "Ease of Use": 3, "Performance": 3,
        "Test Coverage": 4, "Scalability": 3,
        "hard_gates": ["Security", "Bug Threshold"],
    },
    "mvp": {
        "Security": 3, "Compliance": 2, "Code Quality": 3,
        "Bug Threshold": 4, "Ease of Use": 4, "Performance": 1,
        "Test Coverage": 2, "Scalability": 1,
        "hard_gates": [],
    },
    "enterprise": {
        "Security": 5, "Compliance": 5, "Code Quality": 4,
        "Bug Threshold": 5, "Ease of Use": 3, "Performance": 4,
        "Test Coverage": 5, "Scalability": 4,
        "hard_gates": ["Security", "Compliance", "Bug Threshold", "Test Coverage"],
    },
}

HARD_GATE_THRESHOLD = 6


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class IterationResult:
    iteration: int
    artifact: str
    scores: dict[str, float]
    weighted_avg: float
    hard_gate_status: str
    convergence: str
    top_issues: list[str]
    reasoning: str
    gen_tokens: TokenUsage = field(default_factory=TokenUsage)
    disc_tokens: TokenUsage = field(default_factory=TokenUsage)
    wall_time_sec: float = 0.0


# ─── API Callers ─────────────────────────────────────────────────────────────

def call_openai(client: httpx.Client, base_url: str, api_key: str,
                model: str, system: str, user: str, max_tokens: int = 8000) -> tuple[str, TokenUsage]:
    """Call OpenAI-compatible API. Returns (text, usage)."""
    resp = client.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, TokenUsage(
        input_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("completion_tokens", 0),
    )


def call_anthropic(client: httpx.Client, api_key: str,
                   model: str, system: str, user: str, max_tokens: int = 8000) -> tuple[str, TokenUsage]:
    """Call Anthropic Messages API. Returns (text, usage)."""
    resp = client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(b.get("text", "") for b in data.get("content", []))
    usage = data.get("usage", {})
    return text, TokenUsage(
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
    )


def call_llm(client: httpx.Client, provider: str, base_url: str, api_key: str,
             model: str, system: str, user: str, max_tokens: int = 8000) -> tuple[str, TokenUsage]:
    """Route to the correct provider."""
    if provider == "anthropic":
        return call_anthropic(client, api_key, model, system, user, max_tokens)
    return call_openai(client, base_url, api_key, model, system, user, max_tokens)


# ─── Rubric Builder ─────────────────────────────────────────────────────────

def build_rubric_table(profile: dict) -> str:
    """Build a markdown rubric table from a profile dict."""
    hard_gates = profile.get("hard_gates", [])
    lines = ["| Priority | Weight | Hard Gate? |", "|---|---|---|"]
    for dim, weight in profile.items():
        if dim == "hard_gates":
            continue
        hg = "YES (< 6 blocks)" if dim in hard_gates else "No"
        lines.append(f"| {dim} | {weight} | {hg} |")
    return "\n".join(lines)


def load_rubric_file(rubric_dir: Path, filename: str) -> str:
    """Load a rubric markdown file if it exists."""
    p = rubric_dir / filename
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


# ─── Score Parser ────────────────────────────────────────────────────────────

def parse_discriminator_output(text: str) -> dict:
    """Parse structured Discriminator output into scores and metadata."""
    scores = {}
    weighted_avg = 0.0
    hard_gate = "UNKNOWN"
    convergence = "UNKNOWN"
    top_issues = []
    reasoning = ""

    for line in text.split("\n"):
        # Score lines: "- Security: 8/10 — evidence"
        m = re.match(r'^[-*]\s*\**(.+?)\**:\s*(\d+(?:\.\d+)?)\s*/\s*10', line)
        if m:
            scores[m.group(1).strip()] = float(m.group(2))
            continue

        if "WEIGHTED_AVERAGE" in line:
            m2 = re.search(r'(\d+\.?\d*)\s*/\s*10', line)
            if m2:
                weighted_avg = float(m2.group(1))

        if "HARD_GATE" in line:
            hard_gate = "FAIL" if "FAIL" in line.upper() else "PASS"

        if "CONVERGENCE" in line and "CONVERGE" in line.upper():
            if "ITERATE" in line.upper():
                convergence = "ITERATE"
            elif "EARLY" in line.upper():
                convergence = "EARLY_EXIT"
            else:
                convergence = "CONVERGE"

        if "REASONING" in line:
            reasoning = line.split(":", 1)[-1].strip() if ":" in line else ""

        # Top issues: "1. [dim] issue → FIX: fix"
        im = re.match(r'^\d+\.\s*(.+)', line)
        if im and ("FIX" in line or "→" in line or "fix" in line.lower()):
            top_issues.append(im.group(1).strip())

    return {
        "scores": scores,
        "weighted_avg": weighted_avg,
        "hard_gate": hard_gate,
        "convergence": convergence,
        "top_issues": top_issues[:5],
        "reasoning": reasoning,
    }


def compute_weighted_avg(scores: dict[str, float], profile: dict) -> float:
    """Compute weighted average from scores and profile weights."""
    total_weight = 0
    total_score = 0
    for dim, weight in profile.items():
        if dim == "hard_gates":
            continue
        score = scores.get(dim, 0)
        if score == 0:
            # Try fuzzy match
            for s_dim, s_val in scores.items():
                if dim.lower() in s_dim.lower() or s_dim.lower() in dim.lower():
                    score = s_val
                    break
        total_weight += weight
        total_score += score * weight
    return round(total_score / total_weight, 2) if total_weight > 0 else 0


def check_hard_gates(scores: dict[str, float], profile: dict) -> tuple[bool, list[str]]:
    """Check if any hard gate dimensions fail. Returns (passed, failed_dims)."""
    hard_gates = profile.get("hard_gates", [])
    failed = []
    for dim in hard_gates:
        score = scores.get(dim, 0)
        if score == 0:
            for s_dim, s_val in scores.items():
                if dim.lower() in s_dim.lower() or s_dim.lower() in dim.lower():
                    score = s_val
                    break
        if score < HARD_GATE_THRESHOLD:
            failed.append(f"{dim}={score}")
    return len(failed) == 0, failed


# ─── Prompts ─────────────────────────────────────────────────────────────────

def generator_prompt_iter1(task: str, artifact_type: str) -> tuple[str, str]:
    """Build Generator system + user prompt for iteration 1."""
    system = (
        f"You are the GENERATOR in an adversarial refinement loop. "
        f"Produce a comprehensive, production-quality {artifact_type}. "
        f"Be thorough, specific, and measurable. A strict Discriminator will evaluate your output."
    )
    return system, task


def generator_prompt_iter_n(task: str, artifact_type: str,
                            prev_artifact: str, feedback: str, iteration: int) -> tuple[str, str]:
    """Build Generator system + user prompt for iteration 2+."""
    system = (
        f"You are the GENERATOR in an adversarial refinement loop (iteration {iteration}). "
        f"IMPROVE the artifact based on Discriminator feedback. Fix every issue. Do not regress."
    )
    user = (
        f"ORIGINAL TASK:\n{task}\n\n"
        f"PREVIOUS ARTIFACT:\n{prev_artifact[:3000]}...\n[truncated for context]\n\n"
        f"DISCRIMINATOR FEEDBACK:\n{feedback}\n\n"
        f"Produce an IMPROVED version fixing ALL identified issues."
    )
    return system, user


def discriminator_prompt(artifact_summary: str, rubric_table: str,
                         iteration: int, max_iter: int,
                         prev_score: float = 0, prev_issues: str = "") -> tuple[str, str]:
    """Build Discriminator system + user prompt."""
    system = (
        "You are the DISCRIMINATOR. Evaluate the artifact against the rubric. "
        "Score honestly — 5/10 means mediocre. Be specific in evidence."
    )
    context = ""
    if iteration > 1:
        context = (
            f"\nIteration: {iteration} of {max_iter}\n"
            f"Previous score: {prev_score}/10\n"
            f"Previous issues:\n{prev_issues}\n"
            f"Check whether fixes are genuine.\n"
        )

    user = (
        f"## Rubric\n{rubric_table}\n\n"
        f"## Artifact to Evaluate\n{artifact_summary}\n\n"
        f"{context}"
        f"## Output Format\n"
        f"SCORES:\n- [Dimension]: X/10 — [evidence]\n...\n\n"
        f"WEIGHTED_AVERAGE: X.X/10\n"
        f"HARD_GATE_STATUS: PASS or FAIL\n"
        f"TOP_ISSUES:\n1. issue → FIX: fix\n2. issue → FIX: fix\n3. issue → FIX: fix\n"
        f"CONVERGENCE: CONVERGE or ITERATE\nREASONING: one sentence"
    )
    return system, user


# ─── Display ─────────────────────────────────────────────────────────────────

def print_header(text: str):
    bar = "═" * 60
    print(f"\n{bar}")
    print(f"  {text}")
    print(bar)


def print_iteration(result: IterationResult, profile: dict):
    print(f"\n  ╭─ Iteration {result.iteration} {'─' * 40}")
    print(f"  │ Weighted Average: {result.weighted_avg}/10")
    print(f"  │ Hard Gates: {result.hard_gate_status}")
    print(f"  │ Decision: {result.convergence}")
    print(f"  │ Gen tokens: {result.gen_tokens.input_tokens:,} in / {result.gen_tokens.output_tokens:,} out")
    print(f"  │ Disc tokens: {result.disc_tokens.input_tokens:,} in / {result.disc_tokens.output_tokens:,} out")
    print(f"  │ Wall time: {result.wall_time_sec:.1f}s")
    if result.scores:
        print(f"  │")
        for dim, score in result.scores.items():
            bar = "█" * int(score) + "░" * (10 - int(score))
            status = "✅" if score >= 8 else "⚠️" if score >= 6 else "❌"
            print(f"  │ {status} {dim:<22} {bar} {score}/10")
    if result.top_issues:
        print(f"  │")
        print(f"  │ Top Issues:")
        for i, issue in enumerate(result.top_issues[:3], 1):
            print(f"  │   {i}. {issue[:80]}")
    print(f"  ╰{'─' * 50}")


def print_summary(iterations: list[IterationResult], profile_name: str, threshold: float):
    total_tokens = TokenUsage()
    for it in iterations:
        total_tokens.input_tokens += it.gen_tokens.input_tokens + it.disc_tokens.input_tokens
        total_tokens.output_tokens += it.gen_tokens.output_tokens + it.disc_tokens.output_tokens

    total_time = sum(it.wall_time_sec for it in iterations)
    final = iterations[-1]

    print_header("FINAL SUMMARY")
    print(f"  Profile:              {profile_name}")
    print(f"  Threshold:            {threshold}/10")
    print(f"  Iterations used:      {len(iterations)}")
    print(f"  Final score:          {final.weighted_avg}/10")
    print(f"  Hard gates:           {final.hard_gate_status}")
    converged = final.weighted_avg >= threshold and final.hard_gate_status == "PASS"
    print(f"  Converged:            {'✅ YES' if converged else '⚠️ NO (best-of-N selected)'}")
    print(f"")
    print(f"  Token Usage:")
    print(f"    Input:              {total_tokens.input_tokens:,}")
    print(f"    Output:             {total_tokens.output_tokens:,}")
    print(f"    Total:              {total_tokens.total:,}")
    print(f"    Est. cost (@ $3/$15 per M): ${total_tokens.input_tokens * 3 / 1_000_000 + total_tokens.output_tokens * 15 / 1_000_000:.3f}")
    print(f"")
    print(f"  Wall time:            {total_time:.1f}s")
    print(f"")
    if len(iterations) > 1:
        print(f"  Trajectory:")
        for it in iterations:
            print(f"    Iter {it.iteration}: {it.weighted_avg}/10 → {it.convergence}")
    print(f"{'═' * 60}\n")


# ─── Main Loop ───────────────────────────────────────────────────────────────

def run_gan_loop(
    task: str,
    input_file: str | None,
    provider: str,
    base_url: str,
    api_key: str,
    model: str,
    profile_name: str,
    threshold: float,
    max_iterations: int,
    delta_threshold: float,
    rubric_dir: Path,
    output_file: str | None,
) -> list[IterationResult]:

    profile = PROFILES.get(profile_name)
    if not profile:
        print(f"ERROR: Unknown profile '{profile_name}'. Available: {', '.join(PROFILES.keys())}")
        sys.exit(1)

    rubric_table = build_rubric_table(profile)
    artifact_type = "PRD" if "prd" in profile_name else "code module"

    # Load input artifact if provided
    if input_file:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_file}")
            sys.exit(1)
        task = f"Refine the following artifact:\n\n{input_path.read_text(encoding='utf-8')}"

    print_header(f"GAN Artifact Generator — {profile_name}")
    print(f"  Model:     {model}")
    print(f"  Provider:  {provider}")
    print(f"  Threshold: {threshold}/10")
    print(f"  Max iter:  {max_iterations}")

    iterations: list[IterationResult] = []
    current_artifact = ""
    feedback_text = ""

    with httpx.Client() as client:
        for i in range(1, max_iterations + 1):
            iter_start = time.time()

            # ── Generator ──
            print(f"\n  ⏳ Iteration {i}/{max_iterations}: Generating...")
            if i == 1:
                gen_sys, gen_user = generator_prompt_iter1(task, artifact_type)
            else:
                gen_sys, gen_user = generator_prompt_iter_n(
                    task, artifact_type, current_artifact, feedback_text, i
                )

            gen_text, gen_usage = call_llm(
                client, provider, base_url, api_key, model, gen_sys, gen_user
            )
            current_artifact = gen_text

            # ── Discriminator ──
            print(f"  ⏳ Iteration {i}/{max_iterations}: Evaluating...")
            prev_score = iterations[-1].weighted_avg if iterations else 0
            prev_issues = "\n".join(iterations[-1].top_issues) if iterations else ""

            disc_sys, disc_user = discriminator_prompt(
                current_artifact[:6000],  # truncate for context window
                rubric_table, i, max_iterations, prev_score, prev_issues,
            )

            disc_text, disc_usage = call_llm(
                client, provider, base_url, api_key, model, disc_sys, disc_user, max_tokens=3000
            )
            feedback_text = disc_text

            # ── Parse ──
            parsed = parse_discriminator_output(disc_text)
            computed_avg = compute_weighted_avg(parsed["scores"], profile)
            # Prefer Discriminator's self-reported avg, fallback to computed
            w_avg = parsed["weighted_avg"] if parsed["weighted_avg"] > 0 else computed_avg
            gates_pass, gates_failed = check_hard_gates(parsed["scores"], profile)

            iter_time = time.time() - iter_start

            result = IterationResult(
                iteration=i,
                artifact=current_artifact,
                scores=parsed["scores"],
                weighted_avg=w_avg,
                hard_gate_status="PASS" if gates_pass else f"FAIL: {', '.join(gates_failed)}",
                convergence=parsed["convergence"],
                top_issues=parsed["top_issues"],
                reasoning=parsed["reasoning"],
                gen_tokens=gen_usage,
                disc_tokens=disc_usage,
                wall_time_sec=iter_time,
            )
            iterations.append(result)
            print_iteration(result, profile)

            # ── Arbiter ──
            if w_avg >= threshold and gates_pass:
                result.convergence = "CONVERGE"
                print(f"\n  ✅ CONVERGED at iteration {i} ({w_avg}/10 ≥ {threshold})")
                break

            if not gates_pass:
                print(f"\n  🚫 Hard gate failure: {', '.join(gates_failed)} — MUST ITERATE")
                continue

            if i >= 2 and len(iterations) >= 2:
                prev = iterations[-2].weighted_avg
                if prev > 0:
                    delta = (w_avg - prev) / prev
                    if 0 <= delta < delta_threshold:
                        result.convergence = "EARLY_EXIT"
                        print(f"\n  ⏹ Delta {delta:.1%} < {delta_threshold:.0%} — EARLY EXIT (best-of-N)")
                        break

            if i == max_iterations:
                result.convergence = "BEST_OF_N"
                print(f"\n  ⚠️ Max iterations reached — selecting best-of-{i}")

    # Select best artifact
    best = max(iterations, key=lambda x: x.weighted_avg)
    if best.iteration != iterations[-1].iteration:
        print(f"  📌 Best iteration was #{best.iteration} ({best.weighted_avg}/10)")

    # Save output
    if output_file:
        Path(output_file).write_text(best.artifact, encoding="utf-8")
        print(f"\n  💾 Artifact saved to: {output_file}")

    print_summary(iterations, profile_name, threshold)

    # Save JSON results
    results_file = f"gan-results-{int(time.time())}.json"
    results_json = {
        "task": task[:200],
        "profile": profile_name,
        "model": model,
        "provider": provider,
        "threshold": threshold,
        "iterations": [
            {
                "iteration": it.iteration,
                "weighted_avg": it.weighted_avg,
                "scores": it.scores,
                "hard_gate_status": it.hard_gate_status,
                "convergence": it.convergence,
                "top_issues": it.top_issues,
                "gen_tokens": {"input": it.gen_tokens.input_tokens, "output": it.gen_tokens.output_tokens},
                "disc_tokens": {"input": it.disc_tokens.input_tokens, "output": it.disc_tokens.output_tokens},
                "wall_time_sec": it.wall_time_sec,
            }
            for it in iterations
        ],
        "total_tokens": sum(it.gen_tokens.total + it.disc_tokens.total for it in iterations),
        "converged": best.weighted_avg >= threshold and best.hard_gate_status == "PASS",
    }
    Path(results_file).write_text(json.dumps(results_json, indent=2), encoding="utf-8")
    print(f"  📊 Results saved to: {results_file}")

    return iterations


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GAN Artifact Generator — Adversarial refinement via API calls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --task "Write a PRD for rate limiting middleware" --profile prd-default
  %(prog)s --input my-prd.md --profile prd-default --threshold 9.0
  %(prog)s --task "Write a Python rate limiter" --profile production-code --provider anthropic
        """,
    )
    parser.add_argument("--task", help="Task description for artifact generation")
    parser.add_argument("--input", help="Path to existing artifact to refine")
    parser.add_argument("--output", help="Path to save the final artifact")
    parser.add_argument("--profile", default="prd-default",
                        choices=list(PROFILES.keys()),
                        help="Rubric profile (default: prd-default)")
    parser.add_argument("--threshold", type=float, default=8.0,
                        help="Convergence threshold (default: 8.0)")
    parser.add_argument("--max-iterations", type=int, default=3,
                        help="Maximum iterations (default: 3)")
    parser.add_argument("--delta-threshold", type=float, default=0.05,
                        help="Delta early-exit threshold (default: 0.05)")
    parser.add_argument("--provider", default=os.environ.get("GAN_PROVIDER", "openai"),
                        choices=["openai", "anthropic"],
                        help="LLM provider (default: openai, or GAN_PROVIDER env)")
    parser.add_argument("--model", default=os.environ.get("GAN_MODEL", "gpt-4o"),
                        help="Model name (default: gpt-4o, or GAN_MODEL env)")
    parser.add_argument("--api-key", default=os.environ.get("GAN_API_KEY"),
                        help="API key (default: GAN_API_KEY env)")
    parser.add_argument("--api-base", default=os.environ.get("GAN_API_BASE", "https://api.openai.com/v1"),
                        help="API base URL (default: GAN_API_BASE env)")
    parser.add_argument("--rubric-dir", default=str(Path(__file__).parent.parent.parent),
                        help="Directory containing rubric .md files")

    args = parser.parse_args()

    if not args.task and not args.input:
        parser.error("Either --task or --input is required")

    if not args.api_key:
        parser.error("API key required. Set GAN_API_KEY env or use --api-key")

    run_gan_loop(
        task=args.task or "",
        input_file=args.input,
        provider=args.provider,
        base_url=args.api_base,
        api_key=args.api_key,
        model=args.model,
        profile_name=args.profile,
        threshold=args.threshold,
        max_iterations=args.max_iterations,
        delta_threshold=args.delta_threshold,
        rubric_dir=Path(args.rubric_dir),
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
