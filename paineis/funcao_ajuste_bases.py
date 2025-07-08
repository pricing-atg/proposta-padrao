import streamlit as st
import pandas as pd
import duckdb
import numpy as np

from datetime import datetime

def show_resumo_base_receita(
    tipo_coberturas,
    data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, 
    ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, 
    lista_mf_filtrar, parametros):

    caminho_base_itens = 'data/base_itens_parte_*.parquet'
    con = duckdb.connect(database=':memory:')

    # 🔁 Mapeamento conforme a imagem
    mapeamento_coberturas = {
        "Vidros": ["VIDROS"],
        "FLR": ["FLR"],
        "Higienização": ["VIDROS"],
        "Cristalização": ["VIDROS"],
        "Martelinho": ["MARTELINHO"],
        "SRA": ["SRA"],
        "RLP": ["RLP"],
        "RPS": ["RPS"],
        "Pneu": ["PNEU"],
        "ADAS": ["VIDROS"],
        "Polimento de Farol": ["FLR"],
        "Reparo de Parabrisa": ["VIDROS"],
        "RLPP": ["RLPP", "RLP", "TROCA_DE_PARACHOQUE"],
        "Troca - PC": ["TROCA_DE_PARACHOQUE", "PARACHOQUE"],
        "Reparo - PC": ["TROCA_DE_PARACHOQUE", "PARACHOQUE"]
    }

    # 🔍 Determina colunas de cobertura com base nas coberturas selecionadas
    colunas_cobertura = set()
    for cobertura in tipo_coberturas:
        colunas_cobertura.update(mapeamento_coberturas.get(cobertura, []))
    colunas_cobertura = sorted(colunas_cobertura)

    # 🔧 Colunas fixas + dinâmicas
    colunas_fixas = [
        "DAT_REFERENCIA_MODIF",
        "SEGURADORA",
        "MF_VEICULO",
        "VEICULO_ADAS",
        "TIPO_VEICULO"
    ]
    colunas_selecionadas = colunas_fixas + colunas_cobertura

    colunas_select = ",\n            ".join(colunas_selecionadas)
    colunas_group = ",\n            ".join(colunas_selecionadas)

    # 🧩 Filtros adicionais
    tipos_veiculos_str = ", ".join(f"'{tipo}'" for tipo in tipo_veiculo_selecionado)
    ufs_str = ", ".join(f"'{uf}'" for uf in ufs_selecionadas)

    filtros_restricao = []
    if "Blindados" in tipo_veiculo_restricao:
        filtros_restricao.append("BLINDADOS = 'Não'")
    if "Cabrio" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_CABRIO_CONVENCIONAL != 'Cabrio'")
    if "Convencional" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_CABRIO_CONVENCIONAL != 'Convencional'")
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Convencional'")
    if "Elétrico" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Elétrico'")
    if "Híbrido" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Híbrido'")
    if lista_mf_filtrar:
        lista_mf_str = ", ".join(f"'{mf}'" for mf in lista_mf_filtrar)
        filtros_restricao.append(f"MF_VEICULO IN ({lista_mf_str})")

    filtros_restricao_sql = ""
    if filtros_restricao:
        filtros_restricao_sql = " AND " + " AND ".join(filtros_restricao)

    # 🎯 Filtro dinâmico de colunas com cobertura TRUE
    filtro_colunas_true = ""
    if colunas_cobertura:
        condicoes_true = " OR ".join(f"{col} = TRUE" for col in colunas_cobertura)
        filtro_colunas_true = f" AND ({condicoes_true})"

    # 🧾 Query completa
    query_importar_base_itens = f"""
        SELECT 
            {colunas_select},
            SUM(ITENS) AS ITENS
        FROM parquet_scan('{caminho_base_itens}')
        WHERE 
            DAT_REFERENCIA_MODIF BETWEEN '{data_inicio}' AND '{data_fim}'
            AND TIPO_VEICULO IN ({tipos_veiculos_str})
            AND UF IN ({ufs_str})
            AND ANO_MODELO BETWEEN {ano_modelo_min} AND {ano_modelo_max}
            AND VALOR_VEICULO BETWEEN {valor_min} AND {valor_max}
            {filtros_restricao_sql}
            {filtro_colunas_true}
        GROUP BY 
            {colunas_group}
    """

    base_receita = con.execute(query_importar_base_itens).fetchdf()
    con.close()

    return base_receita



def show_resumo_base_despesa(
    tipo_coberturas,
    data_inicio, data_fim, tipo_veiculo_selecionado, tipo_veiculo_restricao, 
    ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, 
    lista_mf_filtrar, parametros):
    
    # Caminho da base principal e da tabela de classificação
    caminho_base_despesa = 'data/base_despesa.parquet'

    # Conectando ao DuckDB em memória
    con = duckdb.connect(database=':memory:')
    
    # Convertendo listas em strings formatadas corretamente para SQL
    tipos_veiculos_str = ", ".join([f"'{tipo}'" for tipo in tipo_veiculo_selecionado])
    ufs_str = ", ".join([f"'{uf}'" for uf in ufs_selecionadas])

    # Filtros adicionais baseados nas restrições
    filtros_restricao = []

    if "Blindados" in tipo_veiculo_restricao:
        filtros_restricao.append("BLINDADOS = 'Não'")
    
    if "Cabrio" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_CABRIO_CONVENCIONAL != 'Cabrio'")
    
    if "Convencional" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_CABRIO_CONVENCIONAL != 'Convencional'")
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Convencional'")
    
    if "Elétrico" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Elétrico'")
    
    if "Híbrido" in tipo_veiculo_restricao:
        filtros_restricao.append("VEIC_ELET_HIBRI_CONV != 'Híbrido'")

    # Filtro para MF_VEICULO, se houver itens na lista
    if lista_mf_filtrar:
        lista_mf_str = ", ".join(f"'{mf}'" for mf in lista_mf_filtrar)
        filtros_restricao.append(f"MF_VEICULO IN ({lista_mf_str})")

    # Unir os filtros adicionais à cláusula WHERE
    filtros_restricao_sql = ""
    if filtros_restricao:
        filtros_restricao_sql = " AND " + " AND ".join(filtros_restricao)
    
    # Construção da query com os filtros
    query_importar_base_despesa = f"""
        SELECT DISTINCT *
            
        FROM parquet_scan('{caminho_base_despesa}')
        WHERE 
            "Data Realização OS" >= '{data_inicio}' AND "Data Realização OS" <= '{data_fim}'
            AND TIPO_VEICULO IN ({tipos_veiculos_str})
            AND "UF R" IN ({ufs_str})
            AND "Ano Modelo Fipe Mapeamento" >= {ano_modelo_min} AND "Ano Modelo Fipe Mapeamento" <= {ano_modelo_max}
            AND "VALOR_VEICULO" >= {valor_min} AND "VALOR_VEICULO" <= {valor_max}
            {filtros_restricao_sql}

    """
    
    # Executando a consulta
    base_despesa = con.execute(query_importar_base_despesa).fetchdf()
    con.close()
    
    df_imposto_editado = pd.DataFrame(parametros["imposto_ajuste"])
    ajuste_cms = df_imposto_editado["Ajuste CMS (%)"].iloc[0]
    base_despesa["Ajuste CMS (%)"] = ajuste_cms
    
    df_lmi_editado = pd.DataFrame(parametros["lmi_franquia"])
    base_despesa = base_despesa.merge(
        df_lmi_editado,
        left_on=["TIPO_VEICULO", "Script Franquia"],
        right_on=["Tipo de Veículo", "Script"],
        how="left"
    ).drop(columns=["Tipo de Veículo", "Script"])
    
    base_despesa["Valor Ajustado CMS"] = ((base_despesa["Ajuste CMS (%)"] / 100)+1) * base_despesa["Valor Total Negociado"]

    def calcular_franquia_ajustada(row):
        tipo = row["TIPO_VEICULO"]
        script_franquia = row["Script Franquia"]
        script_cms = row["Script CMS"]
        os_reparo = row["OS Reparo"]
        
        # 1. Se Tipo de Veículo não é "Auto", "Moto" ou "Carga" → retorna NA
        if tipo not in ["Auto", "Moto", "Carga"]:
            return np.nan

        # 2. Se Script Franquia for "isento" → 0
        if str(script_franquia).strip().lower() == "isento":
            return 0

        # 3. Se OS Reparo = "SIM" e Script Franquia em ["Vidros", "FLR"] e tipo_guincho em ["Auto", "Carga"] → 0
        if os_reparo == "SIM" and script_cms in ["Vidros", "FLR"] and tipo in ["Auto", "Carga"]:
            return 0

        # 4. Se tipo_guincho == "Moto" → usar "Franquia (R$)"
        if tipo == "Moto":
            return row["Franquia (R$)"]

        # 5. Se Script Franquia em ["Higienização", "Cristalização"] → 0
        if script_cms in ["Higienização", "Cristalização"]:
            return 0

        # 6. Se Script Franquia em ["Matelinho", "SRA"] → Valor Total Negociado - Custo Total Financeiro
        if script_cms in ["Martelinho", "SRA"]:
            return row["Valor Total Negociado"] - row["Custo Total Financeiro"]

        # 7. Se tipo_guincho em ["Auto", "Carga"] → usar "Franquia (R$)"
        if tipo in ["Auto", "Carga"]:
            return row["Franquia (R$)"]

        # Caso nada acima satisfaça (teoricamente não deve ocorrer)
        return np.nan

    # Aplicar a função na base
    base_despesa["Franquia Ajustada"] = base_despesa.apply(calcular_franquia_ajustada, axis=1)
    
    base_despesa["Franquia Ajustada"] = base_despesa["Franquia Ajustada"].round(2)
    
    # 1. Verifica se o LMI é nulo ou igual a 0
    condicao_sem_lmi = (base_despesa["LMI (R$)"].isna()) | (base_despesa["LMI (R$)"] == 0)

    # 2. Calcula o valor base: Valor Ajustado CMS - Franquia Ajustada, garantindo que seja no mínimo 0
    valor_base = np.maximum(base_despesa["Valor Ajustado CMS"] - base_despesa["Franquia Ajustada"], 0)

    # 3. Se LMI é NA ou 0 → Despesa = valor_base
    #    Caso contrário → Despesa = menor entre o LMI e o valor_base
    base_despesa["Despesa"] = np.where(
        condicao_sem_lmi,
        valor_base,
        np.minimum(base_despesa["LMI (R$)"], valor_base)
    )

    # Arredondar se desejar:
    base_despesa["Despesa"] = base_despesa["Despesa"].round(2)
    
    return base_despesa