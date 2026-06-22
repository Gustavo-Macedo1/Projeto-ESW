from typing import List, Optional

import mysql.connector

from database.connection import get_connection
from models.board import Quadro


class BoardRepository:
    def list_by_project(self, user_id: int, project_id: int) -> List[Quadro]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        q.id,
                        q.nome,
                        q.max_integrantes,
                        q.visibilidade,
                        q.wip,
                        q.projeto_id,
                        COUNT(c.id) AS total_cartoes,
                        SUM(
                            CASE
                                WHEN col.nome = 'FEITO' AND c.id IS NOT NULL THEN 1
                                ELSE 0
                            END
                        ) AS total_cartoes_feitos
                    FROM quadros q
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    LEFT JOIN colunas col
                        ON col.quadro_id = q.id
                    LEFT JOIN cartoes c
                        ON c.coluna_id = col.id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                    GROUP BY
                        q.id,
                        q.nome,
                        q.max_integrantes,
                        q.visibilidade,
                        q.wip,
                        q.projeto_id
                    ORDER BY q.nome
                    """,
                    (user_id, project_id),
                )
                rows = cursor.fetchall() or []
                return [
                    Quadro(
                        id=row["id"],
                        nome=row["nome"],
                        max_integrantes=row["max_integrantes"],
                        visibilidade=row["visibilidade"],
                        wip=row["wip"],
                        projeto_id=row["projeto_id"],
                        total_cartoes=int(row["total_cartoes"] or 0),
                        total_cartoes_feitos=int(row["total_cartoes_feitos"] or 0),
                    )
                    for row in rows
                ]
        finally:
            connection.close()

    def get_by_id(self, user_id: int, project_id: int, board_id: int) -> Optional[Quadro]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        q.id,
                        q.nome,
                        q.max_integrantes,
                        q.visibilidade,
                        q.wip,
                        q.projeto_id,
                        COUNT(c.id) AS total_cartoes,
                        SUM(
                            CASE
                                WHEN col.nome = 'FEITO' AND c.id IS NOT NULL THEN 1
                                ELSE 0
                            END
                        ) AS total_cartoes_feitos
                    FROM quadros q
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    LEFT JOIN colunas col
                        ON col.quadro_id = q.id
                    LEFT JOIN cartoes c
                        ON c.coluna_id = col.id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    GROUP BY
                        q.id,
                        q.nome,
                        q.max_integrantes,
                        q.visibilidade,
                        q.wip,
                        q.projeto_id
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Quadro(
                    id=row["id"],
                    nome=row["nome"],
                    max_integrantes=row["max_integrantes"],
                    visibilidade=row["visibilidade"],
                    wip=row["wip"],
                    projeto_id=row["projeto_id"],
                    total_cartoes=int(row["total_cartoes"] or 0),
                    total_cartoes_feitos=int(row["total_cartoes_feitos"] or 0),
                )
        finally:
            connection.close()

    def create(
        self,
        user_id: int,
        project_id: int,
        nome: str,
        max_integrantes: int,
        visibilidade: str,
        wip: int,
    ) -> Optional[Quadro]:
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
                    return None

                cursor.execute(
                    """
                    INSERT INTO quadros (nome, max_integrantes, visibilidade, wip, projeto_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (nome, max_integrantes, visibilidade, wip, project_id),
                )
                board_id = cursor.lastrowid

                default_columns = [("A_FAZER", 1), ("FAZENDO", 2), ("FEITO", 3)]
                for column_name, ordem in default_columns:
                    cursor.execute(
                        """
                        INSERT INTO colunas (nome, ordem, quadro_id)
                        VALUES (%s, %s, %s)
                        """,
                        (column_name, ordem, board_id),
                    )

                cursor.execute(
                    """
                    INSERT INTO raias (nome, descricao, quadro_id)
                    VALUES ('Principal', 'Raia padrão do quadro', %s)
                    """,
                    (board_id,),
                )

                connection.commit()
                return Quadro(
                    id=board_id,
                    nome=nome,
                    max_integrantes=max_integrantes,
                    visibilidade=visibilidade,
                    wip=wip,
                    projeto_id=project_id,
                )
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def update(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        nome: str,
        max_integrantes: int,
        visibilidade: str,
        wip: int,
    ) -> bool:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE quadros q
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    SET
                        q.nome = %s,
                        q.max_integrantes = %s,
                        q.visibilidade = %s,
                        q.wip = %s
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    """,
                    (nome, max_integrantes, visibilidade, wip, user_id, project_id, board_id),
                )
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    def delete(self, user_id: int, project_id: int, board_id: int) -> bool:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                connection.start_transaction()

                cursor.execute(
                    """
                    SELECT q.id
                    FROM quadros q
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    DELETE hm
                    FROM historico_movimentacoes hm
                    INNER JOIN cartoes c ON c.id = hm.cartao_id
                    INNER JOIN colunas col ON col.id = c.coluna_id
                    WHERE col.quadro_id = %s
                    """,
                    (board_id,),
                )

                cursor.execute(
                    """
                    DELETE c
                    FROM cartoes c
                    INNER JOIN colunas col ON col.id = c.coluna_id
                    WHERE col.quadro_id = %s
                    """,
                    (board_id,),
                )

                cursor.execute("DELETE FROM raias WHERE quadro_id = %s", (board_id,))
                cursor.execute("DELETE FROM colunas WHERE quadro_id = %s", (board_id,))
                cursor.execute(
                    """
                    DELETE FROM quadros
                    WHERE id = %s AND projeto_id = %s
                    """,
                    (board_id, project_id),
                )

                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()
