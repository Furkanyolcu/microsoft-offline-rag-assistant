import sqlite3
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import config
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))
class VectorDatabase:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.db_path
        self.init_db()
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    def init_db(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_filename ON document_chunks(filename);
            ''')
            conn.commit()
        finally:
            conn.close()
    def clear_db(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_chunks;")
            conn.commit()
        finally:
            conn.close()
    def delete_document(self, filename: str):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_chunks WHERE filename = ?;", (filename,))
            conn.commit()
        finally:
            conn.close()
    def insert_chunk(self, filename: str, chunk_index: int, content: str, embedding: List[float]):
        embedding_json = json.dumps(embedding)
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO document_chunks (filename, chunk_index, content, embedding)
                VALUES (?, ?, ?, ?)
            ''', (filename, chunk_index, content, embedding_json))
            conn.commit()
        finally:
            conn.close()
    def insert_batch(self, chunks: List[Dict[str, Any]]):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            for item in chunks:
                emb_json = json.dumps(item["embedding"])
                cursor.execute('''
                    INSERT INTO document_chunks (filename, chunk_index, content, embedding)
                    VALUES (?, ?, ?, ?)
                ''', (item["filename"], item["chunk_index"], item["content"], emb_json))
            conn.commit()
        finally:
            conn.close()
    def fetch_all_chunks(self) -> List[Dict[str, Any]]:
        chunks = []
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, chunk_index, content, embedding FROM document_chunks;")
            rows = cursor.fetchall()
            for row in rows:
                vector = json.loads(row["embedding"])
                chunks.append({
                    "id": row["id"],
                    "filename": row["filename"],
                    "chunk_index": row["chunk_index"],
                    "content": row["content"],
                    "embedding": vector
                })
        finally:
            conn.close()
        return chunks
    def get_stats(self) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM document_chunks;")
            total_chunks = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT filename) FROM document_chunks;")
            total_docs = cursor.fetchone()[0]
            cursor.execute("SELECT filename, COUNT(*) as chunk_count FROM document_chunks GROUP BY filename;")
            doc_details = [{"filename": r[0], "chunks": r[1]} for r in cursor.fetchall()]
        finally:
            conn.close()
        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "documents": doc_details,
            "db_path": str(self.db_path)
        }
