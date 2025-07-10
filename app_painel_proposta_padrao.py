from PIL import Image
import streamlit as st
from authentication.login import login_user
from paineis.painel_proposta_padrao import *

# Configuração da página
st.set_page_config(
    page_title="Proposta Padrão",
    layout="wide",
    page_icon=Image.open("img/favicon.ico"),
)

# Autenticação
authenticator = login_user()
auth_status = st.session_state.get("authentication_status", None)

def mostrar_logo_e_login():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("img/logo-autoglass-maxpar-1.png", use_container_width=True)
    st.markdown(
        "<h3 style='text-align: center; margin-top: 10px;'>Painel de Proposta Padrão</h3>",
        unsafe_allow_html=True,
    )
    authenticator.login(
        location='main',
        fields={
            "Form name": "Acesso ao Sistema",
            "Username": "Usuário",
            "Password": "Senha"
        }
    )

if auth_status is None:
    mostrar_logo_e_login()

elif auth_status is False:
    st.error("Usuário ou senha incorretos.")
    mostrar_logo_e_login()

else:
    # Boas-vindas e botão de logout
    col1, col2 = st.columns([9, 1])
    with col1:
        st.write(f'Seja bem-vindo(a), membro da equipe de {st.session_state["name"]}!')
    with col2:
        authenticator.logout(location='main')

    # Permissão por tipo de usuário
    usuarios_autorizados = {
        "produtos": "produtos",
        "pricing": "pricing"
    }

    usuario_tipo = st.session_state.get("email")

    if usuario_tipo in usuarios_autorizados.values():
        show_painel_proposta_padrao()
    else:
        st.warning("Acesso restrito. Usuário não autorizado ou sessão inválida.")