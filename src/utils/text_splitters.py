from langchain_text_splitters import TokenTextSplitter


def split_text(text, model_name="gpt-4", chunk_size=50, chunk_overlap=10):
    """
    Split the text by metoth tokenizer
    """
    splitter = TokenTextSplitter(
        model_name=model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)
