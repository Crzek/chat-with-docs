from src.config.settings import env
from loaders.pdf_loader import Load_PDF
from src.db.chromadb import ChromaDBManager
from prompts.templates import get_sales_assistant_prompt
from langchain_openai import ChatOpenAI

# Cargar el PDF
# dataPDF = load_pdf(PDF_PATH)
dataPDF = Load_PDF(env.pdf_path)
pages_content = dataPDF.get_pages_content()
chunks, metadata = dataPDF.get_chunks_and_metadata(pages_content)


# Instanciar la base de datos
chromadb_manager = ChromaDBManager(env.db_path)

# Consultar la base de datos
query = "Que productos tienes?"
result = chromadb_manager.query(
    query=query, metadata={"filename": "consultorio.pdf"})

# Crear el contexto
context = "\n".join([doc.page_content for doc in result])

# Crear el prompt y ejecutar la cadena
prompt_template = get_sales_assistant_prompt()
llm = ChatOpenAI(model="gpt-4.1-nano", max_completion_tokens=2000)
chain = prompt_template | llm
chain_response = chain.invoke({"context": context, "query": query})

print("Context:", context)
print("Chain response:", chain_response.content)
