from typing import Optional, Tuple

from models.user import Usuario
from repositories.user_repository import UserRepository


class AuthController:
    def __init__(self, user_repository: Optional[UserRepository] = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def autenticar(self, username: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        usuario = self.user_repository.validate_credentials(username=username, senha=senha)
        if not usuario:
            return False, None
        return True, usuario

    def cadastrar(self, username: str, senha: str, confirma_senha: str) -> Tuple[bool, str]:
        username = username.strip()

        if not username:
            return False, "Informe o usuário."
        if not senha:
            return False, "Informe a senha."
        if senha != confirma_senha:
            return False, "As senhas não coincidem."
        if self.user_repository.get_by_username(username):
            return False, "Usuário já cadastrado."

        self.user_repository.create_user(username=username, senha=senha)
        return True, "Cadastro realizado com sucesso."
