import chromadb
from chromadb.utils import embedding_functions 
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any

from app.config.config import settings
from app.config.logging import logging

local_embedding_model_for_chroma = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL_NAME)
logger = logging.getLogger(__name__)

class LocalEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, texts: List[str]) -> List[List[float]]:
        return local_embedding_model_for_chroma.encode(texts, convert_to_tensor=False).tolist()


# ChromaDB client and embedding function init
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
local_ef = LocalEmbeddingFunction()


def get_or_create_collection(collection_name: str):
    return chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=local_ef
    )


def add_chunks_to_collection(collection, texts: List[str], metadatas: List[Dict], ids: List[str]):
    try:
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        logger.error(f"Error adding documents to ChromaDB: {e}")
        raise


def query_collection(collection, query_texts: List[str], n_results: int = 5, where_filter: Optional[Dict] = None):
    try:
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where_filter
        )
    
    except Exception as e:
        logger.error(f"Error querying ChromaDB: {e}")
        raise


def delete_chunks_by_file_id(collection, file_id: str):
    try:
        collection.delete(where={"file_id": file_id})

    except Exception as e:
        logger.error(f"Error deleting chunks from ChromaDB for file_id {file_id}: {e}")
        raise


def list_all_document_ids_with_filenames(collection) -> List[Dict]:
    try:
        # fetch all items or a large enough limit and extract unique document info
        all_metadata = collection.get(limit=1000000, include=['metadatas'])['metadatas']
        unique_docs = {}
        for meta in all_metadata:
            file_id = meta.get('file_id')
            filename = meta.get('filename')
            if file_id and filename and file_id not in unique_docs:
                unique_docs[file_id] = {"id": file_id, "filename": filename}
        return list(unique_docs.values())
    
    except Exception as e:
        logger.error(f"Error listing documents from ChromaDB: {e}")
        return []