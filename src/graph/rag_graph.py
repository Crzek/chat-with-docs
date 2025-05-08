from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
# from typing import TypedDict
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
# detect_question_type_node, (este nodo no se usa)
app_graph.add_node(detect_language_node)
app_graph.add_node(query_node)
app_graph.add_node(rag_node)
app_graph.add_node(response_node)
app_graph.add_node(appointment_node)

# edges
app_graph.add_edge(START, "detect_language_node")
# condicional
app_graph.add_conditional_edges(
    "detect_language_node", detect_question_type_node)
app_graph.add_edge("appointment_node", END)

# other way
app_graph.add_edge("query_node", "rag_node")
app_graph.add_edge("rag_node", "response_node")
app_graph.add_edge("response_node", END)

# estado inicial y copilar
initial_state = AgentState()
compiled_graph = app_graph.compile()

# generate graph en png
# _ = compiled_graph.get_graph().draw_mermaid_png(
#     output_file_path="agent_graph.png")

# Estado inicial
# pregunta del usuario
question = "quiero una cita para hoy"
user_message = HumanMessage(content=question)
initial_state.messages = [user_message]


# agent_response = compiled_graph.invoke(initial_state)
# print("Agent response:", agent_response["messages"][-1].content)
