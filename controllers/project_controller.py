from typing import List, Optional, Tuple

import mysql.connector

from models.project import Projeto
from repositories.project_repository import ProjectRepository


class ProjectController:
    MAX_PROJECTS_PER_USER = 6

    def __init__(self, project_repository: Optional[ProjectRepository] = None) -> None:
        self.project_repository = project_repository or ProjectRepository()

    def listar_projetos_do_usuario(self, user_id: int) -> List[Projeto]:
        return self.project_repository.list_by_user(user_id=user_id)

    def obter_projeto_do_usuario(self, user_id: int, project_id: int) -> Optional[Projeto]:
        return self.project_repository.get_user_project_by_id(
            user_id=user_id,
            project_id=project_id,
        )

    def criar_projeto(self, user_id: int, nome: str) -> Tuple[bool, str]:
        nome = nome.strip()

        if not nome:
            return False, "Informe o nome do projeto."

        projeto_existente = self.project_repository.get_user_project_by_name(
            user_id=user_id,
            nome=nome,
        )
        if projeto_existente:
            return False, "Você já participa de um projeto com esse nome."

        total_projetos = len(self.project_repository.list_by_user(user_id=user_id))
        if total_projetos >= self.MAX_PROJECTS_PER_USER:
            return False, "Limite de 6 projetos atingido."

        try:
            self.project_repository.create_for_user(user_id=user_id, nome=nome)
            return True, "Projeto criado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível criar o projeto. Tente novamente."

    def excluir_projeto(self, user_id: int, project_id: int) -> Tuple[bool, str]:
        try:
            excluiu = self.project_repository.delete_project_for_user(
                user_id=user_id,
                project_id=project_id,
            )
            if not excluiu:
                return False, "Projeto não encontrado para este usuário."
            return True, "Projeto excluído com sucesso."
        except mysql.connector.IntegrityError:
            return (
                False,
                "Não foi possível excluir este projeto porque existem dados vinculados.",
            )
        except mysql.connector.Error:
            return False, "Não foi possível excluir o projeto. Tente novamente."

    def listar_integrantes_do_projeto(self, user_id: int, project_id: int):
        return self.project_repository.list_project_members(
            user_id=user_id,
            project_id=project_id,
        )

    def listar_usuarios_convidaveis(self, user_id: int, project_id: int):
        return self.project_repository.list_users_not_in_project(
            user_id=user_id,
            project_id=project_id,
        )

    def convidar_usuario_para_projeto(
        self,
        user_id: int,
        project_id: int,
        invited_user_id: int,
    ) -> Tuple[bool, str]:
        try:
            invited = self.project_repository.add_user_to_project(
                user_id=user_id,
                project_id=project_id,
                invited_user_id=invited_user_id,
            )
            if not invited:
                return False, "Não foi possível convidar este usuário."
            return True, "Usuário convidado com sucesso."
        except mysql.connector.Error:
            return False, "Não foi possível concluir o convite. Tente novamente."
