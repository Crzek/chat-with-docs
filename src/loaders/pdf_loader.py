from langchain_community.document_loaders import PyPDFLoader
from src.utils.text_splitters import split_text
from pydantic import BaseModel
import os


class SplitConfig(BaseModel):
    model_name: str = "gpt-4"
    chunk_size: int = 50
    chunk_overlap: int = 10


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
        # itera cada página del pdf
        for page in pdf_content:
            pages_content.append(page.page_content)

        return pages_content

    def get_chunks_and_metadata(
            self,
            pages_content: list[str],
            split_config: SplitConfig  # configuracion para dividir el texto
    ) -> tuple[list, list]:
        """ Dividir el texto en chunks y asociarlos con las páginas """
        chunks = []
        metadatas = []
        for page_number, page_content in enumerate(pages_content):
            # dividir el texto de la página
            page_chunks = split_text(
                text=page_content,
                model_name=split_config.model_name,
                chunk_size=split_config.chunk_size,
                chunk_overlap=split_config.chunk_overlap
            )
            # agregar los chunks a la lista principal
            chunks.extend(page_chunks)
            metadatas.extend(
                [{"filename": self.file_name, "page": page_number + 1}] * len(page_chunks))

        return chunks, metadatas


def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.lazy_load()
