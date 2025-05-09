from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.graph.rag_graph import build_agent_graph
from src.schema.schemas import AgentState
from src.schema.response import CostumJSONResponse


chat_router = APIRouter()


class UserMessage(BaseModel):
    question: str


@chat_router.post("/ask")
async def ask_agent(request_body: UserMessage):
    """
    Endpoint to ask the agent a question.
    """
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
                "thread_id": "1234567890",  # hacer un uuid
            }
        }
    )
    return CostumJSONResponse(
        data={
            "response": agent_response.get("messages")[-1].content,
            "metadata": {
                "language": agent_response.get("language"),
                # "thread_id": agent_response.config["configurable"]["thread_id"]
            }
        }
    )
