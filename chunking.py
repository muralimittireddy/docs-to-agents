# chunking.py
import re
from typing import List, Dict, Any


def split_markdown_by_level(text: str, level: int = 2) -> List[str]:
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

def extract_title(section: str) -> str:
    """
    Extract title from a markdown section.
    """
    first_line = section.splitlines()[0]
    return first_line.lstrip("#").strip()

def detect_content_type(filename: str) -> str:
    """
    Detect whether file is learning material or assignment.
    """
    return "assignment" if "assignment" in filename.lower() else "learning"

def chunk_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    End-to-end chunking:
    - split into sections
    - return chunked documents
    """
    chunks = []

    for doc in docs:
        sections = split_markdown_by_level(doc["content"], level=2)

        for section in sections:
            chunks.append({
                "filename": doc["filename"],
                "content_type": detect_content_type(doc["filename"]),
                "title": extract_title(section),
                "section": section
            })

    return chunks
