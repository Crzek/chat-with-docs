import os
from fastapi import APIRouter, UploadFile, File
from src.loaders.pdf_loader import Load_PDF, SplitConfig
from src.db.embeddings import generate_embeddings_chromadb
from src.config.settings import env
from src.schema.response import CostumJSONResponse

upload_router = APIRouter()


@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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
        chunk_size=80,
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
