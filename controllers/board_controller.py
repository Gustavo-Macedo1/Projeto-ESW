from typing import List, Optional, Tuple

import mysql.connector

from models.board import Quadro
from repositories.board_repository import BoardRepository


class BoardController:
    def __init__(self, board_repository: Optional[BoardRepository] = None) -> None:
        self.board_repository = board_repository or BoardRepository()

    def listar_quadros(self, user_id: int, project_id: int) -> List[Quadro]:
        return self.board_repository.list_by_project(user_id=user_id, project_id=project_id)

    def obter_quadro(self, user_id: int, project_id: int, board_id: int) -> Optional[Quadro]:
        return self.board_repository.get_by_id(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
        )

    def criar_quadro(
        self,
        user_id: int,
        project_id: int,
        nome: str,
        max_integrantes: int,
        visibilidade: str,
        wip: int,
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome do quadro."
        if max_integrantes <= 0:
            return False, "Número máximo de integrantes deve ser maior que zero."
        if wip <= 0:
            return False, "WIP deve ser maior que zero."

        try:
            board = self.board_repository.create(
                user_id=user_id,
                project_id=project_id,
                nome=nome,
                max_integrantes=max_integrantes,
                visibilidade=visibilidade,
                wip=wip,
            )
            if not board:
                return False, "Projeto não encontrado para este usuário."
            return True, "Quadro criado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível criar o quadro. Tente novamente."

    def atualizar_quadro(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        nome: str,
        max_integrantes: int,
        visibilidade: str,
        wip: int,
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome do quadro."
        if max_integrantes <= 0:
            return False, "Número máximo de integrantes deve ser maior que zero."
        if wip <= 0:
            return False, "WIP deve ser maior que zero."

        try:
            updated = self.board_repository.update(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                nome=nome,
                max_integrantes=max_integrantes,
                visibilidade=visibilidade,
                wip=wip,
            )
            if not updated:
                return False, "Quadro não encontrado para este usuário."
            return True, "Quadro atualizado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível atualizar o quadro. Tente novamente."

    def excluir_quadro(self, user_id: int, project_id: int, board_id: int) -> Tuple[bool, str]:
        try:
            deleted = self.board_repository.delete(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
            )
            if not deleted:
                return False, "Quadro não encontrado para este usuário."
            return True, "Quadro excluído com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível excluir o quadro. Tente novamente."
