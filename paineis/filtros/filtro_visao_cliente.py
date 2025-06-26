import streamlit as st
import pandas as pd
import duckdb

from datetime import datetime
    
# Período de Referência
def carregar_variavel_periodo_referencia():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT "DAT_REFERENCIA_MODIF"
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
        SELECT DISTINCT "tipo_guincho"
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_tipo_veiculo = df["tipo_guincho"].unique()

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
        SELECT DISTINCT "Ano Modelo"
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_ano_modelo = df["Ano Modelo"].unique()

    return variavel_ano_modelo

    
# Valor do Veículo
def carregar_variavel_valor():
    # Caminho do arquivo Parquet
    caminho_base_itens = 'data/base_itens_parte_*.parquet'

    # Conectando ao DuckDB
    con = duckdb.connect(database=':memory:')

    # Consulta para carregar dados
    query_importar_base_itens = f"""
        SELECT DISTINCT "Valor"
        FROM parquet_scan('{caminho_base_itens}')
    """

    # Executando a consulta
    df = con.execute(query_importar_base_itens).fetchdf()
    con.close()
    
    variavel_valor = df["Valor"].unique()

    return variavel_valor
