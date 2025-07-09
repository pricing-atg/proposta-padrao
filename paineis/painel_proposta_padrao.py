from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import duckdb
import os

# Importações específicas do projeto
from authentication.login import login_user
from paineis.app_show_filtro_cliente import *
from paineis.funcao_parametros import *
from paineis.funcao_ajuste_bases import *
from paineis.funcao_validacao_freq_cms import *
from paineis.funcao_proposta import *

# Função principal da aplicação
def show_painel_proposta_padrao():
    st.title("Painel de Elaboração da Proposta Padrão")  # Título principal
    
    st.markdown("### 🔎 Filtros")
    
    # Filtros - Ajustado
    tipo_coberturas = show_app_filtro_coberturas()
    
    data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, lista_mf_filtrar = show_app_filtro_cliente()
    
    st.divider()
    
    st.subheader(" ⚙️ Parâmetros de Precificação")
    parametros = show_parametrizacao(tipo_veiculo_selecionado, tipo_coberturas)
            
    # Inicializa os estados da aplicação
    if 'bases_calculadas' not in st.session_state:
        st.session_state.bases_calculadas = False

    # Botão de aplicar filtros
    if st.button("Aplicar filtros"):
        st.session_state.base_receita = show_resumo_base_receita(
            tipo_coberturas,
            data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, 
            ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, 
            lista_mf_filtrar, parametros
        )
        st.session_state.base_despesa = show_resumo_base_despesa(
            tipo_coberturas,
            data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, 
            ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, 
            lista_mf_filtrar, parametros
        )
        st.session_state.parametros = parametros
        st.session_state.bases_calculadas = True
    
    if st.session_state.bases_calculadas:
        st.divider()
        st.markdown("## 📊 Resumo CMS e Frequência - Por Seguradora e Mês de Referência")
        # Se as bases já foram calculadas, atualiza a base de validação
        base_resumo_geral = show_validacao_freq_cms(
            tipo_coberturas,
            st.session_state.base_receita,
            st.session_state.base_despesa,
            st.session_state.parametros
        )
        
        st.session_state.base_resumo_geral = base_resumo_geral
    
    # Exibe os resultados se as bases estiverem prontas
    if st.session_state.bases_calculadas:
        st.markdown("## 💲 Elaboração do Preço")
        
        tipo_precificacao = st.radio(
            "Tipo de Precificação",
            ["Ponto Frequência", "Item Exposto"],
            index=None,
        )

        if tipo_precificacao == "Ponto Frequência":
            show_proposta_ponto_frequencia(
                st.session_state.base_resumo_geral,
                st.session_state.parametros,
                tipo_precificacao
            )

        elif tipo_precificacao == "Item Exposto":
            show_proposta_item_exposto(
                st.session_state.base_resumo_geral,
                st.session_state.parametros,
                tipo_precificacao
            )
