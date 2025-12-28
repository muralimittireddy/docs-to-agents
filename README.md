# 🤖 GitHub Repository AI Assistant

An AI-powered assistant that helps users quickly find answers from any GitHub repository’s documentation and assignments.

## Overview

Large GitHub repositories often contain extensive documentation and assignments that are hard to navigate.

This project solves that problem by providing a conversational AI assistant that:

- Searches GitHub repository documentation

- Retrieves the most relevant sections

- Generates clear, grounded answers with references to source files

### Why it’s useful

- No more scrolling through long Markdown files

- Answers are grounded in real repository content

- Direct references to source files

- Multiple interfaces:

    - CLI

    - Web UI (Streamlit)

## Installation

**Requirements**:

- Python 3.9+  
- [uv](https://github.com/astral-sh/uv) 

```bash
# Make sure you have uv
pip install uv

# Clone this repo
git clone https://github.com/muralimittireddy/docs-to-agents.git
cd docs-to-agents

# Install dependencies
uv sync
```

## Usage

### API key

Set up your GEMINI API key:

```bash
export GEMINI_API_KEY="your-key"
```

### CLI mode  

```bash
uv run main.py
```

This opens an interactive CLI environment. You can ask the conversational agent any question about the course.

Type `stop` to exit.  

### Web UI mode  

```bash
uv run streamlit run app.py
```


This launches a Streamlit app. You can chat with the assistant in your browser.  

The app is available at [http://localhost:8501](http://localhost:8501).


## Features

- 🔎 Search over Markdown files with `minsearch`  
- 🤖 AI-generated answers powered by `pydantic-ai` + GEMINI (`gemini-2.5-flash`)  
- 📂 Direct GitHub references in answers
- 🖥️ Two interfaces: CLI (`main.py`) and Streamlit (`app.py`)  
- 📝 Automatic logging of conversations into JSON files (`logs/`)  


## Evaluations

We evaluate the agent using the following criteria:

- `instructions_follow`: The agent followed the user's instructions
- `instructions_avoid`: The agent avoided doing things it was told not to do  
- `answer_relevant`: The response directly addresses the user's question  
- `answer_clear`: The answer is clear and correct  
- `answer_citations`: The response includes proper citations or sources when required  
- `completeness`: The response is complete and covers all key aspects of the request
- `tool_call_search`: Is the search tool invoked? 

We do this in two steps:

- First, we generate synthetic questions (see [`question_generation.py`](question_generation.py))
- Next, we run our agent on the generated questions and check the criteria (see [`offline_eval.py`](offline_eval.py))

Current evaluation metrics:

| Metric | Score |
|------|------|
| instructions_follow | **0.888889** |
| instructions_avoid | **1.000000** |
| answer_relevant | **0.888889** |
| answer_clear | **1.000000** |
| answer_citations | **0.777778** |
| completeness | **0.666667** |
| tool_call_search | **0.888889** |


The most important metric for this project is `answer_relevant`. This measures whether the system's answer is relevant to the user. It's currently ~90%, meaning almost answers were relevant. 

Improvements: Our evaluation is currently based on only 10 questions. We need to collect more data for a more comprehensive evaluation set.

## Project file overview

`main.py`: Entry point for the CLI version of the assistant  
- Loads and indexes data  
- Initializes the search agent  
- Provides an interactive loop where users can type questions and get answers  
- Logs each interaction to a JSON file

`app.py`: Streamlit-based web UI for the assistant  
- Provides a chat-like interface in the browser  
- Streams assistant responses in real time  
- Logs all interactions into JSON files

`ingest.py`: Handles data ingestion and indexing from the GitHub FAQ repository
- Downloads the repository ZIP archive  
- Extracts `.md` and `.mdx` files

`chunking.py`:
- chunks documents into smaller windows

`indexes.py`:
- Builds a `minsearch` index for fast text-based and vector based retrieval

`tools.py`: Defines the search tool used by the agent  
- Wraps the `minsearch` index into a simple API  
- Provides a `hybrid_search(query)` tool that retrieves up to 5 results

`agent.py`: Defines and configures the AI Agent  
- Uses `pydantic-ai` to build the agent  
- Loads a system prompt template that instructs the assistant on how to answer questions  
- Attaches the search tool so the agent can query the FAQ index  
- Configured with the `gemini-2.5-flash` model

`logs.py`: Utility for logging all interactions  
- Serializes messages, prompts, and model metadata  
- Stores logs in JSON files in the `logs/` directory (configurable via `LOGS_DIRECTORY`)  
- Ensures each log has a timestamp and unique filename


## Tests

TODO: add tests

```bash
uv run pytest
```

(Currently minimal test coverage; contributions welcome.)  


## Deployment

To deploy the app on Streamlit Cloud:

Generate a `requirements.txt` file from your `uv` environment:

```bash
uv export > requirements.txt
```

Make sure it's pushed along with the latest changes.

Next, run the application locally:

```bash
uv run streamlit run app.py
```

Click "deploy", connect your GitHub repo, and configure deployment settings.

In the settings, make sure you configure `GEMINI_API_KEY`.

Once configured, Streamlit Cloud will automatically detect changes. It will redeploy your app whenever you push updates.


## Credits / Acknowledgments

- [DataTalksClub](https://github.com/DataTalksClub) for open-source course materials  
- [Alexey Grigorev](https://www.linkedin.com/in/agrigorev) for the [AI Agents Crash Course](https://alexeygrigorev.com/aihero/)  
- Main libraries: `pydantic-ai` for AI, `minsearch` for search
