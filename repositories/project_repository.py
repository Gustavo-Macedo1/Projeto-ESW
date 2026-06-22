from typing import List, Optional

import mysql.connector

from database.connection import get_connection
from models.project import Projeto


class ProjectRepository:
    def list_by_user(self, user_id: int) -> List[Projeto]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        p.id,
                        p.nome,
                        p.visibilidade,
                        COUNT(q.id) AS total_quadros
                    FROM projetos p
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = p.id
                    LEFT JOIN quadros q
                        ON q.projeto_id = p.id
                    WHERE up.usuario_id = %s
                    GROUP BY p.id, p.nome, p.visibilidade
                    ORDER BY p.nome
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall() or []
                return [
                    Projeto(
                        id=row["id"],
                        nome=row["nome"],
                        visibilidade=row["visibilidade"],
                        total_quadros=int(row["total_quadros"] or 0),
                    )
                    for row in rows
                ]
        finally:
            connection.close()

    def get_user_project_by_name(self, user_id: int, nome: str) -> Optional[Projeto]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        p.id,
                        p.nome,
                        p.visibilidade,
                        COUNT(q.id) AS total_quadros
                    FROM projetos p
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = p.id
                    LEFT JOIN quadros q
                        ON q.projeto_id = p.id
                    WHERE up.usuario_id = %s
                        AND LOWER(p.nome) = LOWER(%s)
                    GROUP BY p.id, p.nome, p.visibilidade
                    LIMIT 1
                    """,
                    (user_id, nome),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Projeto(
                    id=row["id"],
                    nome=row["nome"],
                    visibilidade=row["visibilidade"],
                    total_quadros=int(row["total_quadros"] or 0),
                )
        finally:
            connection.close()

    def get_user_project_by_id(self, user_id: int, project_id: int) -> Optional[Projeto]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        p.id,
                        p.nome,
                        p.visibilidade,
                        COUNT(q.id) AS total_quadros
                    FROM projetos p
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = p.id
                    LEFT JOIN quadros q
                        ON q.projeto_id = p.id
                    WHERE up.usuario_id = %s
                        AND p.id = %s
                    GROUP BY p.id, p.nome, p.visibilidade
                    LIMIT 1
                    """,
                    (user_id, project_id),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Projeto(
                    id=row["id"],
                    nome=row["nome"],
                    visibilidade=row["visibilidade"],
                    total_quadros=int(row["total_quadros"] or 0),
                )
        finally:
            connection.close()

    def create_for_user(self, user_id: int, nome: str, visibilidade: str = "PRIVADO") -> Projeto:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                connection.start_transaction()
                cursor.execute(
                    "INSERT INTO projetos (nome, visibilidade) VALUES (%s, %s)",
                    (nome, visibilidade),
                )
                project_id = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO usuarios_projetos (usuario_id, projeto_id) VALUES (%s, %s)",
                    (user_id, project_id),
                )
                connection.commit()

                return Projeto(
                    id=project_id,
                    nome=nome,
                    visibilidade=visibilidade,
                    total_quadros=0,
                )
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete_project_for_user(self, user_id: int, project_id: int) -> bool:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                connection.start_transaction()

                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios_projetos
                    WHERE usuario_id = %s AND projeto_id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    "DELETE FROM usuarios_projetos WHERE projeto_id = %s",
                    (project_id,),
                )
                cursor.execute(
                    "DELETE FROM projetos WHERE id = %s",
                    (project_id,),
                )
                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_project_members(self, user_id: int, project_id: int) -> List[tuple[int, str]]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.username
                    FROM usuarios u
                    INNER JOIN usuarios_projetos up
                        ON up.usuario_id = u.id
                    WHERE up.projeto_id = %s
                      AND EXISTS (
                        SELECT 1
                        FROM usuarios_projetos me
                        WHERE me.projeto_id = up.projeto_id
                          AND me.usuario_id = %s
                      )
                    ORDER BY u.username
                    """,
                    (project_id, user_id),
                )
                rows = cursor.fetchall() or []
                return [(int(row["id"]), row["username"]) for row in rows]
        finally:
            connection.close()

    def list_users_not_in_project(self, user_id: int, project_id: int) -> List[tuple[int, str]]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.username
                    FROM usuarios u
                    LEFT JOIN usuarios_projetos up
                        ON up.usuario_id = u.id
                       AND up.projeto_id = %s
                    WHERE up.usuario_id IS NULL
                      AND EXISTS (
                        SELECT 1
                        FROM usuarios_projetos me
                        WHERE me.projeto_id = %s
                          AND me.usuario_id = %s
                      )
                    ORDER BY u.username
                    """,
                    (project_id, project_id, user_id),
                )
                rows = cursor.fetchall() or []
                return [(int(row["id"]), row["username"]) for row in rows]
        finally:
            connection.close()

    def add_user_to_project(self, user_id: int, project_id: int, invited_user_id: int) -> bool:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                connection.start_transaction()

                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios_projetos
                    WHERE usuario_id = %s AND projeto_id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (invited_user_id,),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios_projetos
                    WHERE usuario_id = %s AND projeto_id = %s
                    LIMIT 1
                    """,
                    (invited_user_id, project_id),
                )
                if cursor.fetchone() is not None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    INSERT INTO usuarios_projetos (usuario_id, projeto_id)
                    VALUES (%s, %s)
                    """,
                    (invited_user_id, project_id),
                )
                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()
