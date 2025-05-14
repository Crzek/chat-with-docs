import os
import json
from typing import Optional, Generator
from fastapi import APIRouter, Query, UploadFile, File, HTTPException

from uuid import uuid4

from fastapi.responses import StreamingResponse

from src.loaders.pdf_loader import Load_PDF, SplitConfig
from src.db.embeddings import generate_embeddings_chromadb
from src.config.settings import env
from src.schema.response import CostumJSONResponse
from src.utils.check_files import verify_file_exists, create_abs_path

upload_router = APIRouter(prefix="/files", tags=["files"])

# TODO: generar funcion para validar HEADER de API_KEY
uuid_static = uuid4()


class FileStreamService:
    @staticmethod
    def list_files_stream(
        directory: str,
        page: int = 1,
        page_size: int = 50,
        filter_pattern: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Genera un stream de archivos con soporte de paginación y filtrado

        Args:
            directory (str): Directorio a listar
            page (int): Número de página
            page_size (int): Tamaño de página
            filter_pattern (str, optional): Patrón para filtrar archivos

        Yields:
            str: Información de archivos en formato JSON
        """
        # Validar y normalizar el directorio
        directory = os.path.abspath(directory)

        if not os.path.isdir(directory):
            raise ValueError(f"Directory name: {directory} doesn't Exist")

        try:
            # Obtener todos los archivos/directorios
            all_items = []
            for item in os.scandir(directory):
                # Aplicar filtro si está presente
                if filter_pattern and not item.name.startswith(filter_pattern):
                    continue

                try:
                    # Recopilar información detallada del archivo
                    # y la retorna
                    item_info = {
                        "name": item.name,
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "path": item.path.split("chat-with-docs/")[-1],
                        "size": item.stat().st_size if item.is_file() else None,
                        "modified": item.stat().st_mtime
                    }
                    all_items.append(item_info)

                except Exception as e:
                    # Ignorar archivos que no se pueden acceder
                    print(f"Error processing {item.name}: {e}")

            # Aplicar paginación
            start = (page - 1) * page_size
            end = start + page_size
            paginated_items = all_items[start:end]

            # Generar stream de archivos
            for item in paginated_items:
                yield json.dumps(item) + "\n"

        except PermissionError:
            raise ValueError("Not Permission to access the directory")
        except Exception as e:
            raise ValueError(f"Error listing files: {str(e)}")


@upload_router.get("/")
async def stream_files(
    directory: str = Query(env.upload_dir, description="Directory to List"),
    page: int = Query(1, ge=1, description="Number of Page"),
    page_size: int = Query(50, ge=1, le=500, description="Page size"),
    filter_pattern: Optional[str] = Query(
        None, description="Pattern to filter the files")
):
    """
    Endpoint para streaming de archivos

    - Soporta paginación
    - Permite filtrado por patrón
    - Devuelve stream de archivos en formato JSON
    """
    try:
        # Crear generador de archivos
        file_stream = FileStreamService.list_files_stream(
            directory,
            page,
            page_size,
            filter_pattern
        )

        # streaming response
        # con clase de fastAPI
        return StreamingResponse(
            file_stream,
            media_type="application/x-ndjson",  # Newline Delimited JSON
            headers={
                "Content-Type": "application/x-ndjson",
                "Transfer-Encoding": "chunked"
            }
        )
    except ValueError as e:
        # Manejar errores específicos
        raise HTTPException(status_code=400, detail=str(e))

# Ruta para subir un archivo y guardarlo en la base de datos


@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(env.upload_dir, exist_ok=True)
    file_path = create_abs_path(file.filename)

    # Evitar duplicados: si ya existe, no lo volvemos a indexar
    if os.path.exists(file_path):
        return CostumJSONResponse(
            data=None,
            message="The File is already exist."
        )

    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_type = file.filename.split(".")[-1]

    # generate metadata
    metadata = {
        "filePath": file_path,
        "mimeType": file_type,
        "FileName": file.filename
    }
    # metadata_str = json.dumps(metadata)

    return CostumJSONResponse(
        data={"filename": file.filename, "metadata": metadata},
        message="File uploads successfully"
    )

# Ruta para eliminar un archivo y su registro en la base de datos


@upload_router.delete("/{file_name}")
async def delete_file(file_name: str, user_id: str = str(uuid_static)):
    """
    file_name: need to specify the extancion file, like: .pdf , .csv
    """
    exist = verify_file_exists(file_name)
    if not exist:
        raise HTTPException(
            status_code=404, detail=f"{file_name} doesn't exist, you need to uploads before")

    # Eliminar el archivo del sistema
    file_path = create_abs_path(file_name)
    os.remove(file_path)

    return CostumJSONResponse(
        data=None,
        message=f"file: {file_name} deleted successfully"
    )


@upload_router.get("/exist/{file_name}")
async def exist_file(file_name: str, user_id: str = str(uuid_static)):
    """
    file_name: need to specify the extancion file, like: .pdf , .csv
    """
    exist = verify_file_exists(file_name)
    if not exist:
        raise HTTPException(
            status_code=404, detail=f"{file_name} doesn't exist, you need to uploads before")

    return CostumJSONResponse(
        data={"exist": exist},
        message="check data value"
    )


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
