from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

import os
import uuid
import logging

from app.config.config import settings
from app.models.schemas import DocumentUploadResponse, ChatRequest, ChatResponse, Document
from app.services.document_processing import extract_text_from_pdf, extract_text_from_txt, chunk_text, generate_embeddings
from app.db.chromadb_manage import get_or_create_collection, add_chunks_to_collection, delete_chunks_by_file_id, list_all_document_ids_with_filenames
from app.services.rag_services import get_answer_from_rag


router = APIRouter()
kb_collection = get_or_create_collection("knowledge_base")
logger = logging.getLogger(__name__)


# ------------- Background processing ---------------
async def process_document_in_background(file_path: str, file_id: str, original_filename: str):
    """
    - detect file type
    - extract and chuck the data 
    - generate embeddings
    - add meta and id
    - store in chroma collection
    """

    try:
        logger.info(f"Starting background processing for {original_filename} (ID: {file_id})")

        # Extract text from the file
        if file_path.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file type for processing: must be txt or pdf exclusively.")

        # Chunk and embed the text
        chunks = chunk_text(text)
        _embeddings = generate_embeddings(chunks)

        # Add metadata and IDs
        metadatas = [
            {"file_id": file_id, "filename": original_filename, "chunk_index": i}
            for i in range(len(chunks))
        ]
        ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]

        # Add chunks to the collection
        add_chunks_to_collection(kb_collection, chunks, metadatas, ids)
        logger.info(f"Successfully processed and stored document: {original_filename} (ID: {file_id})")

    except Exception as e:
        logger.error(f"Background document processing task failed for document {file_id} ({original_filename}): {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# --------------- Upload Document ---------------
@router.post("/upload-doc/", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    - uploads a document (PDF/TXT)
    - saves it temporarily
    - queues it for background processing
    - returns 202
    """

    if not (file.filename.lower().endswith(".pdf") or file.filename.lower().endswith(".txt")):
        raise HTTPException(status_code=400, detail="only PDF and txt files are allowed.")

    file_id = str(uuid.uuid4())
    sanitized_filename = os.path.basename(file.filename)
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, f"{file_id}_{sanitized_filename}")

    try:
        # Save the uploaded file temporarily
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Add the document processing to a background task
        background_tasks.add_task(process_document_in_background, file_path, file_id, file.filename)

        return DocumentUploadResponse(
            message="processing...",
            file_id=file_id,
            filename=file.filename
        )
    
    except Exception as e:
        # Clean up the partially uploaded file if an error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Failed to process file upload: {e}")    
        raise HTTPException(status_code=500, detail=f"Failed to process file upload: {e}")
        

# --------------- Chat ---------------
@router.post("/chat/", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    - receives a user query
    - retrieves context
    - generates a response
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        rag_response = get_answer_from_rag(request.query, request.file_id)
        return ChatResponse(
            answer=rag_response["answer"],
            context_used=rag_response["context_used"]
        )
    except Exception as e:
        logger.error(f"Failed to get chat response: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat response: {e}")


# --------------- List Documents ---------------
@router.get("/documents/", response_model=list[Document])
async def list_documents():
    """- lists all the documents in the KB"""
    try:
        documents = list_all_document_ids_with_filenames(kb_collection)
        return documents
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {e}")


# --------------- Delete Document ---------------
@router.delete("/documents/{file_id}", status_code=204)
async def delete_document(file_id: str):
    """- deletes the entire document chunks from the KB"""
    try:
        delete_chunks_by_file_id(kb_collection, file_id)

        # Also delete the original uploaded file if it still exists
        for fname in os.listdir(settings.UPLOAD_DIRECTORY):
            if fname.startswith(f"{file_id}_"):
                os.remove(os.path.join(settings.UPLOAD_DIRECTORY, fname))
                logger.info(f"Deleted file: {fname}")
                break
        return JSONResponse(status_code=200, content={"message": f"Document {file_id} deleted."})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {e}")