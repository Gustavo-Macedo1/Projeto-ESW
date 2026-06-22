import streamlit as st

from controllers.project_controller import ProjectController


DIALOG_FLAGS = ["abrir_popup_criar_projeto", "abrir_popup_excluir_projeto"]


def _init_state() -> None:
    defaults = {
        "abrir_popup_criar_projeto": False,
        "abrir_popup_excluir_projeto": False,
        "flash_projeto_sucesso": None,
        "flash_projeto_erro": None,
        "projeto_selecionado_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _fechar_dialogos() -> None:
    for flag in DIALOG_FLAGS:
        st.session_state[flag] = False


def _abrir_dialogo(flag: str) -> None:
    _fechar_dialogos()
    st.session_state[flag] = True


def _dialog_criar_projeto(project_controller: ProjectController, user_id: int) -> None:
    @st.dialog("Criar projeto")
    def _criar():
        total_projetos = len(project_controller.listar_projetos_do_usuario(user_id=user_id))
        if total_projetos >= ProjectController.MAX_PROJECTS_PER_USER:
            st.error("Limite de 6 projetos atingido.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_criar_limite",
                type="secondary",
            ):
                _fechar_dialogos()
                st.rerun()
            return

        with st.form("form_criar_projeto"):
            nome_projeto = st.text_input("Nome do projeto")
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
            _fechar_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = project_controller.criar_projeto(
                user_id=user_id,
                nome=nome_projeto,
            )
            if sucesso:
                _fechar_dialogos()
                st.session_state["flash_projeto_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _criar()


def _dialog_excluir_projeto(project_controller: ProjectController, user_id: int, projects) -> None:
    @st.dialog("Excluir projeto")
    def _excluir():
        if not projects:
            st.info("Você não participa de nenhum projeto.")
            if st.button(
                "Fechar",
                use_container_width=True,
                key="fechar_popup_excluir_projeto_vazio",
                type="secondary",
            ):
                _fechar_dialogos()
                st.rerun()
            return

        projects_map = {projeto.id: projeto.nome for projeto in projects}

        with st.form("form_excluir_projeto"):
            st.write("Selecione o projeto que deseja excluir.")
            selected_project_id = st.selectbox(
                "Projeto",
                options=list(projects_map.keys()),
                format_func=lambda item: projects_map[item],
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
            _fechar_dialogos()
            st.rerun()

        if confirmar:
            sucesso, mensagem = project_controller.excluir_projeto(
                user_id=user_id,
                project_id=int(selected_project_id),
            )
            if sucesso:
                _fechar_dialogos()
                st.session_state["flash_projeto_sucesso"] = mensagem
                st.rerun()
            st.error(mensagem)

    _excluir()


def render_project_page(project_controller: ProjectController) -> None:
    _init_state()

    usuario = st.session_state.get("usuario_logado")
    if not usuario:
        st.session_state["current_page"] = "login_page"
        st.rerun()
        return

    projects = project_controller.listar_projetos_do_usuario(user_id=usuario.id)

    if st.session_state.get("abrir_popup_criar_projeto"):
        _dialog_criar_projeto(project_controller=project_controller, user_id=usuario.id)
    elif st.session_state.get("abrir_popup_excluir_projeto"):
        _dialog_excluir_projeto(
            project_controller=project_controller,
            user_id=usuario.id,
            projects=projects,
        )

    if st.session_state.get("flash_projeto_sucesso"):
        st.success(st.session_state["flash_projeto_sucesso"])
        st.session_state["flash_projeto_sucesso"] = None

    if st.session_state.get("flash_projeto_erro"):
        st.error(st.session_state["flash_projeto_erro"])
        st.session_state["flash_projeto_erro"] = None

    st.title("Meus projetos")
    st.write("Selecione um projeto para começar")

    col_criar, col_excluir = st.columns(2)
    clicou_criar = col_criar.button(
        ":material/add: Criar projeto",
        use_container_width=True,
        key="btn_criar_projeto",
        type="secondary",
    )
    clicou_excluir = col_excluir.button(
        ":material/delete: Excluir projeto",
        use_container_width=True,
        key="btn_excluir_projeto",
        type="secondary",
    )

    if clicou_criar:
        _abrir_dialogo("abrir_popup_criar_projeto")
        st.rerun()

    if clicou_excluir:
        _abrir_dialogo("abrir_popup_excluir_projeto")
        st.rerun()

    st.markdown("---")
    if not projects:
        st.info("Nenhum projeto encontrado. Clique em 'Criar projeto' para começar.")
        return

    st.caption("Máximo de 6 projetos por usuário.")
    grid_cols = st.columns(3)
    for idx, projeto in enumerate(projects):
        label = f"**{projeto.nome}**  \n{projeto.total_quadros} quadro(s)"
        col = grid_cols[idx % 3]
        clicou_projeto = col.button(
            label,
            key=f"projeto_btn_{projeto.id}",
            use_container_width=True,
            type="secondary",
        )
        if clicou_projeto:
            st.session_state["projeto_selecionado_id"] = projeto.id
            st.session_state["quadro_selecionado_id"] = None
            st.session_state["current_page"] = "board_page"
            st.rerun()

