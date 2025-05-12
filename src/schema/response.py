from typing import Any, Literal, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ResponseSchema(BaseModel):
    """
    Response schema for the API.

    Attributes:
        data (dict): The data returned by the API.
        error (bool): Indicates if there was an error.
        message (str): A message describing the response.
    """
    data: Optional[Any] = None
    message: str = "Success"
    error: Optional[str] = None


class CostumJSONResponse(JSONResponse):
    def __init__(self, data=None, message="Success", error=None, status_code=200):
        payload = ResponseSchema(
            data=data, message=message, error=error).model_dump()
        super().__init__(content=payload, status_code=status_code)


class ConfigSplitEmbedding(BaseModel):
    model_name: Literal["gpt-4", "gpt-3", "gpt-2"] = "gpt-4"
    chunk_size: int = Field(default=100,)
    chunk_overlap: int = Field(default=20)
