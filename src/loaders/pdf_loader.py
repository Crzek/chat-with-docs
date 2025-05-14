from typing import Optional
from langchain_community.document_loaders import PyPDFLoader
from src.utils.text_splitters import split_text
from pydantic import BaseModel
import os
from uuid import uuid4


class SplitConfig(BaseModel):
    model_name: str = "gpt-4"
    chunk_size: int = 50
    chunk_overlap: int = 10


class Load_PDF:
    def __init__(
            self,
            file_path: str,
            idd: Optional[str] = None,
            lazy_load: bool = True
    ) -> None:
        self.loader = PyPDFLoader(file_path)
        self.islady = lazy_load
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.len_chunks = None
        if not idd:
            self.id = str(uuid4())
        else:
            self.id = idd

    def load(self):
        return self.loader.load()

    def lazy_load(self):
        return self.loader.lazy_load()

    def get_pages_content(self) -> list[str]:
        """
        return a list of content in each page
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

    def get_total_pages(self) -> int:
        "return a len docuemnt"
        return len(self.get_pages_content())

    def get_chunks_and_metadata(
            self,
            pages_content: list[str],
            split_config: SplitConfig  # configuracion para dividir el texto
    ) -> tuple[list, list]:
        """ Dividir el texto en chunks y asociarlos con las páginas\n 
            return:
                ([chunks], [metadatas])
        """
        chunks = []
        metadatas = []
        total_pages = len(pages_content)

        # TODO: REvisar len_chunks de metadata
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
            # CREATE METADATA CHUNKS
            metadatas.extend(
                [{
                    "file_id": self.id,
                    "file_name": self.file_name,
                    "page": page_number + 1,
                    "len_chunks_in_page": len(chunks),
                    "total_pages": total_pages,
                }] * len(page_chunks))

        self.len_chunks = len(chunks)
        return chunks, metadatas

    def get_uuids_for_chucks(
            self,
            chunks: list
    ) -> list[str]:
        return [str(uuid4())
                for _ in range(len(chunks))]  # crear una lista de ids

    def get_len_docs(self):
        """
        return the len of the document
        """
        docs = self.get_pages_content()
        return len(docs)


def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.lazy_load()
