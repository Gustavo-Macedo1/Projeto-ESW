from dataclasses import dataclass


@dataclass
class Quadro:
    id: int
    nome: str
    max_integrantes: int
    visibilidade: str
    wip: int
    projeto_id: int
    total_cartoes: int = 0
    total_cartoes_feitos: int = 0
