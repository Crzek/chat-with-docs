from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


class ChromaDBManager:
    def __init__(self, db_path: str = "chroma_db", embeddings_model_name: str = "text-embedding-3-small"):
        # Cargar el modelo de embeddings
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        # Cargar la base de datos
        self.vector_store = Chroma(
            collection_name="chat_docs_collection",
            embedding_function=self.embeddings,
            persist_directory=db_path
        )

    def store(
        self,
        texts: list[str],
        metadatas: list[dict] = None,
        ids: list = None
    ):
        """Almacenar los textos en la base de datos"""
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )

    def find(
        self,
        metadata: dict,
    ):
        """Buscar elementos en la base de datos (vector store)"""
        result = self.vector_store.get(
            where=metadata,
            # el resultado incluye los embeddings y los documentos
            include=["metadatas", "documents"],
            n_results=5
        )
        return result

    def query(
        self,
        query: str,
        metadata: dict = None,
        n_results: int = 5
    ):
        """Realizar una consulta a la base de datos (vector store)"""
        """
        1r convierte la query en un embedding (vector)
        2n busca en la base de datos (vector store) el embedding más similar
            Es dicer compara Vectores querys con los vectores de la base de datos (dcoumentos, chunks)
        3r devuelve el documento (chunk) más similar
        """
        resul_query = self.vector_store.similarity_search(
            query=query,
            filter=metadata,
            k=n_results
        )
        return resul_query

    def drop_collection(self, metadata: dict):
        """Eliminar la base de datos (vector store)"""
        self.vector_store.delete_collection()

    def drop(self, metadata: dict):
        """Eliminar un elemento de la base de datos (vector store)"""
        self.vector_store.delete(
            where=metadata
        )
