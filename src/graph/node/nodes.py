from termios import N_SLIP
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from typing import Literal

from src.db.chromadb import ChromaDBManager
from src.config.settings import OPENAI_MODEL_LOWER
from src.schema.schemas import LanguagueOutput, AgentState, QuestionType


def detect_language_node(agent_state: AgentState) -> AgentState:
    llm = ChatOpenAI(model=OPENAI_MODEL_LOWER)

    # definir el tipo de salida
    llm_parcer = llm.with_structured_output(LanguagueOutput)
    # salida structurada
    response: LanguagueOutput = llm_parcer.invoke(
        "Detecta si el lenguage si es español o inglés, reponde solo'es' o 'en': "
        f"{agent_state.user_message}"
    )
    agent_state.language = response.language
    print(f"Lenguaje detectado: {agent_state.language}")
    return agent_state


def detect_question_type_node(agent_state: AgentState) -> Literal["appointment_node", "query_node"]:
    user_message = agent_state.messages[-1].content
    llm = ChatOpenAI(model=OPENAI_MODEL_LOWER)

    # definir el tipo de salida
    llm_parcer = llm.with_structured_output(QuestionType)
    # salida structurada
    response: QuestionType = llm_parcer.invoke(
        "Detecta si el mensaje del usuario es de agendamiento de cita o pregunta qualquiera, "
        "reponde solo 'appointment' o 'question':\n"
        "*Mensaje usuario*: "
        f"{agent_state.user_message}"
    )
    agent_state.question_type = response.question_type
    print(f"Tipo de pregunta detectada: {agent_state.question_type}")

    if response.question_type == "appointment":
        return "appointment_node"
    elif response.question_type == "question":
        return "query_node"
    else:
        raise ValueError(
            f"Tipo de pregunta no detectado, los valores deben ser: 'appointment' o 'question', pero se recibió: "
            f"{response.question_type}"
        )


def appointment_node(agent_state: AgentState) -> AgentState:
    """
    Node that handles appointment scheduling.
    """
    print("Appointment node")

    agent_state.messages.append(AIMessage(content="Agendar cita"))
    # agent_state.messages = [AIMessage(content="Agendar cita")]
    return agent_state


def query_node(agent_state: AgentState) -> AgentState:
    history = agent_state.messages[:-1]  # todos menos el último
    user_message = agent_state.messages[-1]  # el último

    llm = ChatOpenAI(model=OPENAI_MODEL_LOWER)
    response = llm.invoke(
        f"""
    Eres un agente que debe generar un query para que se realice una búsqueda vectorial,
    No debes agregar palabras que podrían ser causantes de que se busque en vectores no deseados.
    Debes usar el último mensaje para generar el query y tambien puedes
    usar el histórico para tener un mayor contexto de la pregunta del usuario.

    Historial de conversacion:
    {history}

    Nuevo mensaje del usuario:
    {user_message}

    Query:
    """
    )
    agent_state.query = response.content
    print(f"Query generado: {agent_state.query}")
    return agent_state


def rag_node(agent_state: AgentState) -> AgentState:
    """
    Buscar vectores que tengo guardados en la base de datos
    """
    chromadb_manager = ChromaDBManager()
    result = chromadb_manager.query(
        query=agent_state.query,
        metadata={"filename": "consultorio.pdf"},
        n_results=2
    )
    agent_state.context = "\n\n".join([doc.page_content for doc in result])
    return agent_state


def response_node(agent_state: AgentState) -> AgentState:
    history = agent_state.messages[:-1]
    user_message = agent_state.messages[-1]
    llm = ChatOpenAI(model=OPENAI_MODEL_LOWER)
    llm_response = llm.invoke(
        f"""
        Eres un asistente que responde preguntas de los usuarios relacionadas a un consultorio médico,
        usa la información del contexto y el historial para responder.

        Contexto:
        {agent_state.context}

        Historial de conversacion:
        {history}

        Pregunta del usuario:
        {user_message}
        """
    )
    new_message = AIMessage(content=llm_response.content)
    agent_state.messages = [new_message]
    return agent_state
