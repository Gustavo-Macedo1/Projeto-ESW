from datetime import date

import streamlit as st

from controllers.board_controller import BoardController
from controllers.card_controller import CardController
from controllers.lane_controller import LaneController
from controllers.project_controller import ProjectController


COLUMN_LABELS = {
    "A_FAZER": "A Fazer",
    "FAZENDO": "Fazendo",
    "FEITO": "Feito",
}
KANBAN_COLUMN_HEIGHT = 250

DIALOG_FLAGS = [
    "abrir_popup_novo_quadro",
    "abrir_popup_alterar_quadro",
    "abrir_popup_excluir_quadro",
    "abrir_popup_criar_raia",
    "abrir_popup_atualizar_raia",
    "abrir_popup_excluir_raia",
    "abrir_popup_ler_raias",
    "abrir_popup_criar_card",
    "abrir_popup_atualizar_card",
    "abrir_popup_excluir_card",
    "abrir_popup_mover_card",
    "abrir_popup_ler_card",
    "abrir_popup_convidar_pessoas",
]


def _init_state() -> None:
    defaults = {
        "abrir_popup_novo_quadro": False,
        "abrir_popup_alterar_quadro": False,
        "abrir_popup_excluir_quadro": False,
        "flash_quadro_sucesso": None,
        "flash_quadro_erro": None,
        "modo_alterar_passo": "selecionar",
        "quadro_edicao_id": None,
        "abrir_popup_criar_raia": False,
        "abrir_popup_atualizar_raia": False,
        "abrir_popup_excluir_raia": False,
        "abrir_popup_ler_raias": False,
        "abrir_popup_criar_card": False,
        "abrir_popup_atualizar_card": False,
        "abrir_popup_excluir_card": False,
        "abrir_popup_mover_card": False,
        "abrir_popup_ler_card": False,
        "abrir_popup_convidar_pessoas": False,
        "card_lido_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _resetar_fluxo_alteracao() -> None:
    st.session_state["modo_alterar_passo"] = "selecionar"
    st.session_state["quadro_edicao_id"] = None


def _fechar_todos_dialogos() -> None:
    for flag in DIALOG_FLAGS:
        st.session_state[flag] = False


def _abrir_dialogo(flag: str) -> None:
    _fechar_todos_dialogos()
    st.session_state[flag] = True


def _kanban_column_container():
    try:
        return st.container(height=KANBAN_COLUMN_HEIGHT, border=True)
    except TypeError:
        return st.container(border=True)


def _mostrar_feedback() -> None:
    if st.session_state.get("flash_quadro_sucesso"):
        st.success(st.session_state["flash_quadro_sucesso"])
        st.session_state["flash_quadro_sucesso"] = None

    if st.session_state.get("flash_quadro_erro"):
        st.error(st.session_state["flash_quadro_erro"])
        st.session_state["flash_quadro_erro"] = None


def _dialog_novo_quadro(
    board_controller: BoardController,
    user_id: int,
    project_id: int,
) -> None:
    @st.dialog("Novo quadro")
    def _novo():
        with st.form("form_novo_quadro"):
            nome = st.text_input("Nome do quadro")
            max_integrantes = st.number_input(
                "Número máximo de integrantes",
                min_value=1,
                step=1,
                value=5,
            )
            visibilidade = st.selectbox("Visibilidade", options=["PUBLICO", "PRIVADO"])
            wip = st.number_input("WIP", min_value=1, step=1, value=3)
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = board_controller.criar_quadro(
                user_id=user_id,
                project_id=project_id,
                nome=nome,
                max_integrantes=int(max_integrantes),
                visibilidade=visibilidade,
                wip=int(wip),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _novo()


def _dialog_alterar_quadro(
    board_controller: BoardController,
    user_id: int,
    project_id: int,
    boards,
) -> None:
    @st.dialog("Alterar quadro")
    def _alterar():
        if not boards:
            st.info("Este projeto ainda não tem quadros.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_alterar_sem_quadros",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                _resetar_fluxo_alteracao()
                st.rerun()
            return

        boards_map = {board.id: board for board in boards}
        passo = st.session_state.get("modo_alterar_passo", "selecionar")

        if passo == "selecionar":
            with st.form("form_selecionar_quadro_alteracao"):
                selected_board_id = st.selectbox(
                    "Qual quadro deseja alterar?",
                    options=list(boards_map.keys()),
                    format_func=lambda item: boards_map[item].nome,
                )
                col_avancar, col_cancelar = st.columns(2)
                avancar = col_avancar.form_submit_button(
                    "Avançar",
                    use_container_width=True,
                    type="secondary",
                )
                cancelar = col_cancelar.form_submit_button(
                    "Cancelar",
                    use_container_width=True,
                    type="secondary",
                )

            if cancelar:
                _fechar_todos_dialogos()
                _resetar_fluxo_alteracao()
                st.rerun()

            if avancar:
                st.session_state["quadro_edicao_id"] = int(selected_board_id)
                st.session_state["modo_alterar_passo"] = "editar"
                st.rerun()

        if st.session_state.get("modo_alterar_passo") == "editar":
            board_id = st.session_state.get("quadro_edicao_id")
            board = boards_map.get(board_id)
            if not board:
                board = board_controller.obter_quadro(
                    user_id=user_id,
                    project_id=project_id,
                    board_id=int(board_id),
                )
            if not board:
                st.error("Quadro não encontrado.")
                if st.button(
                    ":material/arrow_back: Voltar",
                    use_container_width=True,
                    key="voltar_alterar_nao_encontrado",
                    type="secondary",
                ):
                    _fechar_todos_dialogos()
                    _resetar_fluxo_alteracao()
                    st.rerun()
                return

            with st.form("form_alterar_quadro"):
                nome = st.text_input("Nome do quadro", value=board.nome)
                max_integrantes = st.number_input(
                    "Número máximo de integrantes",
                    min_value=1,
                    step=1,
                    value=int(board.max_integrantes),
                )
                visibilidade_options = ["PUBLICO", "PRIVADO"]
                visibilidade_idx = visibilidade_options.index(board.visibilidade)
                visibilidade = st.selectbox(
                    "Visibilidade",
                    options=visibilidade_options,
                    index=visibilidade_idx,
                )
                wip = st.number_input("WIP", min_value=1, step=1, value=int(board.wip))
                col_salvar, col_voltar = st.columns(2)
                salvar = col_salvar.form_submit_button(
                    "Salvar",
                    use_container_width=True,
                    type="secondary",
                )
                voltar = col_voltar.form_submit_button(
                    "Voltar",
                    use_container_width=True,
                    type="secondary",
                )

            if voltar:
                _resetar_fluxo_alteracao()
                st.rerun()

            if salvar:
                sucesso, mensagem = board_controller.atualizar_quadro(
                    user_id=user_id,
                    project_id=project_id,
                    board_id=int(board.id),
                    nome=nome,
                    max_integrantes=int(max_integrantes),
                    visibilidade=visibilidade,
                    wip=int(wip),
                )
                if sucesso:
                    _fechar_todos_dialogos()
                    st.session_state["flash_quadro_sucesso"] = mensagem
                    _resetar_fluxo_alteracao()
                    st.rerun()
                st.error(mensagem)

    _alterar()


def _dialog_excluir_quadro(
    board_controller: BoardController,
    user_id: int,
    project_id: int,
    boards,
) -> None:
    @st.dialog("Excluir quadro")
    def _excluir():
        if not boards:
            st.info("Este projeto ainda não tem quadros.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_excluir_sem_quadros",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        boards_map = {board.id: board for board in boards}
        with st.form("form_excluir_quadro"):
            board_id = st.selectbox(
                "Qual quadro deseja excluir?",
                options=list(boards_map.keys()),
                format_func=lambda item: boards_map[item].nome,
            )
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = board_controller.excluir_quadro(
                user_id=user_id,
                project_id=project_id,
                board_id=int(board_id),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                if st.session_state.get("quadro_selecionado_id") == int(board_id):
                    st.session_state["quadro_selecionado_id"] = None
                st.rerun()
            st.error(mensagem)

    _excluir()


def _render_lista_quadros(boards) -> None:
    st.markdown("---")
    if not boards:
        st.info("Nenhum quadro criado neste projeto.")
        return

    grid_cols = st.columns(3)
    for idx, board in enumerate(boards):
        progresso = 0.0
        if board.total_cartoes > 0:
            progresso = board.total_cartoes_feitos / board.total_cartoes
        percentual = int(progresso * 100)

        with grid_cols[idx % 3]:
            with st.container(border=True):
                if st.button(
                    board.nome,
                    key=f"board_btn_{board.id}",
                    use_container_width=True,
                    type="secondary",
                ):
                    _fechar_todos_dialogos()
                    st.session_state["quadro_selecionado_id"] = board.id
                    st.rerun()
                st.write(f"Integrantes: {board.max_integrantes}")
                st.write(f"Visibilidade: {board.visibilidade}")
                st.progress(progresso)
                st.caption(
                    f"Progresso: {percentual}% ({board.total_cartoes_feitos}/{board.total_cartoes})"
                )


def _dialog_convidar_pessoas(project_controller: ProjectController, user_id: int, project_id: int) -> None:
    @st.dialog("Convidar pessoas")
    def _convidar():
        st.write("Selecione o usuário a ser integrado ao projeto")
        usuarios = project_controller.listar_usuarios_convidaveis(
            user_id=user_id,
            project_id=project_id,
        )
        if not usuarios:
            st.info("Não há usuários disponíveis para convidar.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_convidar_sem_usuarios",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        usuarios_map = {uid: username for uid, username in usuarios}
        with st.form("form_convidar_pessoas"):
            invited_user_id = st.selectbox(
                "Usuário",
                options=list(usuarios_map.keys()),
                format_func=lambda item: usuarios_map[item],
            )
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = project_controller.convidar_usuario_para_projeto(
                user_id=user_id,
                project_id=project_id,
                invited_user_id=int(invited_user_id),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _convidar()


def _render_integrantes_section(project_controller: ProjectController, user_id: int, project_id: int) -> None:
    st.subheader("Integrantes")
    integrantes = project_controller.listar_integrantes_do_projeto(
        user_id=user_id,
        project_id=project_id,
    )
    if not integrantes:
        st.info("Nenhum integrante encontrado.")
    else:
        for _, username in integrantes:
            st.write(f"- {username}")

    if st.button(
        "Convidar pessoas",
        key="btn_convidar_pessoas",
        use_container_width=False,
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_convidar_pessoas")
        st.rerun()


def _dialog_criar_raia(lane_controller: LaneController, user_id: int, project_id: int, board_id: int) -> None:
    @st.dialog("Criar raia")
    def _criar():
        with st.form("form_criar_raia"):
            nome = st.text_input("Nome")
            descricao = st.text_area("Descrição")
            cor_fundo = st.color_picker("Cor da raia", value="#F3F4F6")
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = lane_controller.criar_raia(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                nome=nome,
                descricao=descricao,
                cor_fundo=cor_fundo,
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _criar()


def _dialog_atualizar_raia(
    lane_controller: LaneController,
    user_id: int,
    project_id: int,
    board_id: int,
    lanes,
) -> None:
    @st.dialog("Atualizar raia")
    def _atualizar():
        if not lanes:
            st.info("Não há raias para atualizar.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_atualizar_raia_vazio",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        lanes_map = {lane.id: lane for lane in lanes}
        selected_lane_id = st.selectbox(
            "Selecione a raia",
            options=list(lanes_map.keys()),
            format_func=lambda item: lanes_map[item].nome,
            key="selecionar_raia_atualizar",
        )
        lane = lanes_map[int(selected_lane_id)]

        with st.form("form_atualizar_raia"):
            nome = st.text_input("Nome", value=lane.nome)
            descricao = st.text_area("Descrição", value=lane.descricao or "")
            cor_fundo = st.color_picker("Cor da raia", value=lane.cor_fundo or "#F3F4F6")
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = lane_controller.atualizar_raia(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                lane_id=int(selected_lane_id),
                nome=nome,
                descricao=descricao,
                cor_fundo=cor_fundo,
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _atualizar()


def _dialog_excluir_raia(
    lane_controller: LaneController,
    user_id: int,
    project_id: int,
    board_id: int,
    lanes,
) -> None:
    @st.dialog("Excluir raia")
    def _excluir():
        if not lanes:
            st.info("Não há raias para excluir.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_excluir_raia_vazio",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        lanes_map = {lane.id: lane for lane in lanes}
        with st.form("form_excluir_raia"):
            lane_id = st.selectbox(
                "Selecione a raia",
                options=list(lanes_map.keys()),
                format_func=lambda item: lanes_map[item].nome,
            )
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = lane_controller.excluir_raia(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                lane_id=int(lane_id),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _excluir()


def _dialog_ler_raias(lanes) -> None:
    @st.dialog("Ler raias")
    def _ler():
        if not lanes:
            st.info("Não há raias neste quadro.")
        else:
            for lane in lanes:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='background:{lane.cor_fundo};padding:6px;border-radius:6px;'></div>",
                        unsafe_allow_html=True,
                    )
                    st.write(f"**{lane.nome}**")
                    st.caption(lane.descricao or "Sem descrição.")
        if st.button(
            "Fechar",
            use_container_width=True,
            key="fechar_popup_ler_raias",
            type="secondary",
        ):
            _fechar_todos_dialogos()
            st.rerun()

    _ler()


def _dialog_ler_card(cards) -> None:
    @st.dialog("Detalhes do card")
    def _ler_card():
        card_lido_id = st.session_state.get("card_lido_id")
        if not card_lido_id:
            st.info("Nenhum card selecionado.")
        else:
            card_map = {card.id: card for card in cards}
            card = card_map.get(int(card_lido_id))
            if not card:
                st.info("Card não encontrado.")
            else:
                st.write(f"**Nome:** {card.nome}")
                st.write(f"**Responsável:** {card.responsavel_nome}")
                st.write(f"**Prioridade:** {card.prioridade}")
                st.write(f"**Data limite:** {card.data_limite or 'Não definida'}")
                st.write(
                    f"**Raia/Coluna:** {card.raia_nome} / "
                    f"{COLUMN_LABELS.get(card.coluna_nome, card.coluna_nome)}"
                )
                st.write("**Descrição:**")
                st.caption(card.descricao or "Sem descrição.")

        if st.button(
            "Fechar",
            use_container_width=True,
            key="fechar_popup_ler_card",
            type="secondary",
        ):
            st.session_state["card_lido_id"] = None
            _fechar_todos_dialogos()
            st.rerun()

    _ler_card()


def _dialog_criar_card(
    card_controller: CardController,
    user_id: int,
    project_id: int,
    board_id: int,
    principal_lane_id: int,
    a_fazer_coluna_id: int,
) -> None:
    @st.dialog("Criar cards")
    def _criar():
        users = card_controller.listar_usuarios_do_projeto(user_id=user_id, project_id=project_id)
        if not users:
            st.error("Não há usuários disponíveis para definir responsável.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_criar_card_sem_usuarios",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        users_map = {user_id_item: username for user_id_item, username in users}
        with st.form("form_criar_card"):
            nome = st.text_input("Nome")
            responsavel_id = st.selectbox(
                "Responsável",
                options=list(users_map.keys()),
                format_func=lambda item: users_map[item],
            )
            data_limite = st.date_input("Data limite para término", value=date.today())
            prioridade = st.selectbox("Prioridade", options=["BAIXA", "MEDIA", "ALTA", "CRITICA"])
            descricao = st.text_area("Descrição")
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = card_controller.criar_card(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                nome=nome,
                responsavel_id=int(responsavel_id),
                data_limite=data_limite,
                prioridade=prioridade,
                descricao=descricao,
                lane_id=principal_lane_id,
                a_fazer_coluna_id=a_fazer_coluna_id,
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _criar()


def _dialog_atualizar_card(
    card_controller: CardController,
    user_id: int,
    project_id: int,
    board_id: int,
    cards,
) -> None:
    @st.dialog("Atualizar card")
    def _atualizar():
        if not cards:
            st.info("Não há cards para atualizar.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_atualizar_card_vazio",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        cards_map = {card.id: card for card in cards}
        users = card_controller.listar_usuarios_do_projeto(user_id=user_id, project_id=project_id)
        users_map = {user_id_item: username for user_id_item, username in users}
        if not users_map:
            st.error("Não há usuários disponíveis para definir responsável.")
            return

        selected_card_id = st.selectbox(
            "Selecione o card",
            options=list(cards_map.keys()),
            format_func=lambda item: cards_map[item].nome,
            key="selecionar_card_atualizar",
        )
        card = cards_map[int(selected_card_id)]
        prioridade_options = ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
        prioridade_idx = prioridade_options.index(card.prioridade)
        responsavel_ids = list(users_map.keys())
        responsavel_idx = 0
        if card.responsavel_id in responsavel_ids:
            responsavel_idx = responsavel_ids.index(card.responsavel_id)

        with st.form("form_atualizar_card"):
            nome = st.text_input("Nome", value=card.nome)
            responsavel_id = st.selectbox(
                "Responsável",
                options=responsavel_ids,
                format_func=lambda item: users_map[item],
                index=responsavel_idx,
            )
            data_limite = st.date_input("Data limite para término", value=card.data_limite or date.today())
            prioridade = st.selectbox("Prioridade", options=prioridade_options, index=prioridade_idx)
            descricao = st.text_area("Descrição", value=card.descricao or "")
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = card_controller.atualizar_card(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=int(selected_card_id),
                nome=nome,
                responsavel_id=int(responsavel_id),
                data_limite=data_limite,
                prioridade=prioridade,
                descricao=descricao,
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _atualizar()


def _dialog_excluir_card(
    card_controller: CardController,
    user_id: int,
    project_id: int,
    board_id: int,
    cards,
) -> None:
    @st.dialog("Excluir card")
    def _excluir():
        if not cards:
            st.info("Não há cards para excluir.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_excluir_card_vazio",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        cards_map = {card.id: card for card in cards}
        with st.form("form_excluir_card"):
            card_id = st.selectbox(
                "Selecione o card",
                options=list(cards_map.keys()),
                format_func=lambda item: cards_map[item].nome,
            )
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = card_controller.excluir_card(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=int(card_id),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                if st.session_state.get("card_lido_id") == int(card_id):
                    st.session_state["card_lido_id"] = None
                st.rerun()
            st.error(mensagem)

    _excluir()


def _dialog_mover_card(
    card_controller: CardController,
    user_id: int,
    project_id: int,
    board_id: int,
    cards,
    lanes,
) -> None:
    @st.dialog("Mover card")
    def _mover():
        if not cards:
            st.info("Não há cards para mover.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_mover_card_vazio",
                type="secondary",
            ):
                _fechar_todos_dialogos()
                st.rerun()
            return

        columns = card_controller.listar_colunas_do_quadro(
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
        )
        if not columns or not lanes:
            st.error("O quadro precisa ter colunas e raias para mover cards.")
            return

        cards_map = {card.id: card for card in cards}
        columns_map = {col_id: col_name for col_id, col_name in columns}
        lanes_map = {lane.id: lane.nome for lane in lanes}

        with st.form("form_mover_card"):
            card_id = st.selectbox(
                "Card",
                options=list(cards_map.keys()),
                format_func=lambda item: cards_map[item].nome,
            )
            st.write("Selecione a coluna e a raia de destino")
            coluna_destino_id = st.selectbox(
                "Coluna de destino",
                options=list(columns_map.keys()),
                format_func=lambda item: COLUMN_LABELS.get(columns_map[item], columns_map[item]),
            )
            raia_destino_id = st.selectbox(
                "Raia de destino",
                options=list(lanes_map.keys()),
                format_func=lambda item: lanes_map[item],
            )
            col_confirmar, col_cancelar = st.columns(2)
            confirmar = col_confirmar.form_submit_button(
                "Confirmar",
                use_container_width=True,
                type="secondary",
            )
            cancelar = col_cancelar.form_submit_button(
                "Cancelar",
                use_container_width=True,
                type="secondary",
            )

        if cancelar:
            _fechar_todos_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = card_controller.mover_card(
                user_id=user_id,
                project_id=project_id,
                board_id=board_id,
                card_id=int(card_id),
                coluna_destino_id=int(coluna_destino_id),
                raia_destino_id=int(raia_destino_id),
            )
            if sucesso:
                _fechar_todos_dialogos()
                st.session_state["flash_quadro_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _mover()


def _render_kanban_section(lanes, columns, cards) -> None:
    st.subheader("Quadro KanBan")
    st.caption("Clique em um card para ler seu conteúdo.")

    cards_por_raia_coluna = {}
    for card in cards:
        key = (card.raia_id, card.coluna_id)
        cards_por_raia_coluna.setdefault(key, []).append(card)

    for lane in lanes:
        st.markdown(f"**{lane.nome}**")
        column_widgets = st.columns(3)
        for idx, (col_id, col_name) in enumerate(columns):
            with column_widgets[idx % 3]:
                with _kanban_column_container():
                    st.markdown(
                        f"""
                        <div style="
                            background:{lane.cor_fundo};
                            padding:6px 8px;
                            border-radius:6px;
                            margin-bottom:8px;
                            border:1px solid #D9DDE3;
                            font-weight:600;
                        ">
                            {COLUMN_LABELS.get(col_name, col_name)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    cards_da_coluna = cards_por_raia_coluna.get((lane.id, col_id), [])
                    if not cards_da_coluna:
                        st.caption("Sem cards.")
                    for card in cards_da_coluna:
                        if st.button(
                            card.nome,
                            key=f"card_view_{lane.id}_{col_id}_{card.id}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            st.session_state["card_lido_id"] = card.id
                            _abrir_dialogo("abrir_popup_ler_card")
                            st.rerun()


def _render_lanes_commands_section(
    lane_controller: LaneController,
    user_id: int,
    project_id: int,
    board_id: int,
    lanes,
) -> None:
    st.subheader("Raias - Comandos")
    st.caption("Clique nos botões para criar, atualizar, excluir ou ler raias.")

    col_criar, col_atualizar, col_excluir, col_ler = st.columns(4)
    if col_criar.button(
        ":material/add: Criar",
        use_container_width=True,
        key="btn_raia_criar",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_criar_raia")
        st.rerun()
    if col_atualizar.button(
        ":material/edit: Atualizar",
        use_container_width=True,
        key="btn_raia_atualizar",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_atualizar_raia")
        st.rerun()
    if col_excluir.button(
        ":material/delete: Excluir",
        use_container_width=True,
        key="btn_raia_excluir",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_excluir_raia")
        st.rerun()
    if col_ler.button(
        ":material/visibility: Ler",
        use_container_width=True,
        key="btn_raia_ler",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_ler_raias")
        st.rerun()


def _render_cards_commands_section(
    card_controller: CardController,
    user_id: int,
    project_id: int,
    board_id: int,
    cards,
    lanes,
    columns,
) -> None:
    st.subheader("Cards - Comandos")
    st.caption("Clique nos botões para criar, atualizar, excluir ou mover cards.")

    col_criar, col_atualizar, col_excluir, col_mover = st.columns(4)
    if col_criar.button(
        ":material/add: Criar",
        use_container_width=True,
        key="btn_card_criar",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_criar_card")
        st.rerun()
    if col_atualizar.button(
        ":material/edit: Atualizar",
        use_container_width=True,
        key="btn_card_atualizar",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_atualizar_card")
        st.rerun()
    if col_excluir.button(
        ":material/delete: Excluir",
        use_container_width=True,
        key="btn_card_excluir",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_excluir_card")
        st.rerun()
    if col_mover.button(
        ":material/move_item: Mover",
        use_container_width=True,
        key="btn_card_mover",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_mover_card")
        st.rerun()

    colunas_map = {col_name: col_id for col_id, col_name in columns}
    a_fazer_coluna_id = colunas_map.get("A_FAZER")
    principal_lane = next((lane for lane in lanes if lane.nome.strip().lower() == "principal"), None)

    if st.session_state.get("abrir_popup_criar_card"):
        if not principal_lane or not a_fazer_coluna_id:
            _fechar_todos_dialogos()
            st.session_state["flash_quadro_erro"] = (
                "Não foi possível encontrar a raia Principal ou a coluna A_FAZER."
            )
            st.rerun()


def _media_duracao_dias(valores_dias) -> float:
    if not valores_dias:
        return 0.0
    return float(sum(valores_dias) / len(valores_dias))


def _formatar_duracao(media_dias: float, unidade: str) -> str:
    if media_dias <= 0:
        return "Sem dados"
    if unidade == "dias":
        return f"{media_dias:.2f} dias"
    if unidade == "semanas":
        return f"{(media_dias / 7):.2f} semanas"
    return f"{(media_dias / 30):.2f} meses"


def _formatar_throughput(data_conclusoes, periodo: str) -> str:
    if not data_conclusoes:
        return "Sem dados"

    ordenadas = sorted(data_conclusoes)
    dias_janela = max((ordenadas[-1] - ordenadas[0]).days + 1, 1)
    total = len(ordenadas)

    if periodo == "diario":
        valor = total / dias_janela
        return f"{valor:.2f} cards/dia"
    if periodo == "semanal":
        valor = total / (dias_janela / 7)
        return f"{valor:.2f} cards/semana"
    valor = total / (dias_janela / 30)
    return f"{valor:.2f} cards/mês"


def _render_metricas_section(quadro, columns, cards) -> None:
    st.subheader("Métricas")
    st.caption("Acesse aqui as métricas do quadro.")

    cycle_dias = []
    lead_dias = []
    conclusoes = []
    for card in cards:
        if card.data_conclusao:
            conclusoes.append(card.data_conclusao.date())
        if card.data_inicio and card.data_conclusao and card.data_conclusao >= card.data_inicio:
            diff = card.data_conclusao - card.data_inicio
            cycle_dias.append(diff.total_seconds() / 86400)
        if card.data_criacao and card.data_conclusao and card.data_conclusao >= card.data_criacao:
            diff = card.data_conclusao - card.data_criacao
            lead_dias.append(diff.total_seconds() / 86400)

    media_cycle = _media_duracao_dias(cycle_dias)
    media_lead = _media_duracao_dias(lead_dias)

    coluna_fazendo_id = next((col_id for col_id, nome in columns if nome == "FAZENDO"), None)
    wip_real = 0
    if coluna_fazendo_id is not None:
        wip_real = sum(1 for card in cards if card.coluna_id == coluna_fazendo_id)

    row1 = st.columns([2.4, 1.4, 2.2])
    row1[0].write("- Cycle time médio")
    unidade_cycle = row1[1].selectbox(
        "Unidade cycle",
        options=["dias", "semanas", "meses"],
        label_visibility="collapsed",
        key=f"metric_cycle_unit_{quadro.id}",
    )
    row1[2].write(_formatar_duracao(media_cycle, unidade_cycle))

    row2 = st.columns([2.4, 1.4, 2.2])
    row2[0].write("- Lead time médio")
    unidade_lead = row2[1].selectbox(
        "Unidade lead",
        options=["dias", "semanas", "meses"],
        label_visibility="collapsed",
        key=f"metric_lead_unit_{quadro.id}",
    )
    row2[2].write(_formatar_duracao(media_lead, unidade_lead))

    row3 = st.columns([2.4, 1.4, 2.2])
    row3[0].write("- Throughput")
    unidade_throughput = row3[1].selectbox(
        "Unidade throughput",
        options=["diario", "semanal", "mensal"],
        label_visibility="collapsed",
        key=f"metric_throughput_unit_{quadro.id}",
    )
    row3[2].write(_formatar_throughput(conclusoes, unidade_throughput))

    row4 = st.columns([2.4, 1.4, 2.2])
    row4[0].write("- WIP máximo")
    row4[1].write("")
    row4[2].write(str(quadro.wip))

    row5 = st.columns([2.4, 1.4, 2.2])
    row5[0].write("- WIP real")
    row5[1].write("")
    row5[2].write(str(wip_real))


def _render_quadro_detalhe(
    projeto,
    quadro,
    user_id: int,
    project_id: int,
    board_id: int,
    boards,
    board_controller: BoardController,
    lane_controller: LaneController,
    card_controller: CardController,
) -> None:
    lane_controller.garantir_raia_principal(board_id=board_id)

    lanes = lane_controller.listar_raias(user_id=user_id, project_id=project_id, board_id=board_id)
    columns = card_controller.listar_colunas_do_quadro(
        user_id=user_id,
        project_id=project_id,
        board_id=board_id,
    )
    cards = card_controller.listar_cards(user_id=user_id, project_id=project_id, board_id=board_id)

    st.title(quadro.nome)
    st.markdown(
        f"<p style='font-size:0.9rem;color:#7a7a7a;margin-top:-10px;'>Projeto: {projeto.nome}</p>",
        unsafe_allow_html=True,
    )

    if st.button(
        ":material/arrow_back: Voltar para quadros",
        use_container_width=False,
        key="btn_voltar_lista_quadros",
        type="secondary",
    ):
        st.session_state["quadro_selecionado_id"] = None
        st.rerun()

    st.markdown("---")
    _render_kanban_section(lanes=lanes, columns=columns, cards=cards)

    st.markdown("---")
    _render_lanes_commands_section(
        lane_controller=lane_controller,
        user_id=user_id,
        project_id=project_id,
        board_id=board_id,
        lanes=lanes,
    )

    st.markdown("---")
    _render_cards_commands_section(
        card_controller=card_controller,
        user_id=user_id,
        project_id=project_id,
        board_id=board_id,
        cards=cards,
        lanes=lanes,
        columns=columns,
    )

    st.markdown("---")
    _render_metricas_section(quadro=quadro, columns=columns, cards=cards)

    colunas_map = {col_name: col_id for col_id, col_name in columns}
    a_fazer_coluna_id = colunas_map.get("A_FAZER")
    principal_lane = next((lane for lane in lanes if lane.nome.strip().lower() == "principal"), None)

    if st.session_state.get("abrir_popup_novo_quadro"):
        _dialog_novo_quadro(board_controller=board_controller, user_id=user_id, project_id=project_id)
    elif st.session_state.get("abrir_popup_alterar_quadro"):
        _dialog_alterar_quadro(
            board_controller=board_controller,
            user_id=user_id,
            project_id=project_id,
            boards=boards,
        )
    elif st.session_state.get("abrir_popup_excluir_quadro"):
        _dialog_excluir_quadro(
            board_controller=board_controller,
            user_id=user_id,
            project_id=project_id,
            boards=boards,
        )
    elif st.session_state.get("abrir_popup_criar_raia"):
        _dialog_criar_raia(lane_controller, user_id, project_id, board_id)
    elif st.session_state.get("abrir_popup_atualizar_raia"):
        _dialog_atualizar_raia(lane_controller, user_id, project_id, board_id, lanes)
    elif st.session_state.get("abrir_popup_excluir_raia"):
        _dialog_excluir_raia(lane_controller, user_id, project_id, board_id, lanes)
    elif st.session_state.get("abrir_popup_ler_raias"):
        _dialog_ler_raias(lanes)
    elif st.session_state.get("abrir_popup_criar_card"):
        if not principal_lane or not a_fazer_coluna_id:
            _fechar_todos_dialogos()
            st.session_state["flash_quadro_erro"] = (
                "Não foi possível encontrar a raia Principal ou a coluna A_FAZER."
            )
            st.rerun()
        _dialog_criar_card(
            card_controller=card_controller,
            user_id=user_id,
            project_id=project_id,
            board_id=board_id,
            principal_lane_id=int(principal_lane.id),
            a_fazer_coluna_id=int(a_fazer_coluna_id),
        )
    elif st.session_state.get("abrir_popup_atualizar_card"):
        _dialog_atualizar_card(card_controller, user_id, project_id, board_id, cards)
    elif st.session_state.get("abrir_popup_excluir_card"):
        _dialog_excluir_card(card_controller, user_id, project_id, board_id, cards)
    elif st.session_state.get("abrir_popup_mover_card"):
        _dialog_mover_card(card_controller, user_id, project_id, board_id, cards, lanes)
    elif st.session_state.get("abrir_popup_ler_card"):
        _dialog_ler_card(cards)


def render_board_page(
    project_controller: ProjectController,
    board_controller: BoardController,
    lane_controller: LaneController,
    card_controller: CardController,
) -> None:
    _init_state()

    usuario = st.session_state.get("usuario_logado")
    if not usuario:
        st.session_state["current_page"] = "login_page"
        st.rerun()
        return

    projeto_id = st.session_state.get("projeto_selecionado_id")
    if not projeto_id:
        st.title("Meus quadros")
        st.info("Selecione um projeto em 'Meus projetos' para ver os quadros.")
        return

    projeto = project_controller.obter_projeto_do_usuario(
        user_id=usuario.id,
        project_id=int(projeto_id),
    )
    if not projeto:
        st.session_state["projeto_selecionado_id"] = None
        st.title("Meus quadros")
        st.error("Projeto não encontrado para este usuário.")
        return

    boards = board_controller.listar_quadros(user_id=usuario.id, project_id=int(projeto.id))

    _mostrar_feedback()

    selected_board_id = st.session_state.get("quadro_selecionado_id")
    if selected_board_id:
        quadro = board_controller.obter_quadro(
            user_id=usuario.id,
            project_id=int(projeto.id),
            board_id=int(selected_board_id),
        )
        if not quadro:
            st.session_state["quadro_selecionado_id"] = None
            st.error("Quadro selecionado não foi encontrado.")
            st.rerun()
            return

        _render_quadro_detalhe(
            projeto=projeto,
            quadro=quadro,
            user_id=usuario.id,
            project_id=int(projeto.id),
            board_id=int(quadro.id),
            boards=boards,
            board_controller=board_controller,
            lane_controller=lane_controller,
            card_controller=card_controller,
        )
        return

    st.title(projeto.nome)
    if st.button(
        ":material/arrow_back: Voltar",
        key="btn_voltar_para_projetos",
        use_container_width=False,
        type="secondary",
    ):
        st.session_state["quadro_selecionado_id"] = None
        st.session_state["current_page"] = "project_page"
        st.rerun()

    st.markdown("---")
    st.subheader("Quadros - Comandos")
    col_novo, col_alterar, col_excluir = st.columns(3)
    if col_novo.button(
        ":material/add: Novo quadro",
        use_container_width=True,
        key="btn_lista_novo_quadro",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_novo_quadro")
        st.rerun()
    if col_alterar.button(
        ":material/edit: Alterar quadro",
        use_container_width=True,
        key="btn_lista_alterar_quadro",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_alterar_quadro")
        _resetar_fluxo_alteracao()
        st.rerun()
    if col_excluir.button(
        ":material/delete: Excluir quadro",
        use_container_width=True,
        key="btn_lista_excluir_quadro",
        type="secondary",
    ):
        _abrir_dialogo("abrir_popup_excluir_quadro")
        st.rerun()

    st.markdown("---")
    st.subheader("Quadros no projeto")
    _render_lista_quadros(boards=boards)

    st.markdown("---")
    _render_integrantes_section(
        project_controller=project_controller,
        user_id=usuario.id,
        project_id=int(projeto.id),
    )

    if st.session_state.get("abrir_popup_novo_quadro"):
        _dialog_novo_quadro(
            board_controller=board_controller,
            user_id=usuario.id,
            project_id=int(projeto.id),
        )
    elif st.session_state.get("abrir_popup_alterar_quadro"):
        _dialog_alterar_quadro(
            board_controller=board_controller,
            user_id=usuario.id,
            project_id=int(projeto.id),
            boards=boards,
        )
    elif st.session_state.get("abrir_popup_excluir_quadro"):
        _dialog_excluir_quadro(
            board_controller=board_controller,
            user_id=usuario.id,
            project_id=int(projeto.id),
            boards=boards,
        )
    elif st.session_state.get("abrir_popup_convidar_pessoas"):
        _dialog_convidar_pessoas(
            project_controller=project_controller,
            user_id=usuario.id,
            project_id=int(projeto.id),
        )

