from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

QUESTION_PROMPT = """
You are helping to create test questions for an AI agent that answers questions about a git hub repository.

Based on the provided content, generate realistic questions that students might ask.

The questions should:

- Be natural and varied in style
- Range from simple to complex
- Include both specific technical questions and general course questions

Generate one question for each record.
""".strip()


class QuestionsList(BaseModel):
    questions: list[str]

eval_model = GeminiModel(
    model_name="gemini-2.5-flash-lite"
)

question_generator = Agent(
    name="question_generator",
    model=eval_model,
    instructions=QUESTION_PROMPT,
    output_type=QuestionsList,
)
