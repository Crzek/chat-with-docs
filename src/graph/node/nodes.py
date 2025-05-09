from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from typing import Literal

from src.db.chromadb import ChromaDBManager
from src.config.settings import env
from src.schema.schemas import LanguagueOutput, AgentState, QuestionType
from src.utils.tools import create_appointment


def detect_language_node(agent_state: AgentState) -> AgentState:
    """
    detect_language_node: detecta y guarda el idioma. Nada más.
    """
    llm = ChatOpenAI(model=env.openai_model)

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
    """
    detect_question_type_node: decide a qué nodo ir (query_node o appointment_node). No necesita ser nodo.
    """
    print("\n mensaje\n")
    print(agent_state.messages)
    user_message = agent_state.messages[-1].content
    print(f"Mensaje del usuario: {user_message}\n")
    # print(agent_state.message)
    llm = ChatOpenAI(model=env.openai_model)

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
    tools = [create_appointment]
    # agrego tools a la IA
    # tools son funciones que se pueden llamar
    llm = ChatOpenAI(model=env.openai_model).bind_tools(tools)
    response_llm = llm.invoke(agent_state.messages)

    # tines que tener al menos una llamada a tool
    tool_calls = response_llm.tool_calls  # lista
    if tool_calls:
        fuction_result = None  # guardar el resultado de la función
        for tool_call in tool_calls:

            # miramos si la llamada a la herramienta es la correcta
            # tools son funciones (que creas) que se pueden llamar
            if tool_call["name"] == "create_appointment":
                args = tool_call["args"]
                # utilizamos la función que creamos
                fuction_result = create_appointment.invoke(args)

        agent_state.messages.append(AIMessage(content=fuction_result))
        agent_state.messages = [AIMessage(content=fuction_result)]

    else:
        # si no hay tool_calls, solo se guarda el mensaje de la IA
        agent_state.messages = [AIMessage(content=response_llm.content)]

    return agent_state


def query_node(agent_state: AgentState) -> AgentState:
    history = agent_state.messages[:-1]  # todos menos el último
    user_message = agent_state.messages[-1]  # el último

    llm = ChatOpenAI(model=env.openai_model)
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
    chromadb_manager = ChromaDBManager(
        embeddings_model_name=env.embedding_model)
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
    llm = ChatOpenAI(model=env.openai_model)
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
    # agent_state.messages.append(new_message)
    return agent_state
