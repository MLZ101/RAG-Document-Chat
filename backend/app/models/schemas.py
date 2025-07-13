from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentUploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's query.")
    file_id: Optional[str] = Field(None, description="Optional: ID of a specific document to chat with")

class ChatResponse(BaseModel):
    answer: str
    context_used: List[str]

class Document(BaseModel):
    id: str
    filename: str
    # TODO: can add something like upload_date, status, chunk_count