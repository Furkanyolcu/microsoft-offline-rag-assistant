import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "sample_documents"
DB_PATH = DATA_DIR / "vector_store.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)
@dataclass
class RAGConfig:
    db_path: Path = DB_PATH
    docs_dir: Path = DOCS_DIR
    chunk_size: int = 400
    chunk_overlap: int = 60
    top_k: int = 3
    similarity_threshold: float = 0.15  
    embedding_dim: int = 384
    llm_provider: str = os.getenv("LLM_PROVIDER", "auto")  
    foundry_model_name: str = "phi-3.5-mini"
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "ollama")
    system_prompt: str = (
        "You are EchoLocal, an accurate offline AI Knowledge Assistant.\n"
        "Your task is to answer the user's question clearly and directly based on the provided Context Passages.\n"
        "Guidelines:\n"
        "1. Extract relevant facts from the provided Context Passages to answer the question.\n"
        "2. Include source document citations (e.g. [Source: filename.pdf | Section: Chunk #0]) for your answer.\n"
        "3. If none of the context passages contain any information related to the question, reply with: 'I do not have enough information in the local knowledge base to answer this question.'"
    )
config = RAGConfig()
