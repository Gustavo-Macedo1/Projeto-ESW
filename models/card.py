from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Cartao:
    id: int
    nome: str
    descricao: Optional[str]
    prioridade: str
    data_criacao: datetime
    data_inicio: Optional[datetime]
    data_conclusao: Optional[datetime]
    data_limite: Optional[date]
    responsavel_id: int
    coluna_id: int
    raia_id: int
    responsavel_nome: Optional[str] = None
    coluna_nome: Optional[str] = None
    raia_nome: Optional[str] = None
