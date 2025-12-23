import io
import zipfile
import requests
import frontmatter
import os
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from google import genai
from dotenv import load_dotenv
import time
from minsearch import Index
from sentence_transformers import SentenceTransformer
import numpy as np
from minsearch import VectorSearch

load_dotenv()  # loads .env into environment

def download_github_zip(url: str, out_path: str):
    out = Path(out_path)

    # Delete existing file (fresh download)
    if out.exists():
        out.unlink()
        print(f"Deleted existing file: {out.name}")

    # Prepare session with retries
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    # Download with streaming
    try:
        with session.get(url, stream=True, timeout=(5, 60)) as r:
            r.raise_for_status()

            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0

            with open(out, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total:
                            percent = (downloaded / total) * 100
                            print(
                                f"\rDownloading: {percent:.2f}% "
                                f"({downloaded // 1024} KB)",
                                end=""
                            )

        print("\nDownload completed")

    except Exception as e:
        # Cleanup on failure
        if out.exists():
            out.unlink()
        raise RuntimeError("Download failed and partial file removed") from e

def sliding_window(seq, size, step):
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []
    for i in range(0, n, step):
        chunk = seq[i:i+size]
        result.append({'start': i, 'chunk': chunk})
        if i + size >= n:
            break

    return result

def split_markdown_by_level(text, level=2):
    """
    Split markdown text by a specific header level.
    
    :param text: Markdown text as a string
    :param level: Header level to split on
    :return: List of sections as strings
    """
    # This regex matches markdown headers
    # For level 2, it matches lines starting with "## "
    header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)

    # Split and keep the headers
    parts = pattern.split(text)
    
    sections = []
    for i in range(1, len(parts), 3):
        # We step by 3 because regex.split() with
        # capturing groups returns:
        # [before_match, group1, group2, after_match, ...]
        # here group1 is "## ", group2 is the header text
        header = parts[i] + parts[i+1]  # "## " + "Title"
        header = header.strip()

        # Get the content after this header
        content = ""
        if i+2 < len(parts):
            content = parts[i+2].strip()

        if content:
            section = f'{header}\n\n{content}'
        else:
            section = header
        sections.append(section)
    
    return sections

client = genai.Client()

def llm(prompt: str, model: str = "gemini-2.5-flash") -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

DOC_PROMPT  = """
Organize the following web development documentation
into clear, logical sections suitable for learning
and technical reference.

Guidelines:
- Group related concepts together
- Preserve technical accuracy and terminology
- Keep each section focused on ONE core concept
- Maintain instructional flow
- Include explanations around any code examples

<DOCUMENT>
{document}
</DOCUMENT>

Output format (strict):

## Section Title

Clear, structured explanation with all relevant details.

---

## Next Section Title

Next logical concept.

---
""".strip()

ASSIGNMENT_PROMPT = """
Organize the following web development assignment
into clear, task-oriented sections.

Guidelines:
- Separate objectives, requirements, and steps
- Keep tasks actionable and explicit
- Preserve constraints, inputs, and expected outputs
- Do NOT convert tasks into explanations

<DOCUMENT>
{document}
</DOCUMENT>

Output format (strict):

## Assignment Objective

What the learner is expected to build or achieve.

---

## Requirements

Explicit technical and functional requirements.

---

## Steps / Tasks

Ordered steps to complete the assignment.

---

## Submission / Evaluation Criteria

How the assignment will be assessed (if present).

---
""".strip()

def get_prompt(document_type: str) -> str:
    if document_type == "assignment":
        return ASSIGNMENT_PROMPT
    return DOC_PROMPT

def detect_doc_type(filename: str) -> str:
    name = filename.lower()
    if "assignment" in name:
        return "assignment"
    return "doc"

def intelligent_chunking(text: str, doc_type: str):
    prompt_template = get_prompt(doc_type)
    prompt = prompt_template.format(document=text)

    response = llm(prompt)

    sections = response.split('---')
    return [s.strip() for s in sections if s.strip()]

def extract_title(section):
    first_line = section.splitlines()[0]
    return first_line.lstrip('#').strip()

def detect_content_type(filename):
    text = filename.lower()
    if "assignment" in text:
        return "assignment"
    return "learning"

def classify_query(query):
    q = query.lower()
    if "assignment" in q or "task" in q or "exercise" in q:
        return "assignment"
    return "learning"

def build_chunk_text(d):
    parts = []
    if "title" in d:
        parts.append(d["title"])
    if "section" in d:
        parts.append(d["section"])
    if "filename" in d:
        parts.append(d["filename"].split("/")[-1])
    return "\n\n".join(parts)

def text_search(query,index):
    return index.search(query, num_results=5)

def vector_search(query,v_index,embedding_model):
    q = embedding_model.encode(query)
    return v_index.search(q, num_results=5)


def hybrid_search(query,v_index,embedding_model,index):
    text_results = text_search(query,index)
    vector_results = vector_search(query,v_index,embedding_model)
    
    # Combine and deduplicate results
    seen_ids = set()
    combined_results = []

    for result in text_results + vector_results:
        if result['filename'] not in seen_ids:
            seen_ids.add(result['filename'])
            combined_results.append(result)
    
    return combined_results

def main():
    print("Hello from AI AGENTS course!")

    ZIP_PATH = "repo.zip"
    EXTRACT_DATA = []
    ALLOWED_FILES = {"readme.md", "assignment.md"}

    url = "https://codeload.github.com/microsoft/Web-Dev-For-Beginners/zip/refs/heads/main"
    download_github_zip(url, ZIP_PATH)


    # 2️⃣ Open ZIP from disk
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        for file_info in zf.infolist():
            filename = file_info.filename
            filename_lower = file_info.filename.lower()
            if not (filename_lower.endswith(".md") or filename_lower.endswith(".mdx")):
                continue

            if filename.split("/")[-1] not in ALLOWED_FILES:
                continue

            if "/translations/" in filename:
                continue
    
            with zf.open(file_info) as f_in:
                content = f_in.read()
                post = frontmatter.loads(content)
                data = post.to_dict()
                data["filename"] = filename
                EXTRACT_DATA.append(data)
    repo_chunks = []
    
    # chunking by characters (simple chunking)
    # for doc in EXTRACT_DATA:
    #     doc_copy = doc.copy()
    #     doc_content = doc_copy.pop('content')
    #     chunks = sliding_window(doc_content, 2000, 1000)
    #     for chunk in chunks:
    #         chunk.update(doc_copy)
    #     repo_chunks.extend(chunks)

    # chunking by paragraphs and sections
    for doc in EXTRACT_DATA:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content')
        sections = split_markdown_by_level(doc_content, level=2)
        for section in sections:
            # print('section '+section)
            section_doc = doc_copy.copy()
            section_doc["content_type"] = detect_content_type(section_doc["filename"])
            section_doc["title"] = extract_title(section)
            section_doc['section'] = section
            repo_chunks.append(section_doc)

    # Chunking with LLM
    # for doc in EXTRACT_DATA:
    #     doc_copy = doc.copy()
    #     doc_content = doc_copy.pop('content')
    #     doc_type = detect_doc_type(doc_copy["filename"])
    #     time.sleep(15)  # due to model rate limiting
    #     sections = intelligent_chunking(doc_content, doc_type)
    #     for section in sections:
    #         section_doc = doc_copy.copy()
    #         section_doc['section'] = section
    #         repo_chunks.append(section_doc)
            
    # print(len(repo_chunks))

    # text search
    index = Index(
        text_fields=["title", "section", "filename"],
        keyword_fields=["content_type"]
    )
    
    index.fit(repo_chunks)

    # user_query = "learn java script"
    # query_type = classify_query(user_query)
    # results = index.search(
    #     user_query
    # )
    # print(results)

    # vector search
    embedding_model = SentenceTransformer("all-mpnet-base-v2")
    chunk_embeddings = []

    for d in repo_chunks:
        text = build_chunk_text(d)
        v = embedding_model.encode(text)
        chunk_embeddings.append(v)

    chunk_embeddings = np.array(chunk_embeddings)

    v_index =  VectorSearch()
    v_index.fit(chunk_embeddings,repo_chunks)

    # query = 'what to learn in javascript?'
    # q = embedding_model.encode(query)
    # results = v_index.search(q)
    # print(results)
    query = 'what assignments are there on js?'
    hybrid_search(query,v_index,embedding_model,index)



if __name__ == "__main__":
    main()

