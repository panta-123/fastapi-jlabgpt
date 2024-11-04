from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str = Field(..., description="The query string")

class StreamRequest(BaseModel):
    query: str = Field(..., description="The query string for streaming")

class UploadResponse(BaseModel):
    filename: str
    metadata_filename: Optional[str] = None
    status: str


class ChunkResponse(BaseModel):
    chunk: str