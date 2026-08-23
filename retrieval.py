from typing import List, Dict, Any, Optional
from config import config
from database import VectorDatabase, cosine_similarity
from ingest import EmbeddingGenerator
class Retriever:
    def __init__(self, db: Optional[VectorDatabase] = None, embedder: Optional[EmbeddingGenerator] = None):
        self.db = db or VectorDatabase()
        self.embedder = embedder or EmbeddingGenerator()
    def get_top_chunks(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        top_k = top_k or config.top_k
        threshold = threshold or config.similarity_threshold
        query_vector = self.embedder.embed_text(query)
        all_chunks = self.db.fetch_all_chunks()
        if not all_chunks:
            return []
        scored_chunks = []
        for chunk in all_chunks:
            score = cosine_similarity(query_vector, chunk["embedding"])
            if score >= threshold:
                scored_chunks.append({
                    "id": chunk["id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "score": round(score, 4)
                })
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
if __name__ == "__main__":
    retriever = Retriever()
    test_query = "What is the grading policy for CS101?"
    results = retriever.get_top_chunks(test_query)
    print(f"Query: {test_query}\n")
    for r in results:
        print(f"[{r['score']}] Source: {r['filename']} (Chunk {r['chunk_index']})")
        print(f"Content: {r['content'][:120]}...\n")
