# Evaluator-Optimizer Workflow
# Implement the Evaluator-Optimizer workflow pattern: Generate analysis → evaluate quality → refine using feedback
# This is one of the three required workflow patterns

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv

from agents.investment_research_agent import investment_research_agent
from agents.evaluator_agent import evaluate_analysis, build_revision_plan

MIN_OVERALL = 0.85
MAX_ITERS   = 1
DEFAULT_RANGE = "3M"

load_dotenv(".env")

def _overall_0to1(scores: Dict[str, Any]) -> float:
    keys = ("completeness", "accuracy", "clarity")
    vals = [float(scores.get(k, 0.0)) for k in keys]
    return sum(vals) / max(len(vals), 1)


def _generate(symbol_or_name: str, date_range: str) -> str:
    """Ask Investment Research Agent for a compact brief (not just a plan)."""
    prompt = (
        "Produce a concise investment research brief for the ticker/company below. "
        "Keep it PDF-friendly (short bullets), and do NOT fabricate data—use 'n/a' if unknown.\n\n"
        f"Symbol/Name: {symbol_or_name}\n"
        f"Date Focus: {date_range} (include last 48h news impact)\n\n"
        "Sections:\n"
        "1) Snapshot (price/3M return/beta/PE/EV/EBITDA/next ER; 'n/a' if missing)\n"
        "2) News (last 48h highlighted) — 3–5 bullets\n"
        "3) Earnings/Filings — 2–3 bullets\n"
        "4) Valuation (multiples and/or simple DCF) — brief\n"
        "5) Bull vs Bear — 2–3 bullets each\n"
        "6) Catalysts & Risks — 3–4 bullets total"
    )
    resp = investment_research_agent.run(prompt)
    return getattr(resp, "content", str(resp))


def _optimize(draft: str, plan_json: Dict[str, Any], symbol_or_name: Optional[str]) -> str:
    """One-shot revise using Investment Research Agent and the evaluator's plan."""
    prompt = (
        "Revise the research brief using this revision plan (JSON). Improve completeness, accuracy, and clarity. "
        "Keep it concise and DO NOT invent numbers; leave 'n/a' where data is missing.\n\n"
        f"== SYMBOL/NAME ==\n{symbol_or_name or 'n/a'}\n\n"
        "== CURRENT DRAFT ==\n"
        f"{draft}\n\n"
        "== REVISION PLAN (JSON) ==\n"
        f"{json.dumps(plan_json, ensure_ascii=False)}\n\n"
        "Return ONLY the revised brief."
    )
    resp = investment_research_agent.run(prompt)
    return getattr(resp, "content", str(resp))


def evaluator_optimizer_workflow(analysis_input: str, *, date_range: str = DEFAULT_RANGE) -> Dict[str, Any]:
    """
    Orchestrates: generate → evaluate → (optional) refine.
    Returns: {'input', 'initial', 'final', 'feedback'}.
    """
    # Implementation steps:
    # Step 1: Generate initial analysis
    # Step 2: Evaluate quality (completeness, accuracy, clarity)
    # Step 3: Refine based on feedback
    # Step 4: Repeat until satisfactory quality
    
    symbol = (analysis_input or "").strip()
    if not symbol:
        raise ValueError("analysis_input must be a non-empty ticker/company string.")

    initial = _generate(symbol, date_range)
    final, feedback = iterative_refinement(initial, max_iterations=MAX_ITERS, symbol_or_name=symbol, min_overall=MIN_OVERALL)

    return {"input": symbol, "initial": initial, "final": final, "feedback": feedback}


def iterative_refinement(
    analysis: str,
    max_iterations: int = MAX_ITERS,
    symbol_or_name: Optional[str] = None,
    min_overall: float = MIN_OVERALL,
) -> Tuple[str, Dict[str, Any]]:
    """
    Evaluate → (if needed) plan → optimize → re-evaluate, up to max_iterations.
    Returns (final_draft, last_feedback_json).
    """
    current = analysis or ""
    feedback: Dict[str, Any] = {}

    for _ in range(max_iterations + 1):  # +1 to always do a final evaluate
        feedback = evaluate_analysis(current)
        # normalize overall if missing
        sc = feedback.get("scores", {})
        if "overall" not in sc:
            feedback.setdefault("scores", {})["overall"] = _overall_0to1(sc)

        if float(feedback["scores"]["overall"]) >= min_overall:
            return current, feedback

        # build plan + optimize (one pass), then loop back for final evaluate
        plan = build_revision_plan(current, feedback)
        improved = _optimize(current, plan, symbol_or_name)
        if not improved or not improved.strip():
            return current, feedback
        current = improved

    return current, feedback

if __name__ == "__main__":
    # tiny smoke test
    result = evaluator_optimizer_workflow("AAPL", date_range=DEFAULT_RANGE)
    print("\n=== FINAL BRIEF (preview) ===\n", result["final"][:1500])
    print("\n=== FEEDBACK (preview) ===\n", json.dumps(result["feedback"], indent=2)[:1500])
