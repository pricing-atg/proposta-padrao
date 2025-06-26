import streamlit as st
import pandas as pd
import duckdb
import numpy as np

from datetime import datetime

from paineis.filtros.filtro_visao_cliente import *
from paineis.funcao_validacao_freq_cms import *

def show_app_filtro_coberturas():
    
    with st.container():
        tipo_coberturas = st.multiselect(
            "Coberturas",
            options=["Vidros", "FLR", "Higienização", "Cristalização", "Martelinho", "SRA", "RLP", "RPS", "Pneu", "ADAS", "Polimento de Farol", "Reparo de Parabrisa","RLPP","Troca - PC","Reparo - PC"],
            default=["Vidros", "FLR", "Higienização", "Cristalização", "Martelinho", "SRA", "RLP", "RPS", "Pneu", "ADAS", "Polimento de Farol", "Reparo de Parabrisa","RLPP","Troca - PC","Reparo - PC"],
            placeholder="Selecione os tipos de coberturas"  
        )
        
    return tipo_coberturas


def show_app_filtro_cliente():
    
    variavel_periodo_referencia = carregar_variavel_periodo_referencia()
    variavel_tipo_veiculo = carregar_variavel_tipo_veiculo()
    base_regiao = carregar_base_regiao()
    variavel_ano_modelo = carregar_variavel_ano_modelo()
    variavel_valor = carregar_variavel_valor()
    
    # Filtros para selecionar o período de referência e os tipos de veículos
    with st.container():
        coluna01, coluna02 = st.columns(2)        

        with coluna01:
            # Filtro com select_slider usando datas
            data_inicio, data_fim = st.select_slider(
                "Período de Referência",
                options=variavel_periodo_referencia,
                value=(variavel_periodo_referencia[0], variavel_periodo_referencia[-1]),  # Default: início ao fim
                format_func=lambda x: x.strftime("%b/%Y")  # Exemplo de formatação: Jan/2024
            )
            
        with coluna02:
            tipos_veiculos_selecionados = st.multiselect(
                "Tipo de Veículo",
                options=sorted(variavel_tipo_veiculo),
                default=sorted(variavel_tipo_veiculo),  # Todos selecionados como padrão
                placeholder="Selecione os tipos de veículo"
            )
    
    # Filtros para selecionar as regiões a serem consideradas
    with st.container():
        coluna01, coluna02 = st.columns(2)

        # Define o valor a ser excluído dos filtros (mas não dos dados finais)
        valor_excluido = "UF_NULL"

        # Remove 'UF_NULL' da base para os filtros, mas não altera a base original
        base_filtrada = base_regiao[
            (base_regiao["UF"] != valor_excluido) &
            (base_regiao["REGIAO"] != valor_excluido)
        ]

        with coluna01:
            # Cria opções de regiões com 'BRASIL' + regiões únicas (sem UF_NULL)
            regioes_disponiveis = ['BRASIL'] + sorted(base_filtrada["REGIAO"].dropna().unique())
            regiao_selecionada = st.selectbox("Região", options=regioes_disponiveis)

        with coluna02:
            if regiao_selecionada == 'BRASIL':
                ufs_disponiveis = sorted(base_filtrada["UF"].dropna().unique())
            else:
                ufs_disponiveis = sorted(
                    base_filtrada[base_filtrada["REGIAO"] == regiao_selecionada]["UF"].dropna().unique()
                )

            # Adiciona a opção 'TODAS' no início da lista
            ufs_opcoes = ['TODAS'] + ufs_disponiveis

            ufs_selecionadas = st.multiselect(
                "UFs",
                options=ufs_opcoes,
                default=ufs_disponiveis,
                placeholder="Selecione as UFs"
            )

            # Lógica para "TODAS"
            if 'TODAS' in ufs_selecionadas:
                regiao_selecionada = 'BRASIL'
                # Aqui usamos a base original para incluir até mesmo o UF_NULL se estiver presente
                ufs_selecionadas = sorted(base_regiao["UF"].dropna().unique())
            
            ufs_selecionadas.append(valor_excluido)

    
    # Filtros para selecionar a idade dos veículos e os valores
    with st.container():
        coluna01, coluna02 = st.columns(2)

        with coluna01:
            ano_atual = datetime.now().year
            anos_disponiveis = sorted(variavel_ano_modelo)
            anos_filtrados = [ano for ano in anos_disponiveis if ano >= ano_atual - 30]

            ano_modelo_min, ano_modelo_max = st.select_slider(
                "Ano do Modelo",
                options=anos_filtrados,
                value=(anos_filtrados[0], anos_filtrados[-1])
            )

        with coluna02:
            valores_disponiveis = sorted(variavel_valor)
            valor_max = int(max(valores_disponiveis)) if len(valores_disponiveis) > 0 else 50000
            valores_intervalados = list(range(0, valor_max + 50000, 50000))

            valor_min, valor_max = st.select_slider(
                "Valor do Veículo",
                options=valores_intervalados,
                value=(valores_intervalados[0], valores_intervalados[-1]),
                format_func=lambda x: f"R$ {x:,.0f}".replace(",", ".")
            )
    
    return data_inicio, data_fim, tipos_veiculos_selecionados, ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max
