from typing import Annotated, Literal
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from sympy import Li


class LanguagueOutput(BaseModel):
    """
    Type de salida de la lengua
    """
    language: Literal["es", "en"] = "es"


class QuestionType(BaseModel):
    """
    Tipo de pregunta
    """
    question_type: Literal["appointment", "question"] = "question"


class AgentState(BaseModel):
    """Agent state schema."""

    user_message: str = ""
    query: str = ""
    context: str = ""  # info de la base de datos
    # language: LanguagueOutput = "es"
    language: LanguagueOutput = LanguagueOutput(language="es")
    # Anotacion para agregar mensajes a la lista
    # pano tener que enviar la lista completa
    messages: Annotated[list[AnyMessage], add_messages] = []
    # question_type: QuestionType = "question"
    question_type: QuestionType = QuestionType(question_type="question")
    len_chunks_query: int = None
    metadata: dict = None
    n_results: int = None
