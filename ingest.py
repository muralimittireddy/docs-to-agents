import zipfile
import requests
import frontmatter
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Any


GITHUB_ZIP_URL = (
    "https://codeload.github.com/microsoft/"
    "Web-Dev-For-Beginners/zip/refs/heads/main"
)

ZIP_PATH = Path("repo.zip")

ALLOWED_FILES = {"readme.md", "assignment.md"}
EXCLUDE_DIRS = {"/translations/"}

def download_github_zip(url: str, out_path: Path) -> None:
    """
    Downloads a GitHub repository ZIP with retries and streaming.
    Deletes any partial file on failure.
    """
      
    # out = Path(out_path)

    # Delete existing file (fresh download)
    if out_path.exists():
        out_path.unlink()
        print(f"Deleted existing file: {out_path.name}")

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

            with open(out_path, "wb") as f:
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
        if out_path.exists():
            out_path.unlink()
        raise RuntimeError("Download failed and partial file removed") from e


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

def extract_markdown_from_zip(zip_path: Path) -> List[Dict[str, Any]]:
    """
    Reads allowed markdown files from ZIP and extracts frontmatter + content.
    """
    documents = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            filename = info.filename
            name = filename.lower()

            if not (name.endswith(".md") or name.endswith(".mdx")):
                continue

            if filename.split("/")[-1] not in ALLOWED_FILES:
                continue

            if any(d in filename for d in EXCLUDE_DIRS):
                continue

            with zf.open(info) as f:
                post = frontmatter.loads(f.read())
                doc = post.to_dict()
                doc["content"] = post.content
                doc["filename"] = filename
                documents.append(doc)

    return documents


def load_raw_documents() -> List[Dict[str, Any]]:
    """
    End-to-end ingestion:
    - download repo
    - extract markdown
    """
    # download_github_zip(GITHUB_ZIP_URL, ZIP_PATH)
    return extract_markdown_from_zip(ZIP_PATH)