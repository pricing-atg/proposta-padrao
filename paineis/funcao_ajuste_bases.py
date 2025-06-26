import streamlit as st
import pandas as pd
import duckdb
import numpy as np

from datetime import datetime

def show_resumo_base_receita(data_inicio, data_fim, tipos_veiculos_selecionados, ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, parametros):
    
    # Base de receita
    
    # Caminho da base
    caminho_base_itens = 'data/base_itens_parte_*.parquet'
    
    # Conectando ao DuckDB em memória
    con = duckdb.connect(database=':memory:')
    
    # Convertendo listas para strings no formato SQL
    tipos_veiculos_str = ", ".join(f"'{tipo}'" for tipo in tipos_veiculos_selecionados)
    ufs_str = ", ".join(f"'{uf}'" for uf in ufs_selecionadas)
    
    # Construção da query com os filtros
    query_importar_base_itens = f"""
        SELECT DISTINCT 
            DAT_REFERENCIA_MODIF,
            Seguradora,
            tipo_guincho,
            VIDROS,
            FLR,
            MARTELINHO,
            RLP,
            RLPP,
            SRA,
            PNEU,
            RPS,
            TETO_SOLAR,
            TROCA_DE_PARACHOQUE,
            PARACHOQUE,
            "Veículo ADAS",
            SUM(ITENS) AS ITENS
        FROM parquet_scan('{caminho_base_itens}')
        WHERE 
            DAT_REFERENCIA_MODIF BETWEEN '{data_inicio}' AND '{data_fim}'
            AND tipo_guincho IN ({tipos_veiculos_str})
            AND UF IN ({ufs_str})
            AND "Ano Modelo" BETWEEN {ano_modelo_min} AND {ano_modelo_max}
            AND Valor BETWEEN {valor_min} AND {valor_max}
        GROUP BY 
            DAT_REFERENCIA_MODIF,
            Seguradora,
            tipo_guincho,
            VIDROS,
            FLR,
            MARTELINHO,
            RLP,
            RLPP,
            SRA,
            PNEU,
            RPS,
            TETO_SOLAR,
            TROCA_DE_PARACHOQUE,
            PARACHOQUE,
            "Veículo ADAS"
    """

    # Executando a consulta e fechando a conexão
    base_receita = con.execute(query_importar_base_itens).fetchdf()
    con.close()    
    
    return base_receita

def show_resumo_base_despesa(data_inicio, data_fim, tipos_veiculos_selecionados, ufs_selecionadas, ano_modelo_min, ano_modelo_max, valor_min, valor_max, parametros):
    
    # Base de despesa e OS
    
    # Caminho da base principal e da tabela de classificação
    caminho_base_despesa = 'data/base_despesa.parquet'

    # Conectando ao DuckDB em memória
    con = duckdb.connect(database=':memory:')
    
    # Convertendo listas em strings formatadas corretamente para SQL
    tipos_veiculos_str = ", ".join([f"'{tipo}'" for tipo in tipos_veiculos_selecionados])
    ufs_str = ", ".join([f"'{uf}'" for uf in ufs_selecionadas])
    
    # Construção da query com os filtros
    query_importar_base_despesa = f"""
        SELECT DISTINCT *
            
        FROM parquet_scan('{caminho_base_despesa}')
        WHERE 
            "Data Realização OS" >= '{data_inicio}' AND "Data Realização OS" <= '{data_fim}'
            AND "tipo_guincho" IN ({tipos_veiculos_str})
            AND "UF R" IN ({ufs_str})
            AND "Ano Modelo Fipe Mapeamento" >= {ano_modelo_min} AND "Ano Modelo Fipe Mapeamento" <= {ano_modelo_max}
            AND "Valor" >= {valor_min} AND "Valor" <= {valor_max}

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
        left_on=["tipo_guincho", "Script Franquia"],
        right_on=["Tipo de Veículo", "Script"],
        how="left"
    ).drop(columns=["Tipo de Veículo", "Script"])
    
    base_despesa["Valor Ajustado CMS"] = ((base_despesa["Ajuste CMS (%)"] / 100)+1) * base_despesa["Valor Total Negociado"]

    def calcular_franquia_ajustada(row):
        tipo = row["tipo_guincho"]
        script_franquia = row["Script Franquia"]
        script_cms = row["Script CMS"]
        os_reparo = row["OS Reparo"]
        
        # 1. Se tipo_guincho não é "Passeio", "Moto" ou "Pesado" → retorna NA
        if tipo not in ["Passeio", "Moto", "Pesado"]:
            return np.nan

        # 2. Se Script Franquia for "isento" → 0
        if str(script_franquia).strip().lower() == "isento":
            return 0

        # 3. Se OS Reparo = "SIM" e Script Franquia em ["Vidros", "FLR"] e tipo_guincho em ["Passeio", "Pesado"] → 0
        if os_reparo == "SIM" and script_cms in ["Vidros", "FLR"] and tipo in ["Passeio", "Pesado"]:
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

        # 7. Se tipo_guincho em ["Passeio", "Pesado"] → usar "Franquia (R$)"
        if tipo in ["Passeio", "Pesado"]:
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