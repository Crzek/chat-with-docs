from typing import Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from uuid import uuid4
from src.graph.rag_graph import build_agent_graph
from src.schema.schemas import AgentState
from src.schema.response import CostumJSONResponse


chat_router = APIRouter(prefix="/chat", tags=["chat"])


class UserMessage(BaseModel):
    question: str
    thread_id: Optional[str] = None
    # ejemplo
    # thread_id: Optional[Union[str, int]] = None
    # tambien es equivalente lo siguiente:
    # thread_id: str | int


@chat_router.post("/ask")
async def ask_agent(request_body: UserMessage):
    """
    Endpoint to ask the agent a question.
    If you want to follow the conversation, you need to send the thread_id.
    If you want create new conversation, don't send thread_id.
    """
    # Versión más concisa y moderna
# thread_id = str(
#     uuid4()) if request_body.thread_id is None or request_body.thread_id == "" else request_body.thread_id
    # creamos nuevo thread si no existe 1 que envia el cliente
    thread_id = None
    if request_body.thread_id is None or request_body.thread_id == "":
        thread_id = str(uuid4())
    else:
        thread_id = request_body.thread_id

    user_message = HumanMessage(content=request_body.question)
    initial_state = AgentState(
        messages=[user_message], user_message=user_message.content)
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
