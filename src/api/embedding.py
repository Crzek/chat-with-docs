import os
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.loaders.pdf_loader import Load_PDF, SplitConfig
from src.db.embeddings import generate_embeddings_chromadb, drop_embeddings_chromadb
from src.config.settings import env
from src.schema.response import CostumJSONResponse

# modelos de base de datos
from src.model.models import UserDB, FileDB, MessageDB
from src.model import Base, session
from uuid import uuid4

from src.schema.response import ConfigSplitEmbedding

embedding_router = APIRouter(prefix="/embdedding", tags=["embedding"])


@embedding_router.post("/{file_id}")
async def create_embeddings(file_id: str, body: ConfigSplitEmbedding):
    file: Optional[FileDB] = session.query(
        File).filter(File.id == file_id).first()

    if not file:
        raise HTTPException(
            status_code=404, detail="Archivo no encontrado en la base de datos.")

    # Configurar el SplitConfig
    split_config = SplitConfig(
        model_name=body.model_name,
        chunk_size=body.chunk_size,
        chunk_overlap=body.chunk_overlap
    )

    # Extraer texto del archivo
    load_pdf = Load_PDF(file_path=file.file_path, id=file.id)
    pages_pdf = load_pdf.get_pages_content()  # optenemos paguinas
    chunks, metadatas = load_pdf.get_chunks_and_metadata(
        pages_content=pages_pdf, split_config=split_config)
    uuids = load_pdf.get_uuids_for_chucks(chunks)

    # Generar embeddings y guardarlos en el vectorstore
    generate_embeddings_chromadb(chunks, metadatas, uuids)

    # Aquí, puedes guardar la información de los embeddings si es necesario en la base de datos

    return CostumJSONResponse(
        data={"file_id": file.id, "metadata_file": metadatas},
        message="Embeddings generados y guardados correctamente."
    )


@embedding_router.delete("/{file_id}")
async def detele_embeddings(file_id: str):
    file: Optional[FileDB] = session.query(
        File).filter(File.id == file_id).first()

    if not file:
        raise HTTPException(
            status_code=404, detail="Archivo no encontrado en la base de datos.")

    # remover file de los embeddigs (db vector)
    metadata_dict = json.loads(file.file_metadata)
    drop_embeddings_chromadb(metadata_dict)

    # remover files del sistema de archivo
    file_path_abs = file.get_abs_path()
    # os.remove(env.DIR_UPLOAD+file.file_name)

    # # remover del DB

    # return CostumJSONResponse(
    #     data={"file_id": file.id, "metadata_file": metadata_dict},
    #     message="Embeddings generados y guardados correctamente."
    # )
    return CostumJSONResponse(
        data={
            "envBASE": file_path_abs
        }
    )
