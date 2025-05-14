from functools import partial
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.schema.schemas import AgentState
from src.graph.node.nodes import (
    detect_language_node,
    detect_question_type_node,
    query_node,
    rag_node,
    response_node,
    appointment_node,
)


def build_agent_graph():
    """
    Build the agent graph.

    returns:
        compiled_graph: StateGraph
            The compiled state graph.
    """
    # Create a state graph
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

    # MemorySaver?
    # Sirve para guardar el estado del grafo en memoria
    # y poder recuperarlo en caso de que se necesite
    checkpointer = MemorySaver()
    # copilar el grafo
    return app_graph.compile(checkpointer=checkpointer)


def generate_graph():
    """
    Generate the graph image.
    """
    compiled_graph = build_agent_graph()

    # generate graph en png
    _ = compiled_graph.get_graph().draw_mermaid_png(
        output_file_path="agent_graph.png")

    return compiled_graph


"""
# generate graph en png
_ = compiled_graph.get_graph().draw_mermaid_png(
    output_file_path="agent_graph.png")

# Estado inicial
# pregunta del usuario
question = "quiero una cita para hoy"
user_message = HumanMessage(content=question)
initial_state.messages = [user_message]


agent_response = compiled_graph.invoke(initial_state)
print("Agent response:", agent_response["messages"][-1].content)
"""
