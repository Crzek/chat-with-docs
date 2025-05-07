from langchain.prompts import PromptTemplate


def get_sales_assistant_prompt():
    return PromptTemplate.from_template("""
        Eres un asistente de ventas de una tienda de tecnología.
        Debes responder en base a la información del 'Context'
        
        **Context**:
        {context}
        
        **Pregunta**:
        {query}
    """)
