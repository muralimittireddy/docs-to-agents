from ingest import load_raw_documents
from chunking import chunk_documents
from indexes import RepoIndexes
from tools import SearchTools
from agent import build_agent
from logs import log_interaction_to_file
from eval import eval_agent, evaluate_log_record

import asyncio

from dotenv import load_dotenv
load_dotenv()

async def main():
    print('started')
    docs = load_raw_documents()
    print('docs loaded')
    chunks = chunk_documents(docs)
    print('chunking completed')
    indexes = RepoIndexes(chunks)
    print('indexes done')
    tools = SearchTools(indexes)
    print('in hybrid search and going to agents')
    agent = build_agent(tools)
    

    print("\nReady to answer your questions!")
    print("Type 'stop' to exit the program.\n")

    while True:
        question = input("Your question: ")
        if question.strip().lower() == 'stop':
            print("Goodbye!")
            break

        print("Processing your question...")
        response = await agent.run(user_prompt=question)
        print("\nResponse:\n", response.output)
        log_record,log_path =log_interaction_to_file(agent, response.messages)

        # ---------- Evaluation ----------
        evaluation = await evaluate_log_record(eval_agent, log_record)
        print("\nEvaluation Summary:\n", evaluation.summary)

        for check in evaluation.checklist:
            status = "✅" if check.check_pass else "❌"
            print(f"{status} {check.check_name}: {check.justification}")

        print(f"\nLog saved at: {log_path}")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())