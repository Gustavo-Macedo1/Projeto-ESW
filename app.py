import streamlit as st

from controllers.auth_controller import AuthController
from controllers.board_controller import BoardController
from controllers.card_controller import CardController
from controllers.lane_controller import LaneController
from controllers.project_controller import ProjectController
from views.board_page import render_board_page
from views.login_page import render_login_page
from views.project_page import render_project_page


def _init_session_state() -> None:
    defaults = {
        "current_page": "login_page",
        "usuario_logado": None,
        "popup_sucesso": False,
        "redirecionar_para": "project_page",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _fazer_logoff() -> None:
    st.session_state["usuario_logado"] = None
    st.session_state["current_page"] = "login_page"
    st.session_state["projeto_selecionado_id"] = None
    st.rerun()


def _render_sidebar_menu() -> None:
    with st.sidebar:
        st.subheader("Menu")
        if st.button(
            "Meus projetos",
            use_container_width=True,
            key="sidebar_meus_projetos",
            type="primary",
        ):
            st.session_state["current_page"] = "project_page"
            st.session_state["quadro_selecionado_id"] = None
            st.rerun()
        if st.button(
            "Meus quadros",
            use_container_width=True,
            key="sidebar_meus_quadros",
            type="primary",
        ):
            st.session_state["current_page"] = "board_page"
            st.session_state["quadro_selecionado_id"] = None
            st.rerun()

        st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
        if st.button(
            "Logoff",
            use_container_width=True,
            key="sidebar_logoff",
            type="primary",
        ):
            _fazer_logoff()


def main() -> None:
    st.set_page_config(page_title="Seeban", page_icon=":clipboard:")
    _init_session_state()

    auth_controller = AuthController()
    board_controller = BoardController()
    lane_controller = LaneController()
    card_controller = CardController()
    project_controller = ProjectController()
    page = st.session_state.get("current_page", "login_page")
    usuario_logado = st.session_state.get("usuario_logado")

    if page != "login_page" and not usuario_logado:
        st.session_state["current_page"] = "login_page"
        st.rerun()
        return

    if usuario_logado and page != "login_page":
        _render_sidebar_menu()

    if page == "login_page":
        render_login_page(auth_controller)
    elif page == "project_page":
        render_project_page(project_controller)
    elif page == "board_page":
        render_board_page(project_controller, board_controller, lane_controller, card_controller)
    else:
        st.session_state["current_page"] = "login_page"
        st.rerun()


if __name__ == "__main__":
    main()
