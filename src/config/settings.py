import os
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "rag/consultorio.pdf")
DB_PATH = os.getenv("DB_PATH", "chromadb.db")
OPENAI_MODEL_LOWER = os.getenv("OPENAI_MODEL_LOWER", "gpt-4.1-nano")
ANTHROPIC_MODEL_LOWER = os.getenv("ANTHROPIC_MODEL_LOWER", "claude-1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
