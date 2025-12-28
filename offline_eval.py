import json
import random
import pandas as pd
from tqdm.auto import tqdm
from pathlib import Path
import asyncio
import time
import os
from logs import log_interaction_to_file, LOG_DIR
from eval import eval_agent, evaluate_log_record
from question_generation import question_generator
from ingest import load_raw_documents
from chunking import chunk_documents
from indexes import RepoIndexes
from tools import SearchTools
from agent import build_agent
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# LOG_DIR = Path("logs")
MAX_RPM = 4
LLM_INTERVAL_SECONDS = 60/MAX_RPM  # 4 RPM => 1 call / 15 sec

_llm_lock = asyncio.Lock()
_last_llm_call_ts = 0.0

async def llm_call(call_fn, max_retries=5):
    """
    Global LLM call executor:
    - Guarantees <= 4 RPM
    - Handles retries safely
    """
    global _last_llm_call_ts

    # ---- Rate limiting (GLOBAL) ----
    async with _llm_lock:
        now = time.time()
        elapsed = now - _last_llm_call_ts

        if elapsed < LLM_INTERVAL_SECONDS:
            wait_time = LLM_INTERVAL_SECONDS - elapsed
            print(f"[RateLimit] Sleeping {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        _last_llm_call_ts = time.time()

    # ---- Retry logic (outside lock) ----
    for attempt in range(1, max_retries + 1):
        try:
            return await call_fn()
        except Exception as e:
            if attempt == max_retries:
                raise
            backoff = 2 ** attempt
            print(f"[Retry {attempt}] backing off {backoff}s")
            await asyncio.sleep(backoff)


def build_repo_agent():
    docs = load_raw_documents()
    chunks = chunk_documents(docs)
    indexes = RepoIndexes(chunks)
    tools = SearchTools(indexes)
    agent = build_agent(tools)
    return agent

async def generate_questions(num_questions=3):
    docs = load_raw_documents()

    # Randomly sample FAQ records
    sample = random.sample(docs, num_questions)

    # Extract text content only
    prompt_docs = []
    for d in sample:
        if isinstance(d, dict):
            prompt_docs.append(d.get("content", ""))
        else:
            prompt_docs.append(d.content)

    prompt = json.dumps(prompt_docs)

    # result = await question_generator.run(prompt)
    result = await llm_call(
        lambda: question_generator.run(prompt)
    )
    return result.output.questions

async def run_agent_on_questions(agent, questions):
    for q in tqdm(questions, desc="Running agent on questions"):

        # async def call_agent():
        #     return await agent.run(user_prompt=q)

        # result = await with_retry(call_agent)

        result = await llm_call(
            lambda: agent.run(user_prompt=q)
        )

        log_interaction_to_file(
            agent,
            result.new_messages(),
            source="ai-generated"
        )

        # small delay to stay under free-tier QPS
        # await asyncio.sleep(0.5)

def load_ai_generated_logs():
    records = []

    for log_file in LOG_DIR.glob("*.json"):
        with log_file.open("r", encoding="utf-8") as f:
            record = json.load(f)
            record["log_file"] = log_file

            if record.get("source") == "ai-generated":
                records.append(record)

    return records

async def evaluate_logs(log_records):
    results = []

    for record in tqdm(log_records, desc="Evaluating logs"):
        # async def call_eval():
        #     return await evaluate_log_record(eval_agent, record)

        # eval_result = await with_retry(call_eval)

        eval_result = await llm_call(
            lambda: evaluate_log_record(eval_agent, record)
        )

        results.append((record, eval_result))
        # eval can be slightly faster
        # await asyncio.sleep(0.3)
    return results

def build_eval_dataframe(eval_results):
    rows = []

    for log_record, eval_result in eval_results:
        messages = log_record["messages"]

        row = {
            "file": log_record["log_file"].name,
            "question": messages[0]["parts"][0]["content"],
            "answer": messages[-1]["parts"][0]["content"],
        }

        for check in eval_result.checklist:
            row[check.check_name] = check.check_pass

        rows.append(row)

    return pd.DataFrame(rows)


async def run_offline_eval():
    print("Building agent...")
    agent = build_repo_agent()

    print("Generating synthetic questions...")
    questions = await generate_questions(num_questions=3)
    # print(f"DEBUG: generated {len(questions)} questions")
    print(f"Generated {len(questions)} questions")
    print(f"passing {questions[:3]} questions")

    print("Running agent on questions...")
    await run_agent_on_questions(agent, questions[:3])

    print("Loading AI-generated logs...")
    log_records = load_ai_generated_logs()

    print("Evaluating logs...")
    eval_results = await evaluate_logs(log_records)

    df = build_eval_dataframe(eval_results)

    print("\nEvaluation averages:\n")
    print(df.mean(numeric_only=True))

    print("\nSample rows:\n")
    print(df.head())

if __name__ == "__main__":
    asyncio.run(run_offline_eval())
