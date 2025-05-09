"""
Para ejecutar langgraph con RAG, primero ejecuta el siguiente comando:
```bash
langgraph dev

``
"""
from src.graph.rag_graph import build_agent_graph

graph = build_agent_graph()
