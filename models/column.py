from dataclasses import dataclass


@dataclass
class Coluna:
    id: int
    nome: str
    ordem: int
    quadro_id: int
