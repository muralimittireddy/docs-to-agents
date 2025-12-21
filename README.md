# docs-to-agents

This project is part of a **7-day AI Agents crash course**.

## Environment Setup

This project uses **uv** for fast and clean dependency management.

### 1. Install uv

    pip install uv

### 2. Initialize project

    uv init

### 3. Add dependencies

    uv add requests python-frontmatter
    uv add --dev jupyter

### 4. Run Jupyter

    uv run jupyter notebook

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
