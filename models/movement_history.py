from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HistoricoMovimentacao:
    id: int
    cartao_id: int
    coluna_origem_id: Optional[int]
    coluna_destino_id: int
    raia_origem_id: Optional[int]
    raia_destino_id: int
    usuario_id: int
    data_movimentacao: datetime
