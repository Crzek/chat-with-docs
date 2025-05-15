from typing import Optional, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from uuid import uuid4
from src.graph.rag_graph import build_agent_graph
from src.schema.schemas import AgentState
from src.schema.response import CostumJSONResponse
from src.utils.check_files import verify_file_exists, create_abs_path
from src.utils.search_manager import SearchManager
from src.loaders.pdf_loader import Load_PDF

# mongo
from src.config.db_motor import connection


chat_router = APIRouter(prefix="/chats", tags=["chat"])


class UserMessage(BaseModel):
    question: str
    presicion: float = Field(default=0.2, ge=0.05, le=1.0)
    thread_id: Optional[str] = None
    # ejemplo
    # thread_id: Optional[Union[str, int]] = None
    # tambien es equivalente lo siguiente:
    # thread_id: str | int


@chat_router.post("/ask/{file_name}")
async def ask_agent(request_body: UserMessage, file_name: str):
    """
    Endpoint to ask the agent a question.
    If you want to follow the conversation, you need to send the thread_id.
    If you want create new conversation, don't send thread_id.
    """
    # Obtner Metadata y n_results para este file_name
    # if not verify_file_exists(file_name):
    try:
        db = await connection()
        file_db = await db["files"].find_one({"file_name": file_name})
        if not file_db:
            return CostumJSONResponse(
                message=f"File doesn't Exist {file_name}, remember to generate embeddings", error="Not found")

        # obtener n_resultas apartir del documento
        search_manager = SearchManager(
            Load_PDF(create_abs_path(file_name)), file_db["len_chunks"])
        k_results = search_manager.get_k_results(request_body.presicion)

        # seguir conversasion con thread_id o generar si no hay.
        thread_id = str(uuid4()) if request_body.thread_id is None or request_body.thread_id == "" \
            else request_body.thread_id

        # 1r msg de User
        user_message = HumanMessage(content=request_body.question)
        from langchain_core.runnables import RunnableConfig

        # estado inicial del Agente
        initial_state = AgentState(
            messages=[user_message],
            user_message=user_message.content,
            metadata={"file_name": file_name},
            n_results=k_results,
        )
        agent_response = build_agent_graph().invoke(
            initial_state,
            config={
                "configurable": {
                    "detect_language_node": {
                        "language": "es",
                    },
                    "thread_id": thread_id,  # hacer un uuid
                }
            }
        )
        return CostumJSONResponse(
            data={
                "responseAI": agent_response.get("messages")[-1].content,
                "metadata": {
                    "language": agent_response.get("language"),
                    # "thread_id": agent_response.config["configurable"]["thread_id"]
                    "thread_id": thread_id,  # hacer un uuid
                }
            }
        )

    except Exception as e:
        return CostumJSONResponse(message=f"Error in db: {e}", error="Error Mongo db")
