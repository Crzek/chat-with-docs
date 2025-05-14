from pydantic import BaseModel
# from typing import LiteralString


class MetadataFile(BaseModel):
    file_id: str
    file_name: str
    page: int
    len_chunks: int
    total_pages: int


class File(BaseModel):
    _id: str
    file_name: str
    file_path: str
    metadata: MetadataFile
