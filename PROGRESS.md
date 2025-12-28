# docs-to-agents

This project is part of a **7-day AI Agents crash course**, where the goal is to build a production-style conversational AI agent that understands and answers questions about any GitHub repository (documentation + assignments).

## Tech Stack

- **Python 3.11+**

- **uv** – fast dependency management

- **Gemini API** – LLM backend

- **Pydantic AI** – agent framework

- **minsearch** – lightweight text search

- **Sentence Transformers** – vector embeddings

- **python-frontmatter** – Markdown parsing

## Environment Setup

This project uses **uv** for fast and clean dependency management.

### 1. Install uv

    pip install uv

### 2. Initialize project

    uv init

### 3. Add dependencies

    uv add requests python-frontmatter python-dotenv google-genai minsearch  sentence-transformers pydantic_ai streamlit

    uv add --dev jupyter

### 4. Run Jupyter

    uv run jupyter notebook

### 5. Create .env

    GEMINI_API_KEY = your-api-key-here

### 6. Run the project

    uv run python main.py


## Day 1 – GitHub Repository Ingestion

**Goal**: Safely ingest GitHub repositories for downstream AI processing.

### What this does (Day 1 scope)

- Downloads any GitHub repository ZIP using `codeload.github.com`
- Streams downloads to avoid memory issues
- Retries on transient network failures
- Deletes partial or duplicate ZIP files
- Extracts and parses `.md` files using `python-frontmatter`
- Produces structured raw documents for chunking

### Why this matters

Reliable ingestion is the foundation of any AI system.

If ingestion fails, everything downstream breaks.

---

## Day 2 – Document Chunking Strategies

**Goal**: Convert large documents into meaningful, AI-friendly chunks.

**Explored three approaches**:

- Simple sliding-window chunking
- Section-based splitting using document structure
- AI-powered intelligent chunking

### Final choice

**Section-based chunking**

### Why

- Documentation already has strong structure

- Preserves semantic context

- Avoids unnecessary LLM usage

- Faster and cheaper than AI-based chunking

**Key insight**: Start with simple, deterministic chunking.

Use AI only when rules are insufficient.

---

## Day 3 – Text, Vector & Hybrid Search

**Goal**: Build robust retrieval over documentation and assignments.

### Implemented search strategies

- **Text search** – exact keyword matching

- **Vector search** – semantic understanding via embeddings

- **Hybrid search** – combines both approaches

### Why hybrid search

- Documentation uses precise technical terms

- User questions are often paraphrased

- Text search alone lacks semantic understanding

- Vector search alone lacks precision

**Hybrid retrieval provides**:

- High precision for technical queries

- Strong recall for conceptual questions

---

## Day 4 – Agentic AI with Pydantic AI

**Goal**: Turn retrieval into an agentic system that can reason, act, and answer reliably

### What changed

Instead of manually calling search functions, the system now uses an LLM-driven agent that:

1. Interprets the user question

2. Decides when and how to search

3. Calls the appropriate tool (hybrid search)

4. Reads retrieved content

5. Produces a grounded answer

### Key concepts learned

- Tool-calling with LLMs

- Agent-driven decision making

- Dependency injection (agent does not know about indexes)

- Separation of concerns:

    - Ingestion

    - Chunking

    - Retrieval

    - Reasoning

### Why Pydantic AI

- Clean abstraction over tool calling

- Automatic argument validation

- Async-safe agent execution

- Provider-agnostic (OpenAI / Gemini interchangeable)

### Result

A true agentic **RAG system** — not just “retrieve then prompt”.

---

## Day 5 – Logging & Automated Evaluation (LLM-as-Judge)

**Goal**: Add observability and objective quality evaluation to the AI agent.

### What this does (Day 5 scope)

- Captures every agent interaction as a structured JSON log

- Logs:
        
   - system prompt
    
   - user question
    
   - tool calls & returns
    
   - final answer
    
   - model & tool metadata

- Introduces an evaluation agent (LLM-as-judge)

- Evaluates answers using a checklist-based rubric

- Supports synthetic evaluation using generated questions

- Aggregates results into quantitative metrics

### Logging design

Each agent run produces a JSON log file containing:

- Agent name & model

- System instructions

- Tools available

- Full message trace (user → tool → agent)

- Source (user vs ai-generated)

This enables:

- Debugging incorrect answers

- Replaying agent decisions

- Comparing prompt versions

- Offline evaluation without re-running the agent

**Key insight**:

If you can’t log it, you can’t evaluate or improve it.

### Evaluation Results (Day 5)

The agent was evaluated using offline synthetic questions and an LLM-as-judge checklist.

Results are aggregated across multiple runs.

| Metric | Score |
|------|------|
| instructions_follow | **0.888889** |
| instructions_avoid | **1.000000** |
| answer_relevant | **0.888889** |
| answer_clear | **1.000000** |
| answer_citations | **0.777778** |
| completeness | **0.666667** |
| tool_call_search | **0.888889** |

**Interpretation**:

- The agent consistently follows safety rules and produces clear answers.

- Retrieval is used in most cases, but not enforced yet.

- Answer completeness and explicit citations are the main improvement areas.

These metrics provide a baseline for future prompt tuning and regression testing.

## Day 6 – Publishing the Agent with Streamlit & Deployment

**Goal**: Make the AI agent accessible through a simple, interactive web interface.

### What this does (Day 6 scope)

#### Created a chat-based UI using Streamlit

- Simple, intuitive interface for asking questions

- Maintains conversation history using session state

- Clean separation between UI and agent logic

#### Deployed the application on Streamlit Community Cloud

- Connected the GitHub repository

- Configured environment variables securely

- Enabled one-click deployment

- App is now accessible via a public URL

**Result**:

The agent is no longer a local experiment — it’s a live, shareable AI application.
