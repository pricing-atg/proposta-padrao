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
    variavel_restricao = carregar_variavel_tipo_categoria_veiculo()
    base_regiao = carregar_base_regiao()
    variavel_ano_modelo = carregar_variavel_ano_modelo()
    variavel_valor = carregar_variavel_valor()
    
    # Filtros para selecionar o período de referência e os tipos de veículos
    with st.container():
        coluna01, coluna02, coluna03 = st.columns(3)        

        with coluna01:
            # Filtro com select_slider usando datas
            data_inicio, data_fim = st.select_slider(
                "Período de Referência",
                options=variavel_periodo_referencia,
                value=(variavel_periodo_referencia[0], variavel_periodo_referencia[-1]),  # Default: início ao fim
                format_func=lambda x: x.strftime("%b/%Y")  # Exemplo de formatação: Jan/2024
            )
            
        with coluna02:
            tipo_veiculo_selecionado = st.multiselect(
                "Tipo de Veículo",
                options=sorted(variavel_tipo_veiculo),
                default=sorted(variavel_tipo_veiculo),  # Todos selecionados como padrão
                placeholder="Selecione os tipos de veículo"
            )
            
        with coluna03:
            tipo_veiculo_restricao = st.multiselect(
                "Categorias de Restrição",
                options=sorted(variavel_restricao),
                default=None,
                placeholder="Selecione as Restrições dos Veículos"
            )
    
    # Filtros para selecionar as regiões a serem consideradas
    with st.container():
        coluna01, coluna02 = st.columns(2)

        # Valor a ser excluído dos filtros (mas não dos dados finais)
        valor_excluido = "UF_NULL"

        # Remove valores inválidos apenas para os filtros
        base_filtrada = base_regiao[
            (base_regiao["UF"] != valor_excluido) &
            (base_regiao["REGIAO"] != valor_excluido)
        ]

        with coluna01:
            # Cria opções de regiões com "BRASIL" + únicas da base filtrada
            regioes_disponiveis = ['BRASIL'] + sorted(base_filtrada["REGIAO"].dropna().unique())
            regiao_selecionada = st.multiselect(
                "Região", 
                options=regioes_disponiveis,
                placeholder="Selecione as Regiões"
                )

        with coluna02:
            # Define as UFs disponíveis conforme a seleção da região
            if 'BRASIL' in regiao_selecionada or not regiao_selecionada:
                ufs_disponiveis = sorted(base_filtrada["UF"].dropna().unique())
            else:
                ufs_disponiveis = sorted(
                    base_filtrada[base_filtrada["REGIAO"].isin(regiao_selecionada)]["UF"].dropna().unique()
                )

            # Adiciona a opção "TODAS"
            ufs_opcoes = ['TODAS'] + ufs_disponiveis

            # Multiselect de UFs
            ufs_selecionadas = st.multiselect(
                "UFs",
                options=ufs_opcoes,
                default=ufs_disponiveis,
                placeholder="Selecione as UFs"
            )

            # Se "TODAS" for selecionado, considera todas as UFs da base original (com ou sem UF_NULL)
            if 'TODAS' in ufs_selecionadas:
                regiao_selecionada = ['BRASIL']
                ufs_selecionadas = sorted(base_regiao["UF"].dropna().unique())

            # Garante que o valor_excluido esteja presente para preservar os dados finais
            ufs_selecionadas.append(valor_excluido)

    
    # Filtros para selecionar a idade dos veículos e os valores
    with st.container():
        coluna01, coluna02 = st.columns(2)

        with coluna01:
            
            variavel_ano_modelo = sorted(variavel_ano_modelo)

            ano_modelo_min, ano_modelo_max = st.select_slider(
                "Ano do Modelo",
                options=variavel_ano_modelo,
                value=(variavel_ano_modelo[0], variavel_ano_modelo[-1])
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
            
    with st.container():
        coluna01, coluna02 = st.columns(2)

        with coluna01:
            # Upload do arquivo com as montadoras famílias
            arquivo_mf = st.file_uploader("Importar arquivo com Montadoras Famílias (Excel ou .txt)", type=["xlsx", "xls", "txt"])
            

        with coluna02:
            # Campo para colar os valores manualmente
            texto_colado = st.text_area("Ou cole as Montadoras Famílias abaixo (uma por linha):", height=150)
    

    # Lista final para filtrar
    lista_mf_filtrar = []
    
    # Se um arquivo foi enviado
    if arquivo_mf is not None:
        try:
            if arquivo_mf.name.endswith(".txt"):
                conteudo = arquivo_mf.read().decode("utf-8")
                lista_mf_filtrar = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]
            elif arquivo_mf.name.endswith((".xlsx", ".xls")):
                df_arquivo = pd.read_excel(arquivo_mf)
                primeira_coluna = df_arquivo.columns[0]
                lista_mf_filtrar = df_arquivo[primeira_coluna].dropna().astype(str).tolist()
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

    # Se o usuário colou manualmente
    if texto_colado:
        colados = [linha.strip() for linha in texto_colado.splitlines() if linha.strip()]
        lista_mf_filtrar.extend(colados)

    # Remover duplicados
    lista_mf_filtrar = list(set(lista_mf_filtrar))
    
    return data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, lista_mf_filtrar
