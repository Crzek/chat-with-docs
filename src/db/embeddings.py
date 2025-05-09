from src.db.chromadb import ChromaDBManager
from src.config.settings import env


def get_db_embeddings() -> ChromaDBManager:
    return ChromaDBManager(
        embeddings_model_name=env.embedding_model)


def generate_embeddings_chromadb(
        chunks: list,
        metadatas: list,
        uuids: list
) -> None:
    chromadb_manager = get_db_embeddings()

    # almacenar los chunks en la base de datos
    # Esto se debe ejecutar una sola vez
    # # hace la llamada a la API de OpenAI para generar los embeddings
    chromadb_manager.store(
        texts=chunks,
        metadatas=metadatas,
        ids=uuids
    )


def drop_embeddings_chromadb(
        metadata: dict
):
    """
    e.g 
        `metadata={"filename": "lista_productos.pdf"}`
    """
    chromadb_manager = get_db_embeddings()
    # # para eliminar documentos
    chromadb_manager.drop(
        metadata=metadata
    )
