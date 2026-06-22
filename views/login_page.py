import time

import streamlit as st

from controllers.auth_controller import AuthController


def _abrir_popup_sucesso() -> None:
    mensagem = "Login realizado com sucesso. Redirecionando..."
    if hasattr(st, "dialog"):
        @st.dialog("Seeban")
        def _popup():
            st.write(mensagem)

        _popup()
    else:
        st.success(mensagem)


def _css_login() -> None:
    st.markdown(
        """
        <style>
            .seeban-title {
                text-align: center;
                font-size: 72px;
                font-weight: 800;
                letter-spacing: 1px;
                margin-top: 24px;
                margin-bottom: 18px;
            }
            .login-card {
                border: 1px solid #E7E7E7;
                border-radius: 14px;
                padding: 20px 22px 12px 22px;
                box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
                background: #FFFFFF;
            }
            .stTextInput > div > div > input {
                border-radius: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_page(auth_controller: AuthController) -> None:
    if "mostrar_cadastro_popup" not in st.session_state:
        st.session_state["mostrar_cadastro_popup"] = False
    if "flash_sucesso" not in st.session_state:
        st.session_state["flash_sucesso"] = None

    if st.session_state.get("popup_sucesso"):
        _abrir_popup_sucesso()
        time.sleep(1.4)
        st.session_state["popup_sucesso"] = False
        st.session_state["current_page"] = st.session_state.get(
            "redirecionar_para",
            "project_page",
        )
        st.rerun()

    if st.session_state.get("flash_sucesso"):
        st.success(st.session_state["flash_sucesso"])
        st.session_state["flash_sucesso"] = None

    if st.session_state.get("mostrar_cadastro_popup"):
        @st.dialog("Cadastrar")
        def _cadastro_dialog():
            with st.form("form_cadastro"):
                cadastro_usuario = st.text_input("Usuário", key="cadastro_usuario")
                cadastro_senha = st.text_input(
                    "Senha",
                    type="password",
                    key="cadastro_senha",
                )
                cadastro_confirma_senha = st.text_input(
                    "Confirmar senha",
                    type="password",
                    key="cadastro_confirma_senha",
                )
                col_criar, col_cancelar = st.columns(2)
                clicou_criar = col_criar.form_submit_button(
                    ":material/add: Criar conta",
                    use_container_width=True,
                    type="secondary",
                )
                clicou_cancelar = col_cancelar.form_submit_button(
                    "Cancelar",
                    use_container_width=True,
                    type="secondary",
                )

            if clicou_cancelar:
                st.session_state["mostrar_cadastro_popup"] = False
                st.rerun()

            if clicou_criar:
                sucesso, mensagem = auth_controller.cadastrar(
                    username=cadastro_usuario,
                    senha=cadastro_senha,
                    confirma_senha=cadastro_confirma_senha,
                )
                if sucesso:
                    st.session_state["mostrar_cadastro_popup"] = False
                    st.session_state["flash_sucesso"] = mensagem
                    st.rerun()
                st.error(mensagem)

        _cadastro_dialog()

    _css_login()
    st.markdown('<div class="seeban-title">Seeban</div>', unsafe_allow_html=True)

    _, center, _ = st.columns([1.2, 1.6, 1.2])
    with center:
        st.subheader("Bem-vindo(a) ao Seeban!")

        with st.form("form_login"):
            username = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            col_login, col_cadastro = st.columns(2)
            clicou_login = col_login.form_submit_button(
                "Login",
                use_container_width=True,
                type="secondary",
            )
            clicou_cadastro = col_cadastro.form_submit_button(
                ":material/add: Cadastrar",
                use_container_width=True,
                type="secondary",
            )

    if clicou_cadastro:
        st.session_state["mostrar_cadastro_popup"] = True
        st.rerun()

    if clicou_login:
        autenticado, usuario = auth_controller.autenticar(username=username.strip(), senha=senha)
        if autenticado:
            st.session_state["usuario_logado"] = usuario
            st.session_state["popup_sucesso"] = True
            st.session_state["redirecionar_para"] = "project_page"
            st.rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")

