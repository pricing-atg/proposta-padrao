import streamlit as st
import pandas as pd
import duckdb
import numpy as np

from datetime import datetime
    
# Período de Referência
def carregar_variavel_periodo_referencia():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT DAT_REFERENCIA_MODIF
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()

    # Converte a coluna para datetime e ordena
    df["DAT_REFERENCIA_MODIF"] = pd.to_datetime(df["DAT_REFERENCIA_MODIF"], errors='coerce')
    variavel_periodo_referencia = sorted(df["DAT_REFERENCIA_MODIF"].dropna().unique())
    
    return variavel_periodo_referencia
    
# Tipo de Veículo
def carregar_variavel_tipo_veiculo():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT TIPO_VEICULO
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_tipo_veiculo = df["TIPO_VEICULO"].unique()

    return variavel_tipo_veiculo


# Base de Região
def carregar_base_regiao():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT REGIAO,UF
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()

    return df


    
# Ano Modelo
def carregar_variavel_ano_modelo():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT ANO_MODELO
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_ano_modelo = df["ANO_MODELO"].unique()

    return variavel_ano_modelo

    
# Valor do Veículo
def carregar_variavel_valor():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT VALOR_VEICULO
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_valor = df["VALOR_VEICULO"].unique()

    return variavel_valor

# Tipo de Categoria Veículo
def carregar_variavel_tipo_categoria_veiculo():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT VEIC_CABRIO_CONVENCIONAL
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_cabrio_convencional = df["VEIC_CABRIO_CONVENCIONAL"].unique()

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT VEIC_ELET_HIBRI_CONV
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_eletrico_hibrido_convencional = df["VEIC_ELET_HIBRI_CONV"].unique()
    
    variavel_restricao = np.unique(
        np.concatenate([variavel_cabrio_convencional, variavel_eletrico_hibrido_convencional, ["Blindados"]])
        )

    return variavel_restricao
