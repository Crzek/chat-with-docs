"""
En el Query tengo que ver o definier algun algoritmo para que segun la longitud
del file coja 5 chunks si tiene 20 chunks totales o 20 si tiene 100 chunks.
nota: el nuemro resultados no puede superar al a los chucnks.
e.g: chunks:10
n_result: 1>10

No se recomienda coger todo el contenido porque los vectores se alejan de la Query
Mejor numero intermdia.
20%-40% ->small chunks de 10 chunks
0 - 30% -> long chunks de 100 chunks
"""
from pydantic import validate_arguments, Field
from src.loaders.pdf_loader import Load_PDF


class SearchManager:
    def __init__(self, loader_documnet: Load_PDF, len_chunks: int) -> None:
        self.pages = loader_documnet.get_len_docs()

        if len_chunks:
            self.len_chunks = len_chunks
        else:
            loader_documnet.len_chunks

    @validate_arguments
    def get_k_results(self, percent: float = Field(0.2, ge=0.0, le=1.0)):
        """
        Calcula un número de resultados basado en un porcentaje.

        Args:
            percent: Valor decimal entre 0 y 1 que representa el porcentaje.
                    Por ejemplo, 0.2 representa el 20%.

        Returns:
            int: Número de chunks a retornar basado en el porcentaje
            sacar porcentage de un valor -> precent (tanto porciento)

        e.g: valores actos entr 0-1
        0.2 reprensent -> 20 %
        """
        return int(self.len_chunks * percent)
