# Interfaz común (DIP + LSP)
from abc import ABC, abstractmethod
class VerificadorAcceso(ABC):
    @abstractmethod
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        pass