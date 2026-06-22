from dataclasses import dataclass
from typing import Optional


@dataclass
class Raia:
    id: int
    nome: str
    descricao: Optional[str]
    quadro_id: int
    cor_fundo: str = "#F3F4F6"
