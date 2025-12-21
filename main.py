import io
import zipfile
import requests
import frontmatter
import os
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

        print("\nDownload completed ✅")

    except Exception as e:
        # 4️⃣ Cleanup on failure
        if out.exists():
            out.unlink()
        raise RuntimeError("Download failed and partial file removed") from e


def main():
    print("Hello from AI AGENTS course!")

    ZIP_PATH = "repo.zip"
    EXTRACT_DATA = []

    url = "https://codeload.github.com/microsoft/Web-Dev-For-Beginners/zip/refs/heads/main"
    download_github_zip(url, ZIP_PATH)


    # 2️⃣ Open ZIP from disk
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        for file_info in zf.infolist():
            filename = file_info.filename
            filename_lower = file_info.filename.lower()
            if not (filename_lower.endswith(".md") or filename_lower.endswith(".mdx")):
                continue
    
            with zf.open(file_info) as f_in:
                content = f_in.read()
                post = frontmatter.loads(content)
                data = post.to_dict()
                data["filename"] = filename
                EXTRACT_DATA.append(data)
    
    # print("Markdown files parsed")
    
    # if EXTRACT_DATA:
    #     print(EXTRACT_DATA[0])
    # else:
    #     print("No markdown files found")

if __name__ == "__main__":
    main()

