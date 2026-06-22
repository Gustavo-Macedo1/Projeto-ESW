from datetime import datetime
from typing import List, Optional, Tuple

import mysql.connector

from database.connection import get_connection
from models.card import Cartao


class CardRepository:
    def list_by_board(self, user_id: int, project_id: int, board_id: int) -> List[Cartao]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.nome,
                        c.descricao,
                        c.prioridade,
                        c.data_criacao,
                        c.data_inicio,
                        c.data_conclusao,
                        c.data_limite,
                        c.responsavel_id,
                        c.coluna_id,
                        c.raia_id,
                        u.username AS responsavel_nome,
                        col.nome AS coluna_nome,
                        r.nome AS raia_nome
                    FROM cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    INNER JOIN usuarios u
                        ON u.id = c.responsavel_id
                    INNER JOIN raias r
                        ON r.id = c.raia_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    ORDER BY c.id DESC
                    """,
                    (user_id, project_id, board_id),
                )
                rows = cursor.fetchall() or []
                return [
                    Cartao(
                        id=row["id"],
                        nome=row["nome"],
                        descricao=row["descricao"],
                        prioridade=row["prioridade"],
                        data_criacao=row["data_criacao"],
                        data_inicio=row["data_inicio"],
                        data_conclusao=row["data_conclusao"],
                        data_limite=row["data_limite"],
                        responsavel_id=row["responsavel_id"],
                        coluna_id=row["coluna_id"],
                        raia_id=row["raia_id"],
                        responsavel_nome=row["responsavel_nome"],
                        coluna_nome=row["coluna_nome"],
                        raia_nome=row["raia_nome"],
                    )
                    for row in rows
                ]
        finally:
            connection.close()

    def get_by_id(self, user_id: int, project_id: int, board_id: int, card_id: int) -> Optional[Cartao]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.nome,
                        c.descricao,
                        c.prioridade,
                        c.data_criacao,
                        c.data_inicio,
                        c.data_conclusao,
                        c.data_limite,
                        c.responsavel_id,
                        c.coluna_id,
                        c.raia_id,
                        u.username AS responsavel_nome,
                        col.nome AS coluna_nome,
                        r.nome AS raia_nome
                    FROM cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    INNER JOIN usuarios u
                        ON u.id = c.responsavel_id
                    INNER JOIN raias r
                        ON r.id = c.raia_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND c.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id, card_id),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Cartao(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    prioridade=row["prioridade"],
                    data_criacao=row["data_criacao"],
                    data_inicio=row["data_inicio"],
                    data_conclusao=row["data_conclusao"],
                    data_limite=row["data_limite"],
                    responsavel_id=row["responsavel_id"],
                    coluna_id=row["coluna_id"],
                    raia_id=row["raia_id"],
                    responsavel_nome=row["responsavel_nome"],
                    coluna_nome=row["coluna_nome"],
                    raia_nome=row["raia_nome"],
                )
        finally:
            connection.close()

    def list_project_users(self, user_id: int, project_id: int) -> List[Tuple[int, str]]:
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
                            WHERE me.projeto_id = up.projeto_id AND me.usuario_id = %s
                        )
                    ORDER BY u.username
                    """,
                    (project_id, user_id),
                )
                rows = cursor.fetchall() or []
                return [(int(row["id"]), row["username"]) for row in rows]
        finally:
            connection.close()

    def list_board_columns(self, user_id: int, project_id: int, board_id: int) -> List[Tuple[int, str]]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT col.id, col.nome
                    FROM colunas col
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    ORDER BY col.ordem
                    """,
                    (user_id, project_id, board_id),
                )
                rows = cursor.fetchall() or []
                return [(int(row["id"]), row["nome"]) for row in rows]
        finally:
            connection.close()

    def create(
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
    ) -> Optional[Cartao]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                connection.start_transaction()
                cursor.execute(
                    """
                    SELECT 1
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
                    return None

                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios_projetos
                    WHERE usuario_id = %s AND projeto_id = %s
                    LIMIT 1
                    """,
                    (responsavel_id, project_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return None

                cursor.execute(
                    """
                    INSERT INTO cartoes (
                        nome,
                        descricao,
                        prioridade,
                        data_criacao,
                        data_inicio,
                        data_conclusao,
                        data_limite,
                        responsavel_id,
                        coluna_id,
                        raia_id
                    )
                    VALUES (%s, %s, %s, %s, NULL, NULL, %s, %s, %s, %s)
                    """,
                    (
                        nome,
                        descricao,
                        prioridade,
                        datetime.now(),
                        data_limite,
                        responsavel_id,
                        a_fazer_coluna_id,
                        lane_id,
                    ),
                )
                card_id = cursor.lastrowid
                connection.commit()
                return self.get_by_id(user_id, project_id, board_id, int(card_id))
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
        card_id: int,
        nome: str,
        responsavel_id: int,
        data_limite,
        prioridade: str,
        descricao: Optional[str],
    ) -> bool:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                connection.start_transaction()
                cursor.execute(
                    """
                    SELECT 1
                    FROM usuarios_projetos
                    WHERE usuario_id = %s AND projeto_id = %s
                    LIMIT 1
                    """,
                    (responsavel_id, project_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    UPDATE cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    SET
                        c.nome = %s,
                        c.descricao = %s,
                        c.prioridade = %s,
                        c.data_limite = %s,
                        c.responsavel_id = %s
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND c.id = %s
                    """,
                    (
                        nome,
                        descricao,
                        prioridade,
                        data_limite,
                        responsavel_id,
                        user_id,
                        project_id,
                        board_id,
                        card_id,
                    ),
                )
                updated = cursor.rowcount > 0
                if not updated:
                    connection.rollback()
                    return False

                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete(self, user_id: int, project_id: int, board_id: int, card_id: int) -> bool:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                connection.start_transaction()
                cursor.execute(
                    """
                    SELECT c.id
                    FROM cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND c.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id, card_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute("DELETE FROM historico_movimentacoes WHERE cartao_id = %s", (card_id,))
                cursor.execute("DELETE FROM cartoes WHERE id = %s", (card_id,))
                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def move(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        card_id: int,
        coluna_destino_id: int,
        raia_destino_id: int,
    ) -> bool:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                connection.start_transaction()
                cursor.execute(
                    """
                    SELECT c.id, c.coluna_id, c.raia_id, c.data_inicio
                    FROM cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    INNER JOIN quadros q
                        ON q.id = col.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND c.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id, card_id),
                )
                card = cursor.fetchone()
                if card is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    SELECT 1 FROM colunas
                    WHERE id = %s AND quadro_id = %s
                    LIMIT 1
                    """,
                    (coluna_destino_id, board_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    """
                    SELECT 1 FROM raias
                    WHERE id = %s AND quadro_id = %s
                    LIMIT 1
                    """,
                    (raia_destino_id, board_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return False

                cursor.execute("SELECT nome FROM colunas WHERE id = %s", (coluna_destino_id,))
                destino_coluna = cursor.fetchone()
                destino_nome = destino_coluna["nome"] if destino_coluna else ""

                data_inicio = card["data_inicio"]
                data_conclusao = None
                now = datetime.now()
                if destino_nome == "FAZENDO" and data_inicio is None:
                    data_inicio = now
                if destino_nome == "FEITO":
                    data_conclusao = now

                cursor.execute(
                    """
                    UPDATE cartoes
                    SET coluna_id = %s,
                        raia_id = %s,
                        data_inicio = %s,
                        data_conclusao = %s
                    WHERE id = %s
                    """,
                    (coluna_destino_id, raia_destino_id, data_inicio, data_conclusao, card_id),
                )

                cursor.execute(
                    """
                    INSERT INTO historico_movimentacoes (
                        cartao_id,
                        coluna_origem_id,
                        coluna_destino_id,
                        raia_origem_id,
                        raia_destino_id,
                        usuario_id,
                        data_movimentacao
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        card_id,
                        card["coluna_id"],
                        coluna_destino_id,
                        card["raia_id"],
                        raia_destino_id,
                        user_id,
                        now,
                    ),
                )

                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()
