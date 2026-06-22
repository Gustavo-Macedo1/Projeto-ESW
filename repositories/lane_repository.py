from typing import List, Optional

import mysql.connector

from database.connection import get_connection
from models.lane import Raia


class LaneRepository:
    def __init__(self) -> None:
        self._ensure_color_column()

    def _ensure_color_column(self) -> None:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SHOW COLUMNS FROM raias LIKE 'cor_fundo'")
                exists = cursor.fetchone()
                if exists:
                    return
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    ALTER TABLE raias
                    ADD COLUMN cor_fundo VARCHAR(20) NOT NULL DEFAULT '#F3F4F6'
                    """
                )
                connection.commit()
        finally:
            connection.close()

    def list_by_board(self, user_id: int, project_id: int, board_id: int) -> List[Raia]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT r.id, r.nome, r.descricao, r.quadro_id, r.cor_fundo
                    FROM raias r
                    INNER JOIN quadros q
                        ON q.id = r.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                    ORDER BY r.id
                    """,
                    (user_id, project_id, board_id),
                )
                rows = cursor.fetchall() or []
                return [
                    Raia(
                        id=row["id"],
                        nome=row["nome"],
                        descricao=row["descricao"],
                        quadro_id=row["quadro_id"],
                        cor_fundo=row["cor_fundo"] or "#F3F4F6",
                    )
                    for row in rows
                ]
        finally:
            connection.close()

    def get_by_id(self, user_id: int, project_id: int, board_id: int, lane_id: int) -> Optional[Raia]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT r.id, r.nome, r.descricao, r.quadro_id, r.cor_fundo
                    FROM raias r
                    INNER JOIN quadros q
                        ON q.id = r.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND r.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id, lane_id),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Raia(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    quadro_id=row["quadro_id"],
                    cor_fundo=row["cor_fundo"] or "#F3F4F6",
                )
        finally:
            connection.close()

    def get_principal_lane(self, board_id: int) -> Optional[Raia]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, nome, descricao, quadro_id, cor_fundo
                    FROM raias
                    WHERE quadro_id = %s AND LOWER(nome) = 'principal'
                    ORDER BY id
                    LIMIT 1
                    """,
                    (board_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Raia(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    quadro_id=row["quadro_id"],
                    cor_fundo=row["cor_fundo"] or "#F3F4F6",
                )
        finally:
            connection.close()

    def ensure_principal_lane(self, board_id: int) -> Raia:
        principal = self.get_principal_lane(board_id=board_id)
        if principal:
            return principal

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO raias (nome, descricao, quadro_id, cor_fundo)
                    VALUES ('Principal', 'Raia padrão do quadro', %s, '#F3F4F6')
                    """,
                    (board_id,),
                )
                connection.commit()
                lane_id = cursor.lastrowid
                return Raia(
                    id=lane_id,
                    nome="Principal",
                    descricao="Raia padrão do quadro",
                    quadro_id=board_id,
                    cor_fundo="#F3F4F6",
                )
        finally:
            connection.close()

    def create(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        nome: str,
        descricao: Optional[str],
        cor_fundo: str,
    ) -> Optional[Raia]:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
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
                    return None

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO raias (nome, descricao, quadro_id, cor_fundo)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nome, descricao, board_id, cor_fundo),
                )
                connection.commit()
                lane_id = cursor.lastrowid
                return Raia(
                    id=lane_id,
                    nome=nome,
                    descricao=descricao,
                    quadro_id=board_id,
                    cor_fundo=cor_fundo,
                )
        finally:
            connection.close()

    def update(
        self,
        user_id: int,
        project_id: int,
        board_id: int,
        lane_id: int,
        nome: str,
        descricao: Optional[str],
        cor_fundo: str,
    ) -> bool:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE raias r
                    INNER JOIN quadros q
                        ON q.id = r.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    SET r.nome = %s, r.descricao = %s, r.cor_fundo = %s
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND r.id = %s
                    """,
                    (nome, descricao, cor_fundo, user_id, project_id, board_id, lane_id),
                )
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    def delete(self, user_id: int, project_id: int, board_id: int, lane_id: int) -> bool:
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                connection.start_transaction()

                cursor.execute(
                    """
                    SELECT r.id, r.nome
                    FROM raias r
                    INNER JOIN quadros q
                        ON q.id = r.quadro_id
                    INNER JOIN usuarios_projetos up
                        ON up.projeto_id = q.projeto_id
                    WHERE up.usuario_id = %s
                        AND q.projeto_id = %s
                        AND q.id = %s
                        AND r.id = %s
                    LIMIT 1
                    """,
                    (user_id, project_id, board_id, lane_id),
                )
                lane_row = cursor.fetchone()
                if lane_row is None:
                    connection.rollback()
                    return False

                if str(lane_row["nome"]).strip().lower() == "principal":
                    connection.rollback()
                    raise ValueError("A raia Principal não pode ser excluída.")

                principal_lane = self.get_principal_lane(board_id=board_id)
                if not principal_lane:
                    principal_lane = self.ensure_principal_lane(board_id=board_id)

                principal_lane_id = int(principal_lane.id)

                cursor.execute(
                    """
                    UPDATE cartoes c
                    INNER JOIN colunas col
                        ON col.id = c.coluna_id
                    SET c.raia_id = %s
                    WHERE col.quadro_id = %s AND c.raia_id = %s
                    """,
                    (principal_lane_id, board_id, lane_id),
                )

                cursor.execute(
                    """
                    UPDATE historico_movimentacoes hm
                    INNER JOIN cartoes c ON c.id = hm.cartao_id
                    INNER JOIN colunas col ON col.id = c.coluna_id
                    SET
                        hm.raia_origem_id = CASE
                            WHEN hm.raia_origem_id = %s THEN %s
                            ELSE hm.raia_origem_id
                        END,
                        hm.raia_destino_id = CASE
                            WHEN hm.raia_destino_id = %s THEN %s
                            ELSE hm.raia_destino_id
                        END
                    WHERE col.quadro_id = %s
                        AND (hm.raia_origem_id = %s OR hm.raia_destino_id = %s)
                    """,
                    (
                        lane_id,
                        principal_lane_id,
                        lane_id,
                        principal_lane_id,
                        board_id,
                        lane_id,
                        lane_id,
                    ),
                )

                cursor.execute(
                    "DELETE FROM raias WHERE id = %s AND quadro_id = %s",
                    (lane_id, board_id),
                )

                connection.commit()
                return True
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            connection.close()
