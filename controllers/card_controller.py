from typing import List, Optional, Tuple

import mysql.connector

from models.card import Cartao
from repositories.card_repository import CardRepository


class CardController:
    def __init__(self, card_repository: Optional[CardRepository] = None) -> None:
        self.card_repository = card_repository or CardRepository()

    def listar_cards(self, user_id: int, project_id: int, board_id: int) -> List[Cartao]:
        return self.card_repository.list_by_board(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
        )

    def listar_usuarios_do_projeto(self, user_id: int, project_id: int):
        return self.card_repository.list_project_users(user_id=user_id, project_id=project_id)

    def listar_colunas_do_quadro(self, user_id: int, project_id: int, board_id: int):
        return self.card_repository.list_board_columns(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
        )

    def obter_card(self, user_id: int, project_id: int, board_id: int, card_id: int) -> Optional[Cartao]:
        return self.card_repository.get_by_id(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
            card_id=card_id,
        )

    def criar_card(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        nome: str,
        responsavel_id: int,
        data_limite,
        prioridade: str,
        descricao: Optional[str],
        lane_id: int,
        a_fazer_coluna_id: int,
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome do card."

        try:
            card = self.card_repository.create(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                nome=nome,
                responsavel_id=responsavel_id,
                data_limite=data_limite,
                prioridade=prioridade,
                descricao=descricao,
                lane_id=lane_id,
                a_fazer_coluna_id=a_fazer_coluna_id,
            )
            if not card:
                return False, "Não foi possível criar o card com os dados informados."
            return True, "Card criado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível criar o card. Tente novamente."

    def atualizar_card(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        card_id: int,
        nome: str,
        responsavel_id: int,
        data_limite,
        prioridade: str,
        descricao: Optional[str],
    ) -> Tuple[bool, str]:
        nome = nome.strip()
        if not nome:
            return False, "Informe o nome do card."

        try:
            updated = self.card_repository.update(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=card_id,
                nome=nome,
                responsavel_id=responsavel_id,
                data_limite=data_limite,
                prioridade=prioridade,
                descricao=descricao,
            )
            if not updated:
                return False, "Card não encontrado para este usuário."
            return True, "Card atualizado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível atualizar o card. Tente novamente."

    def excluir_card(self, user_id: int, project_id: int, board_id: int, card_id: int) -> Tuple[bool, str]:
        try:
            deleted = self.card_repository.delete(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=card_id,
            )
            if not deleted:
                return False, "Card não encontrado para este usuário."
            return True, "Card excluído com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível excluir o card. Tente novamente."

    def mover_card(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        card_id: int,
        coluna_destino_id: int,
        raia_destino_id: int,
    ) -> Tuple[bool, str]:
        try:
            moved = self.card_repository.move(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=card_id,
                coluna_destino_id=coluna_destino_id,
                raia_destino_id=raia_destino_id,
            )
            if not moved:
                return False, "Não foi possível mover o card."
            return True, "Card movido com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível mover o card. Tente novamente."
