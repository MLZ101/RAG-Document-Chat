import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    UPLOAD_DIRECTORY: str = "uploaded_documents"
    CHROMA_PERSIST_DIRECTORY: str = "chroma_data"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "phi3"
    LOCAL_EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.UPLOAD_DIRECTORY, exist_ok=True)
        os.makedirs(self.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

settings = Settings()