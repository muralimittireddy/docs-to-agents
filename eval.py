import json
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel
# ---------- Evaluation prompt ----------

EVALUATION_PROMPT = """
Use this checklist to evaluate the quality of an AI agent's answer (<ANSWER>)
to a user question (<QUESTION>). The full interaction log (<LOG>) is provided.

Checklist:
- instructions_follow
- instructions_avoid
- answer_relevant
- answer_clear
- answer_citations
- completeness
- tool_call_search

Return true/false for each check with a short justification.
""".strip()


# ---------- Output schemas ----------

class EvaluationCheck(BaseModel):
    check_name: str
    justification: str
    check_pass: bool


class EvaluationChecklist(BaseModel):
    checklist: list[EvaluationCheck]
    summary: str


# ---------- Eval agent ----------

eval_model = GeminiModel(
    model_name="gemini-2.5-flash-lite"
)

eval_agent = Agent(
    name="eval_agent",
    model=eval_model,
    instructions=EVALUATION_PROMPT,
    output_type=EvaluationChecklist
)


# ---------- Prompt format ----------

USER_PROMPT_TEMPLATE = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()


# ---------- Log simplification (token-safe) ----------

def simplify_log_messages(messages):
    simplified = []

    for m in messages:
        parts = []
        for p in m["parts"]:
            part = p.copy()
            kind = part["part_kind"]

            if kind in {"user-prompt", "tool-return"}:
                part.pop("timestamp", None)
            if kind in {"tool-call", "tool-return"}:
                part.pop("tool_call_id", None)
            if kind == "tool-return":
                part["content"] = "RETURN_RESULTS_REDACTED"
                part.pop("metadata", None)
            if kind == "text":
                part.pop("id", None)

            parts.append(part)

        simplified.append({"kind": m["kind"], "parts": parts})

    return simplified


# ---------- Main evaluation function ----------

async def evaluate_log_record(eval_agent, log_record):
    messages = log_record["messages"]

    instructions = log_record["system_prompt"]
    question = messages[0]["parts"][0]["content"]
    answer = messages[-1]["parts"][0]["content"]

    log_simplified = simplify_log_messages(messages)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=json.dumps(log_simplified),
    )

    result = await eval_agent.run(user_prompt)
    return result.output
