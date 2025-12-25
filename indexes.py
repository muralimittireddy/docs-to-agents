# indexes.py
from minsearch import Index, VectorSearch
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any

class RepoIndexes:
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks

        # 1 Keyword / text index
        self.text_index = Index(
            text_fields=["title", "section", "filename"],
            keyword_fields=["content_type"]
        )
        self.text_index.fit(chunks)

        # 2 Vector index
        self.embedding_model = SentenceTransformer("all-mpnet-base-v2")
        embeddings = np.array([
            self.embedding_model.encode(self._build_text(chunk))
            for chunk in chunks
        ])

        self.vector_index = VectorSearch()
        self.vector_index.fit(embeddings, chunks)

    
    def _build_text(self, chunk: Dict[str, Any]) -> str:
        """
        Canonical text used for embeddings.
        """
        return "\n\n".join(
            filter(
                None,
                [
                    chunk.get("title"),
                    chunk.get("section"),
                    chunk.get("filename"),
                ],
            )
        )
