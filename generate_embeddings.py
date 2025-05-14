from src.loaders.pdf_loader import SplitConfig
from src.config.settings import env
from src.loaders.pdf_loader import Load_PDF
from src.db.chromadb import ChromaDBManager
from uuid import uuid4


dataPDF = Load_PDF(env.pdf_path)
pages_content = dataPDF.get_pages_content()

split_config = SplitConfig(model_name="gpt-4", chunk_size=50, chunk_overlap=10)
chunks, metadatas = dataPDF.get_chunks_and_metadata(
    pages_content, split_config)
uuids = [str(uuid4()) for _ in range(len(chunks))]  # crear una lista de ids


print("chunks:", len(chunks))
# print("metadatas:", metadatas)
# print("uuids:", uuids)
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
