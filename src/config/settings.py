# filepath: /home/cruz-tp/Documents/developer/ai/langchain-py/m3/config/settings.py
import os
from dotenv import load_dotenv
from sympy import E

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "rag/lista_productos.pdf")
DB_PATH = os.getenv("DB_PATH", "chromadb.db")
OPENAI_MODEL_LOWER = os.getenv("OPENAI_MODEL_LOWER", "gpt-4.1-nano")
ANTHROPIC_MODEL_LOWER = os.getenv("ANTHROPIC_MODEL_LOWER", "claude-1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
