from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from src.schema.schemas import AgentState
from src.graph.node.nodes import (
    detect_language_node,
    detect_question_type_node,
    query_node,
    rag_node,
    response_node,
    appointment_node,
)


app_graph = StateGraph(AgentState)

# nodes
app_graph.add_sequence(
    detect_language_node,
    # detect_question_type_node, (este nodo no se usa)
    query_node,
    rag_node,
    response_node,
    appointment_node,
)

# edges
app_graph.add_edge(START, "detect_language_node")
# condicional
app_graph.add_conditional_edges(
    "detect_language_node", detect_question_type_node)
app_graph.add_edge("detect_language_node", "query_node")
app_graph.add_edge("query_node", "rag_node")
app_graph.add_edge("rag_node", "response_node")

# otro away
app_graph.add_edge("detect_language_node", "appointment_node")

# final
app_graph.add_edge(["appointment_node", "response_node"], END)

# estado inicial y copilar
initial_state = AgentState()
compiled_graph = app_graph.compile(initial_state)

# generate graph en png
compiled_graph.get_graph().draw_mermaid_png(output_file_path="agent_graph.png")
