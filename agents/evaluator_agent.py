# Evaluator Agent
# This agent is responsible for evaluating the quality of analysis outputs
# Part of the Evaluator-Optimizer workflow pattern requirement

from __future__ import annotations

from agno.agent import Agent
from agents.config import DEFAULT_AGENT_KWARGS


# Evaluator Agent Implementation
# This agent:
# 1. Evaluates analysis quality (completeness, accuracy, clarity)
# 2. Provides constructive feedback for improvement
# 3. Works with Investment Research Agent for iterative refinement
# 4. Implements the Evaluator-Optimizer workflow pattern

EVAL_THRESH = 4.0

evaluator_agent = Agent(
    name="Evaluator Agent",
    instructions=[
        "You are an evaluation agent for financial research outputs.",
        "Evaluate drafts for completeness, accuracy, and clarity.",
        "Provide actionable feedback with specific, constructive suggestions.",
        "If data is missing or uncertain, recommend concrete next steps to resolve gaps.",
        "Always return a JSON object with this schema:",
        "{"
        '  "scores": {"factuality": float, "coverage": float, "relevance": float, "actionability": float, "overall": float},'
        '  "feedback": {"strengths": [str], "gaps": [str], "suggestions": [str]},'
        '  "actions": {"priority_fixes": [str], "checks": [str], "followups": [str]},'
        '  "ready_for_delivery": bool'
        "}",
        "Scores must be 0.0-5.0. The 'overall' is the mean of the four dimensions.",
        f"Mark 'ready_for_delivery' true only if overall ≥ {EVAL_THRESH}.",
        "Be objective, concise, and specific. Keep JSON compact.",
    ],
    add_datetime_to_context=True,
    markdown=True,
    **DEFAULT_AGENT_KWARGS,
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        evaluator_agent.print_response(user_input)
