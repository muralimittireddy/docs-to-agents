# tools.py
from typing import List, Any, Dict

class SearchTools:
    def __init__(self, indexes):
        self.indexes = indexes

    # def search_learning(self, query: str) -> List[Any]:
    #     return self.indexes.text_index.search(
    #         query,
    #         num_results=5,
    #         filters={"content_type": "learning"}
    #     )

    # def search_assignments(self, query: str) -> List[Any]:
    #     return self.indexes.text_index.search(
    #         query,
    #         num_results=5,
    #         filters={"content_type": "assignment"}
    #     )

    def hybrid_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Hybrid search with intent-aware filtering and safe deduplication.
        """
        
        # Keyword search
        text_results = self.indexes.text_index.search(
            query,
            num_results=5
        )

        # Vector search
        query_vec = self.indexes.embedding_model.encode(query)
        vector_results = self.indexes.vector_index.search(
            query_vec,
            num_results=5
        )

        #  Merge + deduplicate by *section*, not file
        seen = set()
        combined = []

        for r in text_results + vector_results:
            key = (r.get("filename"), r.get("title"))
            if key not in seen:
                seen.add(key)
                combined.append(r)

        return combined
