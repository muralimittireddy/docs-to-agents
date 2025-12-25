# agent.py
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from tools import SearchTools

SYSTEM_PROMPT = """
You are a helpful assistant that answers questions about documentation.  

Use the search tool to find relevant information from the GitHub course repository. materials before answering questions.  

If you can find specific information through search, use it to provide accurate answers.

Rules:
- ALWAYS search before answering
- Decide whether the question is about learning material or assignments
- Answer ONLY using retrieved content
- If the search doesn't return relevant results, let the user know and provide general guidance.
"""

def build_agent(search_tools: SearchTools):
    model = GeminiModel(
        model_name="gemini-2.5-flash"
    )
    return Agent(
        name="repo_agent",
        instructions=SYSTEM_PROMPT,
        tools=[
            search_tools.hybrid_search
        ],
        model=model
    )
