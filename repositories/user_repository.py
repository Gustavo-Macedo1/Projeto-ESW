from typing import Optional

from database.connection import get_connection
from models.user import Usuario


class UserRepository:
    def get_by_username(self, username: str) -> Optional[Usuario]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT id, username, senha FROM usuarios WHERE username = %s",
                    (username,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Usuario(id=row["id"], username=row["username"], senha=row["senha"])
        finally:
            connection.close()

    def validate_credentials(self, username: str, senha: str) -> Optional[Usuario]:
        usuario = self.get_by_username(username=username)
        if not usuario:
            return None
        if usuario.senha != senha:
            return None
        return usuario

    def create_user(self, username: str, senha: str) -> Usuario:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (username, senha) VALUES (%s, %s)",
                    (username, senha),
                )
                connection.commit()
                new_id = cursor.lastrowid
                return Usuario(id=new_id, username=username, senha=senha)
        finally:
            connection.close()
