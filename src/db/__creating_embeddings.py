from src.config.settings import env
from loaders.pdf_loader import Load_PDF
from src.db.chromadb import ChromaDBManager
from uuid import uuid4


# Cargar el PDF
# dataPDF = load_pdf(PDF_PATH)
dataPDF = Load_PDF(env.pdf_path)
pages_content = dataPDF.get_pages_content()
chunks, metadatas = dataPDF.get_chunks_and_metadata(pages_content)
uuids = [str(uuid4()) for _ in range(len(chunks))]  # crear una lista de ids

# Instanciar la base de datos
chromadb_manager = ChromaDBManager(embeddings_model_name=env.embedding_model)

# almacenar los chunks en la base de datos
# Esto se debe ejecutar una sola vez
# # hace la llamada a la API de OpenAI para generar los embeddings
chromadb_manager.store(
    texts=chunks,
    metadatas=metadatas,
    ids=uuids
)


# print("----", end="\n")
# print("Almacenados en la base de datos: ", len(chunks), " chunks")
# print("primer chunk: ", chunks[0])
# print("primer metadata: ", metadatas[0])
# print("primer uuid: ", uuids[0])
# # --BUSQUEDA--
# # para encontrar por metadata
# chromadb_manager.find(
#     metadata={"filename": "lista_productos.pdf"}
# )

# # para eliminar documentos
# chromadb_manager.drop(
#     metadata={"filename": "lista_productos.pdf"}
# )
