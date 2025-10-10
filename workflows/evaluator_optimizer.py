# Evaluator-Optimizer Workflow
# Implement the Evaluator-Optimizer workflow pattern: Generate analysis → evaluate quality → refine using feedback
# This is one of the three required workflow patterns

from __future__ import annotations

import json
import re
import types
import uuid
from agno.workflow import Loop, Step, StepInput, StepOutput
from agents.investment_research_agent import investment_research_agent
from agents.evaluator_agent import evaluator_agent

# Threshold score (0–1) required to consider a draft "ready" without further optimization.
READY_THRESHOLD = 0.85

# Delimiter used to concatenate the pre-eval display block with the draft text in one payload.
_PRE_EVAL_MARK = "\n\n===DRAFT_BELOW==="


# Formats the evaluator's feedback.
def _format_eval_matrix(feedback: dict) -> str:
    scores = feedback.get("scores", {}) or {}
    # Extract completeness score; default to 0.0 if missing; cast to float for math/formatting.
    comp = float(scores.get("completeness", 0.0))
    # Extract accuracy score
    acc = float(scores.get("accuracy", 0.0))
    # Extract clarity score
    clr = float(scores.get("clarity", 0.0))
    # Compute overall if not provided: mean of the three scores when any are present
    ovl = float(
        scores.get("overall", (comp + acc + clr) / 3 if any([comp, acc, clr]) else 0.0)
    )
    # Extract gap messages (what's missing) to display
    gaps = feedback.get("feedback", {}).get("gaps", []) or []

    rows = [
        # Header row for the table.
        "| Metric        | Score |",
        "|--------------|-------|",
        f"| Completeness | {comp:.2f} |",
        f"| Accuracy     | {acc:.2f} |",
        f"| Clarity      | {clr:.2f} |",
        f"| **Overall**  | **{ovl:.2f}** |",
        "",
        "#### Gaps",
        # print gaps as a bullet list; show placeholder if there are none.
        "- " + "\n- ".join(gaps) if gaps else "_None detected_",
    ]
    return "\n".join(rows), ovl


# Normalize any Agno step context into plain text for downstream steps.
def _extract_text_from_ctx(ctx, *, prefer_longest_from_lists: bool = True) -> str:
    """
    Normalize Agno step contexts to a plain string for downstream steps.

    Handles:
      - StepInput: prefer .previous_step_content (the upstream result) over .content (the current payload)
      - StepOutput: use .content
      - list of StepOutputs/strings/dicts (e.g., from Parallel): pick the longest text (default) so we prefer
        the synthesized analysis over short acknowledgements (like memory "Noted..."), or use last item if configured
      - anything else: return str(ctx) as a safe fallback

    Args:
      prefer_longest_from_lists: when True (default), select the longest string from list contexts; when False,
                                 fall back to using the last meaningful list item.

    Returns:
      A best-effort string representing the textual content we want to evaluate/optimize/print.
    """

    # Check for StepInput-like objects: these usually have both .previous_step_content and .content attributes.
    #  prefer .previous_step_content because it carries the *output* of the prior step.
    if hasattr(ctx, "previous_step_content") or hasattr(ctx, "content"):
        # Return the previous step's content if available; otherwise use current content; else empty string.
        return (
            getattr(ctx, "previous_step_content", None)
            or getattr(ctx, "content", "")
            or ""
        )

    # If it's StepOutput-like (has a .content attribute) but not StepInput, just return that content.
    if hasattr(ctx, "content"):
        # Guard with "or ''" so callers never get None.
        return getattr(ctx, "content") or ""

    # If the context is a list (common after Parallel), then decide which element's text to pass along.
    if isinstance(ctx, list) and ctx:
        # If  prefer the longest text, capture the synthesized analysis instead of a short ack.
        if prefer_longest_from_lists:
            # Initialize "best" as empty string to compare lengths safely.
            best = ""
            # Iterate through each item in the list to select the longest content.
            for item in ctx:
                # If the item looks like StepOutput with a string .content, consider it.
                if hasattr(item, "content") and isinstance(item.content, str):
                    # Update "best" when we find a longer string.
                    if len(item.content) > len(best):
                        best = item.content
                # If the item is a plain string, also consider and compare lengths.
                elif isinstance(item, str):
                    if len(item) > len(best):
                        best = item
                # If the item is a dict with a string 'content' key (some event shapes), consider it too.
                elif isinstance(item, dict) and isinstance(item.get("content"), str):
                    if len(item["content"]) > len(best):
                        best = item["content"]
            # Return whichever candidate ended up longest (may still be empty if no text found).
            return best
        else:
            # Alternative policy: walk from the end and pick the last meaningful content (sometimes desired).
            for item in reversed(ctx):
                # Prefer StepOutput-like items with string .content.
                if hasattr(item, "content") and isinstance(item.content, str):
                    return item.content or ""
                # Next, accept plain strings.
                if isinstance(item, str):
                    return item
                # Finally, accept dicts that carry a string 'content'.
                if isinstance(item, dict) and isinstance(item.get("content"), str):
                    return item["content"] or ""
            # If the list had no usable text, return empty string.
            return ""

    # Fallback: for any other unexpected shape (None, numbers, custom objects), return a safe string form.
    return str(ctx or "")


# Agno executor step that displays pre-optimization scores and passes draft forward.
def show_pre_eval_metrics_executor(step_input) -> StepOutput:
    # Extract the synthesized draft text from prior steps (handles StepInput/list/etc.).
    draft = _extract_text_from_ctx(step_input)
    # Call the evaluator agent to get structured feedback on the draft.
    feedback = _evaluate(draft)
    # Format the feedback into a markdown table and get numeric overall.
    matrix_md, ovl = _format_eval_matrix(feedback)
    # Embed the overall score as a parsable marker so later steps can read it without re-evaluating.
    meta = f"\n\n===PRE_EVAL_OVERALL={ovl:.4f}==="
    # Compose the step output: the visible matrix, then meta marker, then our delimiter, then the draft.
    content = (
        "### Pre-Optimization Evaluation\n"
        + matrix_md
        + meta
        + _PRE_EVAL_MARK
        + "\n"
        + draft
    )
    # Return as StepOutput so Agno prints it in a boxed step and forwards the content.
    return StepOutput(content=content)


# Normalizes any Agent.run(...) response (object/string/generator/list/chunks) into plain text.
def _to_text(resp) -> str:
    # If the response has a .content attribute (Agno message object), use it directly.
    if hasattr(resp, "content"):
        return resp.content
    # If it's already a string, return as-is.
    if isinstance(resp, str):
        return resp
    # If it's a dict (e.g., event chunk), try common keys; otherwise stringify.
    if isinstance(resp, dict):
        return resp.get("content") or resp.get("delta") or str(resp)
    # If it's a generator/iterable (streaming), consume and concatenate all parts.
    if isinstance(resp, types.GeneratorType) or hasattr(resp, "__iter__"):
        # Accumulate chunks to form the full text.
        parts = []
        try:
            # Iterate through chunks safely; support multiple shapes.
            for chunk in resp:
                # Prefer chunk.content if present.
                if hasattr(chunk, "content"):
                    parts.append(chunk.content)
                # Otherwise, if chunk is a string, append it.
                elif isinstance(chunk, str):
                    parts.append(chunk)
                # For dict chunks, try common text-bearing keys.
                elif isinstance(chunk, dict):
                    parts.append(chunk.get("content") or chunk.get("delta") or "")
                # Fallback: stringify unknown shapes.
                else:
                    parts.append(str(chunk))
        except Exception:
            # Swallow iteration errors to avoid failing the whole step.
            pass
        # Join and trim the final text.
        return "".join(parts).strip()
    # Final fallback: stringify arbitrary objects.
    return str(resp)


# Computes an overall score as the mean of completeness/accuracy/clarity.
def _compute_overall(scores: dict) -> float:
    # Define the three dimensions we average.
    keys = ["completeness", "accuracy", "clarity"]
    # Extract each score as float with default 0.0.
    vals = [float(scores.get(k, 0.0)) for k in keys]
    # Avoid divide-by-zero by max(len(vals), 1).
    return sum(vals) / max(len(vals), 1)


#  Parse strict JSON from potentially messy LLM output
def _json_from_messy(text: str):
    # Remove code fences like ```json to increase chance of a clean parse.
    cleaned = "\n".join(
        line for line in (text or "").splitlines() if not line.strip().startswith("```")
    ).strip()
    # First attempt: direct JSON parse of the cleaned string.
    try:
        return json.loads(cleaned)
    except Exception:
        # Ignore and try extracting a JSON object substring below.
        pass
    # Find the largest {...} blocks using a permissive regex across newlines.
    m = re.findall(r"\{[\s\S]*\}", cleaned)
    # If any candidates exist, try them from the end (often the last block is complete).
    if m:
        for block in reversed(m):
            try:
                # Try parsing the candidate block.
                return json.loads(block)
            except Exception:
                # Attempt minor repairs (remove trailing commas) and re-parse.
                repaired = block.replace(",]", "]").replace(",}", "}")
                try:
                    return json.loads(repaired)
                except Exception:
                    # Continue trying earlier blocks.
                    continue
    # If nothing parsed, return a sentinel with the raw text for debugging.
    return {"raw_response": text}


EVAL_SCHEMA_JSON = """{
  "scores": {
    "completeness": 0.0,
    "accuracy": 0.0,
    "clarity": 0.0,
    "overall": 0.0
  },
  "feedback": {
    "strengths": [],
    "gaps": [],
    "suggestions": []
  },
  "actions": {
    "priority_fixes": [],
    "checks": [],
    "followups": []
  },
  "ready_for_delivery": false
}"""


# Calls the evaluator agent to score a draft and returns parsed JSON (with 'overall' ensured).
def _evaluate(draft: str) -> dict:
    # Build an instruction that asks strictly for the JSON schema on the provided draft.
    prompt = (
        "Evaluate the following financial analysis draft.\n"
        "Return ONLY a valid JSON object matching this exact schema (no prose, no code fences):\n"
        f"{EVAL_SCHEMA_JSON}\n\n"
        "Rules:\n"
        "- scores.* must be within [0.0, 1.0]\n"
        "- scores.overall = mean(completeness, accuracy, clarity)\n"
        "- If unsure about a score, use a conservative value (e.g., 0.0–0.3) and list the reason in feedback.gaps\n"
        "- Keep arrays concise and specific\n\n"
        "== DRAFT ==\n" + (draft or "").strip()
    )
    # Run the evaluator agent non-streaming to simplify parsing.
    resp = evaluator_agent.run(prompt, stream=False, session_id=str(uuid.uuid4()))
    # Normalize the agent response (handles strings/generators/chunks) into plain text.
    raw = _to_text(resp)
    # Parse robustly into JSON, repairing if needed.
    data = _json_from_messy(raw)
    # If scores exist but 'overall' is missing, compute it to keep downstream logic simple.
    if isinstance(data, dict) and "scores" in data and "overall" not in data["scores"]:
        data["scores"]["overall"] = _compute_overall(data["scores"])
    # Return the structured feedback.
    return data


# Returns True if feedback meets readiness (overall >= READY_THRESHOLD and no 'gaps'); else False.
def _is_ready(feedback: dict, min_overall: float = READY_THRESHOLD) -> bool:
    try:
        # Safely read the scores object; default empty to avoid exceptions.
        scores = feedback.get("scores", {})
        # Pull 'overall' if present; otherwise compute from components.
        overall = float(scores.get("overall", _compute_overall(scores)))
        # Identify any remaining gaps (missing or weak areas) from feedback.
        gaps = feedback.get("feedback", {}).get("gaps", [])
        # Ready when overall meets threshold and evaluator reported no gaps.
        return overall >= min_overall and not gaps
    except Exception:
        # Be conservative on any parsing/computation error.
        return False


# Threshold below which we allow optimization (≤ 0.50 means "too weak, optimize").
OPT_GATE_THRESHOLD = 0.50
# Marker used to tell the optimizer loop to skip optimization entirely.
SKIP_OPT_MARK = "===SKIP_OPTIMIZATION==="


# Decides whether to run optimization based on pre-eval overall score; passes draft forward accordingly.
def gate_optimization_executor(step_input) -> StepOutput:
    mixed = _extract_text_from_ctx(step_input)

    if _PRE_EVAL_MARK in mixed:
        draft = mixed.split(_PRE_EVAL_MARK, 1)[1].lstrip()
    else:
        draft = mixed

    # Try to parse marker: ===PRE_EVAL_OVERALL=<number>===
    marker = "===PRE_EVAL_OVERALL="
    overall = None
    i = mixed.find(marker)
    if i != -1:
        j = mixed.find("===", i + len(marker))
        if j != -1:
            overall_str = mixed[i + len(marker) : j].strip()
            try:
                overall = float(overall_str)
            except Exception:
                overall = None

    # Fallback: if marker not found or parse failed, evaluate now
    if overall is None:
        fb = _evaluate(draft)
        scores = fb.get("scores", {}) or {}
        overall = float(scores.get("overall", 0.0))

    if overall <= OPT_GATE_THRESHOLD:
        decision_banner = f"**Optimization Gate:** overall={overall:.2f} ≤ {OPT_GATE_THRESHOLD:.2f} → *OPTIMIZE*"
        return StepOutput(content=decision_banner + "\n\n" + draft)
    else:
        decision_banner = f"**Optimization Gate:** overall={overall:.2f} > {OPT_GATE_THRESHOLD:.2f} → *SKIP*"
        return StepOutput(
            content=decision_banner + "\n\n" + SKIP_OPT_MARK + "\n" + draft
        )


# Loop stop condition: stop immediately if SKIP marker present; else evaluate and check readiness.
def evaluator_end_condition(ctx) -> bool:
    # Normalize ctx to get the current text under evaluation.
    current_text = _extract_text_from_ctx(ctx)
    # If previous step requested skipping optimization, stop the loop right away.
    if current_text.lstrip().startswith(SKIP_OPT_MARK):
        return True
    # Run evaluator on the current draft content.
    feedback = _evaluate(current_text)
    # show the scores block for visibility.
    print("[LOOP] end_condition: scores =", feedback.get("scores"))
    # Return True to stop if the draft meets quality threshold and has no gaps; otherwise continue.
    return _is_ready(feedback, READY_THRESHOLD)


# Optimizer step: either skip (when marked) or ask the research agent to rewrite and then re-evaluate.
def optimizer_executor(step_input: StepInput) -> StepOutput:
    # Get the working text from the loop (could include the skip marker).
    text = _extract_text_from_ctx(step_input).lstrip()

    # Fast path: if gate said to skip, keep the draft and attach one evaluation for loop termination.
    if text.startswith(SKIP_OPT_MARK):
        # Remove the skip marker line and keep the remaining draft.
        draft = text.split("\n", 1)[1] if "\n" in text else ""
        # Evaluate once so the loop condition has scores to inspect.
        feedback_after = _evaluate(draft)
        # Annotate the draft with evaluation JSON and a note indicating we skipped optimization.
        annotated = (
            draft
            + "\n\n=== Evaluation Feedback ===\n"
            + json.dumps(feedback_after, indent=2)
            + "\n\n(Optimization skipped because overall > 0.50)"
        )
        # Return annotated content (draft + feedback) so the next end_condition can stop cleanly.
        return StepOutput(content=annotated)

    # If previous iteration already appended a feedback block, strip it before rewriting.
    parts = text.rsplit("=== Evaluation Feedback ===", 1)
    # Keep only the pure draft for the optimizer prompt.
    draft_only = parts[0].strip()

    # If there was prior feedback, try to parse it and pass as guidance to the optimizer.
    prior_feedback = {}
    if len(parts) == 2:
        try:
            prior_feedback = json.loads(parts[1])
        except Exception:
            # If it wasn't valid JSON, ignore gracefully.
            prior_feedback = {}

    # Construct an instruction for the Investment Research Agent to directly rewrite the draft.
    optimizer_prompt = "\n".join(
        [
            # Set the role and expectation (rewrite, not meta-plan).
            "You are improving the following financial research draft.",
            # Clarify concrete goals to align the rewrite.
            "Goals:",
            "- Address all gaps and priority fixes.",
            "- Improve completeness, accuracy, and clarity.",
            "- Keep structure tight; use headings and bullets sparingly.",
            "",
            # Provide the draft text.
            "== DRAFT ==",
            draft_only,
            "",
            # Provide the prior evaluation JSON to steer the revision.
            "== EVALUATION JSON ==",
            json.dumps(prior_feedback, indent=2),
            "",
            # Force a direct revised report as the output.
            "== INSTRUCTIONS ==",
            "Rewrite the draft, directly producing the improved report with the fixes applied.",
            "Do not output a plan—output the revised analysis only.",
        ]
    )

    # Ask the research agent for the improved draft; non-streaming avoids generator handling here.
    improved_resp = investment_research_agent.run(optimizer_prompt, stream=False)
    # Normalize the agent response to plain text.
    improved_text = _to_text(improved_resp)
    # Evaluate the improved draft so the loop has fresh metrics for the end condition.
    feedback_after = _evaluate(improved_text)
    # Attach the evaluation block to the improved draft (loop checks this next).
    annotated = (
        improved_text
        + "\n\n=== Evaluation Feedback ===\n"
        + json.dumps(feedback_after, indent=2)
    )
    # Return annotated text to the loop.
    return StepOutput(content=annotated)


# Final step to print a clean report (without attached evaluation JSON) in an Agno-styled box.
def finalize_print_executor(step_input) -> StepOutput:
    # Extract the latest content (likely improved draft + evaluation block).
    text = _extract_text_from_ctx(step_input)
    # Strip the evaluation block so end-users see only the polished report.
    cleaned = text.split("\n\n=== Evaluation Feedback ===", 1)[0].strip()
    # Return the cleaned report; Agno will render it in a boxed step.
    return StepOutput(content=cleaned)


# Agno Loop that runs the optimizer step repeatedly until the end condition says stop.
eval_opt_loop = Loop(
    # Give the loop a descriptive name for logging.
    name="EvaluatorOptimizer Loop",
    steps=[Step(name="Optimize Draft", executor=optimizer_executor)],
    # This function is called after each iteration to decide whether to continue or stop.
    end_condition=evaluator_end_condition,
    # Cap the number of iterations to avoid runaway loops (1 = single pass optimization).
    max_iterations=1,
)
