import os
import logging
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from typing import List, Dict

from app.config.config import settings

logger = logging.getLogger(__name__)
local_embedding_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL_NAME) # downlaods it the 1st time 

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        raise
    return text

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Splits text into chunks with overlap using Langchain's text splitter
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(text)

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    try:
        embeddings = local_embedding_model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error generating embeddings with SentenceTransformer: {e}")
        raise