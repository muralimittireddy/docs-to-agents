# docs-to-agents

This project is part of a **7-day AI Agents crash course**.

## Environment Setup

This project uses **uv** for fast and clean dependency management.

### 1. Install uv

    pip install uv

### 2. Initialize project

    uv init

### 3. Add dependencies

    uv add requests python-frontmatter python-dotenv google-genai
    uv add --dev jupyter

### 4. Run Jupyter

    uv run jupyter notebook

### 5. Create .env

    GEMINI_API_KEY = your-api-key-here


## GitHub Repository Ingestion – Day 1

Day-1 focuses on **ingesting a GitHub repository safely** by:
- Downloading the repository as a ZIP
- Handling network failures with retries
- Avoiding memory issues using streaming
- Parsing Markdown files for downstream AI indexing

---

## What this does (Day 1 scope)

- Downloads any GitHub repository ZIP using `codeload.github.com`
- Deletes existing ZIP to avoid duplicate/corrupt data
- Streams the download to disk (no large memory usage)
- Retries on transient network failures
- Extracts and parses `.md` files using `python-frontmatter`
- Prepares structured data for future embedding / search steps

---

## Chunking Documents - Day 2

Day-2 focuses on how to break large technical documents into smaller, manageable pieces so they can be effectively used by an AI system.

Experimented with three approaches:

- Simple sliding-window chunking
- Section-based splitting using document structure
- AI-powered intelligent chunking

**Key insight**: start simple.

Most real-world cases don’t need complex or expensive chunking strategies.

My project focuses on building a conversational AI agent for GitHub repositories (documentation + assignments).

Since the content is already well-structured with headings and sections, section-based chunking works best—it preserves context, keeps concepts intact, and avoids unnecessary LLM usage.

This hybrid approach (rules first, AI only when needed) makes the system scalable, reliable, and cost-efficient.
