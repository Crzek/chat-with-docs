from langchain_community.document_loaders import PyPDFLoader
from src.utils.text_splitters import split_text
import os


class Load_PDF:
    def __init__(self, file_path: str, lazy_load: bool = True) -> None:
        self.loader = PyPDFLoader(file_path)
        self.islady = lazy_load
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

    def load(self):
        return self.loader.load()

    def lazy_load(self):
        return self.loader.lazy_load()

    def get_pages_content(self) -> list[str]:
        """
        tambien puedes simplificar de esta manera:

        ```python
        pages_content = [page.page_content for page in dataPDF]`
        ```
        """

        pages_content = []
        pdf_content = self.lazy_load()
        for page in pdf_content:
            pages_content.append(page.page_content)

        return pages_content

    def get_chunks_and_metadata(self, pages_content: list[str]) -> tuple[list, list]:
        """ Dividir el texto en chunks y asociarlos con las páginas """
        chunks = []
        metadatas = []
        for page_number, page_content in enumerate(pages_content):
            # dividir el texto de la página
            page_chunks = split_text(page_content)
            # agregar los chunks a la lista principal
            chunks.extend(page_chunks)
            metadatas.extend(
                [{"filename": self.file_name, "page": page_number + 1}] * len(page_chunks))

        return chunks, metadatas


def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.lazy_load()
