import os
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.loaders.pdf_loader import Load_PDF, SplitConfig
from src.db.embeddings import generate_embeddings_chromadb
from src.config.settings import env
from src.schema.response import CostumJSONResponse

# modelos de base de datos
from src.model.models import UserDB, FileDB, MessageDB
from src.model import Base, session
from sqlalchemy.orm import Session
from uuid import uuid4

upload_router = APIRouter(prefix="/file", tags=["files"])

uuid_static = uuid4()

# Ruta para subir un archivo y guardarlo en la base de datos


@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = str(uuid_static)):
    os.makedirs(env.upload_dir, exist_ok=True)
    file_path = os.path.join(env.upload_dir, file.filename)

    # Evitar duplicados: si ya existe, no lo volvemos a indexar
    if os.path.exists(file_path):
        return CostumJSONResponse(
            data=None,
            message="El archivo ya existe. No se volverá a procesar."
        )

    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_type = file.filename.split(".")[-1]

    # generate metadata
    # Crear un registro en la base de datos para el archivo
    metadata = {"file_name": file_path, "file_type": file_type}
    metadata_str = json.dumps(metadata)

    new_file = FileDB(
        user_id=user_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_metadata=metadata_str
    )
    session_db = session()
    session_db.add(new_file)
    session_db.commit()

    return CostumJSONResponse(
        data={"file_id": new_file.id, "filename": file.filename},
        message="Archivo subido correctamente y guardado en la base de datos."
    )

# Ruta para eliminar un archivo y su registro en la base de datos


@upload_router.delete("/delete/{file_id}")
async def delete_file(file_id: str, user_id: str = str(uuid_static)):
    # file = session.query(File).filter(File.filename == file_name, File.user_id == user_id).first()
    file: Optional[FileDB] = session.query(FileDB).filter(FileDB.id == file_id)

    if not file:
        raise HTTPException(
            status_code=404, detail="Archivo no encontrado en la base de datos.")

    # Eliminar el archivo del sistema
    file_path = file.file_path
    if os.path.exists(file_path):
        os.remove(file_path)

    # Eliminar el registro en la base de datos
    session_db = session()
    session_db.delete(file)
    session_db.commit()

    return CostumJSONResponse(
        data=None,
        message=f"Archivo '{file_id}':{file.file_name} y su registro eliminado correctamente."
    )

# Ruta para generar embeddings a partir del archivo y guardarlos en el vectorstore


@upload_router.post("/upload/embeddings")
async def upload_and_gen_embeddings(file: UploadFile = File(...)):
    os.makedirs(env.upload_dir, exist_ok=True)
    file_path = os.path.join(env.upload_dir, file.filename)

    # Evitar duplicados: si ya existe, no lo volvemos a indexar
    if os.path.exists(file_path):
        return CostumJSONResponse(
            data=None,
            message="El archivo ya existe. No se volverá a procesar."
        )

    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Configurar el SplitConfig
    split_config = SplitConfig(
        model_name="gtp-4",
        chunk_size=100,
        chunk_overlap=20
    )

    # 1. Extraer texto
    load_pdf = Load_PDF(file_path=file_path)
    pages_pdf = load_pdf.get_pages_content()
    chunks, metadatas = load_pdf.get_chunks_and_metadata(
        pages_content=pages_pdf, split_config=split_config)
    uuids = load_pdf.get_uuids_for_chucks(chunks)

    # 2. Indexar a vectorstore
    generate_embeddings_chromadb(chunks, metadatas, uuids)

    return CostumJSONResponse(
        data={
            # se creara un collection por cada embedd que se suba.
            "embedding_id": 1,
            "metadata": metadatas
        },
        message="Archivo subido y procesado y generado embeddings correctamente."
    )


# @upload_file.post("/create_embeddings/{file_id}")
# def create_embeddings_by_file_id(file_id: str):
#     """
#     Crea los embeddings y los guarda en la base de datos. (vectorial)
#     """
#     # Mirar lo que hay en data/upload y mostrarlo en return
#     ...
