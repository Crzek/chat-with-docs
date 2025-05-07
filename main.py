from config.settings import PDF_PATH, DB_PATH
from loaders.pdf_loader import Load_PDF
from src.db.chromadb import ChromaDBManager
from prompts.templates import get_sales_assistant_prompt
from langchain_openai import ChatOpenAI

# Cargar el PDF
# dataPDF = load_pdf(PDF_PATH)
dataPDF = Load_PDF(PDF_PATH)
pages_content = dataPDF.get_pages_content()
chunks, metadata = dataPDF.get_chunks_and_metadata(pages_content)


# Instanciar la base de datos
chromadb_manager = ChromaDBManager(DB_PATH)

# Consultar la base de datos
query = "Que productos tienes?"
result = chromadb_manager.query(
    query=query, metadata={"filename": "lista_productos.pdf"})

# Crear el contexto
context = "\n".join([doc.page_content for doc in result])

# Crear el prompt y ejecutar la cadena
prompt_template = get_sales_assistant_prompt()
llm = ChatOpenAI(model="gpt-4.1-nano", max_completion_tokens=2000)
chain = prompt_template | llm
chain_response = chain.invoke({"context": context, "query": query})

print("Context:", context)
print("Chain response:", chain_response.content)
