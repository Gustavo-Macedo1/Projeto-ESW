from typing import List, Optional, Tuple

import mysql.connector

from models.lane import Raia
from repositories.lane_repository import LaneRepository


class LaneController:
    def __init__(self, lane_repository: Optional[LaneRepository] = None) -> None:
        self.lane_repository = lane_repository or LaneRepository()

    def listar_raias(self, user_id: int, project_id: int, board_id: int) -> List[Raia]:
        return self.lane_repository.list_by_board(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
        )

    def garantir_raia_principal(self, board_id: int) -> Raia:
        return self.lane_repository.ensure_principal_lane(board_id=board_id)

    def criar_raia(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        nome: str,
        descricao: Optional[str],
        cor_fundo: str,
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome da raia."

        try:
            lane = self.lane_repository.create(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                nome=nome,
                descricao=descricao,
                cor_fundo=cor_fundo,
            )
            if not lane:
                return False, "Quadro não encontrado para este usuário."
            return True, "Raia criada com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível criar a raia. Tente novamente."

    def atualizar_raia(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        lane_id: int,
        nome: str,
        descricao: Optional[str],
        cor_fundo: str,
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome da raia."

        lane = self.lane_repository.get_by_id(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
            lane_id=lane_id,
        )
        if not lane:
            return False, "Raia não encontrada."
        if lane.nome.strip().lower() == "principal" and nome.strip().lower() != "principal":
            return False, "A raia Principal não pode ter o nome alterado."

        try:
            updated = self.lane_repository.update(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                lane_id=lane_id,
                nome=nome,
                descricao=descricao,
                cor_fundo=cor_fundo,
            )
            if not updated:
                return False, "Raia não encontrada para este usuário."
            return True, "Raia atualizada com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível atualizar a raia. Tente novamente."

    def excluir_raia(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        lane_id: int,
    ) -> Tuple[bool, str]:
        try:
            deleted = self.lane_repository.delete(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                lane_id=lane_id,
            )
            if not deleted:
                return False, "Raia não encontrada para este usuário."
            return True, "Raia excluída com sucesso."
        except ValueError as exc:
            return False, str(exc)
        except mysql.connector.Error:
            return False, "Não foi possível excluir a raia. Tente novamente."
