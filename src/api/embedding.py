import os
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.loaders.pdf_loader import Load_PDF, SplitConfig
from src.db.embeddings import generate_embeddings_chromadb, drop_embeddings_chromadb
from src.config.settings import env
from src.schema.response import CostumJSONResponse

# modelos de base de datos
from uuid import uuid4

from src.schema.response import ConfigSplitEmbedding
from src.utils.check_files import verify_file_exists, create_abs_path
from src.db.embeddings import get_db_embeddings


embedding_router = APIRouter(prefix="/embdeddings", tags=["embedding"])


@embedding_router.post("/{file_name}")
async def create_embeddings(file_name: str, body: ConfigSplitEmbedding):
    exist = verify_file_exists(file_name)
    if not exist:
        raise HTTPException(
            status_code=404, detail=f"{file_name} Not Found")

    # Configurar el SplitConfig
    split_config = SplitConfig(
        model_name=body.model_name,
        chunk_size=body.chunk_size,
        chunk_overlap=body.chunk_overlap
    )
    abs_path_file = create_abs_path(file_name)
    # Extraer texto del archivo
    load_pdf = Load_PDF(file_path=abs_path_file)
    pages_pdf = load_pdf.get_pages_content()  # optenemos paguinas
    chunks, metadatas = load_pdf.get_chunks_and_metadata(
        pages_content=pages_pdf, split_config=split_config)
    uuids = load_pdf.get_uuids_for_chucks(chunks)

    # Generar embeddings y guardarlos en el vectorstore
    # la meta data debe de ser de type: str, int ,flaot, bool
    generate_embeddings_chromadb(chunks, metadatas, uuids)

    # Aquí, puedes guardar la información de los embeddings si es necesario en la base de datos

    return CostumJSONResponse(
        data={
            "file_id": load_pdf.id,
            "file_name": file_name,
            "chunks": len(chunks),
            "metadata_chunk_1": metadatas[1]},
        message="Embeddings created"
    )


@embedding_router.delete("/{file_name}")
async def detele_embeddings(file_name: str):
    """
    Eliminar collections
    si queremos guardar otro tipo de datos como img, audio
    deberiasmos crear otra bd vectorial
    """
    try:

        chromadb_manager = get_db_embeddings()
        # para eliminar documentos
        chromadb_manager.drop(
            metadata={
                "filename":
                file_name
            }
        )
        return CostumJSONResponse(
            data=None,
            message=f"Delete chucks files: {file_name}"
        )

    except Exception as e:
        return CostumJSONResponse(
            data=None,
            message=f"Error Deleting: {e}"
        )
