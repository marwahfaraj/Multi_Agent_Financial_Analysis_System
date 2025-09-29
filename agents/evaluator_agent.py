# TODO: Team - Evaluator Agent
# This agent will be responsible for evaluating the quality of analysis outputs
# Part of the Evaluator-Optimizer workflow pattern requirement

import json
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from dotenv import load_dotenv
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple


load_dotenv(".env")


# TODO: Team - Implement this agent
# This agent should:
# 1. Evaluate analysis quality (completeness, accuracy, clarity)
# 2. Provide constructive feedback for improvement
# 3. Work with Investment Research Agent for iterative refinement
# 4. Implement the Evaluator-Optimizer workflow pattern

evaluator_agent = Agent(
    name="Evaluator Agent",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "You are an evaluation agent for financial research outputs.",
        "Evaluate drafts for completeness, accuracy, and clarity.",
        "Provide actionable feedback with specific, constructive suggestions.",
        "If data is missing or uncertain, recommend concrete next steps to resolve gaps.",
        "Always return a JSON object with this schema:\n"
        "{"
        '  "scores": {"completeness": float, "accuracy": float, "clarity": float, "overall": float},'
        '  "feedback": {"strengths": [str], "gaps": [str], "suggestions": [str]},'
        '  "actions": {"priority_fixes": [str], "checks": [str], "followups": [str]},'
        '  "ready_for_delivery": bool'
        "}",
        "Scores must be 0.0–1.0. The 'overall' is the mean of the three dimensions.",
        "Mark 'ready_for_delivery' true only if overall ≥ 0.85 and no critical gaps remain.",
        "Be objective, concise, and specific. Generic advice is ok."
    ],
    db=SqliteDb(db_file="evaluator_agent.db"),
    add_datetime_to_context=True,
    markdown=True,
)


def _safe_json_loads(s: str) -> Dict[str, Any]:
    """Best-effort JSON parser with graceful fallback."""
    try:
        return json.loads(s)
    except Exception:
        return {"raw_response": s}

def _compute_overall(scores: Dict[str, float]) -> float:
    """Compute overall as mean of completeness, accuracy, clarity if not provided."""
    keys = ["completeness", "accuracy", "clarity"]
    vals = [float(scores.get(k, 0.0)) for k in keys]
    return sum(vals) / max(len(vals), 1)

def _threshold_met(feedback: Dict[str, Any], min_overall: float = 0.85) -> bool:
    """Decide if optimization is needed."""
    try:
        scores = feedback.get("scores", {})
        overall = float(scores.get("overall", _compute_overall(scores)))
        return overall >= min_overall and not feedback.get("feedback", {}).get("gaps")
    except Exception:
        return False


def build_eval_prompt(draft: str, context: Optional[str] = None) -> str:
    parts = [
        "Evaluate the following financial analysis draft.",
        "Return ONLY the JSON object as per the schema.",
        "",
        "== DRAFT ==",
        draft.strip(),
    ]
    if context and context.strip():
        parts.extend(["", "== CONTEXT ==", context.strip()])
    return "\n".join(parts)

def build_optimizer_prompt(draft: str, eval_json: Dict[str, Any]) -> str:
    return (
        "You are preparing an optimization plan for the Investment Research Agent.\n"
        "Produce a structured revision plan (JSON) with:\n"
        "{"
        ' "objective": str,'
        ' "edits": [{"type": "add|revise|remove", "target": str, "rationale": str, "detail": str}],'
        ' "data_requests": [str],'
        ' "acceptance_criteria": [str]'
        "}\n\n"
        "== CURRENT DRAFT ==\n"
        f"{draft.strip()}\n\n"
        "== EVALUATION ==\n"
        f"{json.dumps(eval_json, indent=2)}\n\n"
        "Return ONLY the JSON object."
    )


def evaluate_analysis(draft: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the evaluator on a draft. Returns parsed JSON feedback (or raw fallback).
    """
    prompt = build_eval_prompt(draft, context)
    resp = evaluator_agent.run(prompt)
    data = _safe_json_loads(getattr(resp, "content", str(resp)))
    if "scores" in data and "overall" not in data["scores"]:
        data["scores"]["overall"] = _compute_overall(data["scores"])
    return data

def build_revision_plan(draft: str, eval_feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce a JSON revision plan (no rewriting yet). Keeps Evaluator separate from generator.
    """
    prompt = build_optimizer_prompt(draft, eval_feedback)
    resp = evaluator_agent.run(prompt)
    return _safe_json_loads(getattr(resp, "content", str(resp)))

def evaluator_optimizer_cycle(
    draft: str,
    context: Optional[str] = None,
    symbol_or_name: Optional[str] = None,
    max_rounds: int = 2,
    min_overall: float = 0.85,
) -> Tuple[str, Dict[str, Any]]:
    """
    Minimal Evaluator-Optimizer loop:
      1) Evaluate draft
      2) If threshold not met, build plan & optimize with Investment Research Agent
      3) Re-evaluate the new draft
    Returns (final_draft, last_feedback_json)
    """
    current = draft
    last_feedback = {}

    for _ in range(max_rounds):
        last_feedback = evaluate_analysis(current, context)
        if _threshold_met(last_feedback, min_overall=min_overall):
            return current, last_feedback

        plan = build_revision_plan(current, last_feedback)
        # optimize_with_investment_agent(current, plan, symbol_or_name)
        # TO-DO: Call agent to optimize with
        improved = "not available" 
        # If optimizer not available or returns empty, stop gracefully
        if not improved or "not available" in improved.lower():
            return current, last_feedback
        current = improved

    # Final evaluation after last round
    last_feedback = evaluate_analysis(current, context)
    return current, last_feedback


if __name__ == "__main__":
    print("Evaluator Agent (type 'exit' to quit)")
    count = 0
    while count <1:
        user_input = input("Paste draft to evaluate (or 'exit'): ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        result = evaluate_analysis(user_input)
        print(json.dumps(result, indent=2))
        # Suggest next step if below threshold
        if not _threshold_met(result):
            print("\nOverall < 0.85 — generating a revision plan...")
            plan = build_revision_plan(user_input, result)
            print(json.dumps(plan, indent=2))
            print("\nCall optimize_with_investment_agent(draft, plan) to produce a revised draft.")
        count = count +1
