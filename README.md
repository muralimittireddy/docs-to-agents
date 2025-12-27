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

### 5. Create .env or export 

    GEMINI_API_KEY = your-api-key-here
    export GEMINI_API_KEY=your-api-key-here

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
