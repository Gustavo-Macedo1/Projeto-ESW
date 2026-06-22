from dataclasses import dataclass


@dataclass
class Projeto:
    id: int
    nome: str
    visibilidade: str
    total_quadros: int = 0
