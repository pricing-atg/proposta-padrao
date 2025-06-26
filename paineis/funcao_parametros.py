import streamlit as st
import pandas as pd
import duckdb
import numpy as np

    
def show_parametrizacao(tipos_veiculos_selecionados, tipo_coberturas):
    st.subheader("Parâmetros de Precificação")
    
    # Dicionário de mapeamento: tipo de cobertura -> scripts
    mapeamento_coberturas = {
        "Vidros": ["Parabrisa", "Vigia", "Lateral", "Máquina"],
        "FLR": ["Farol", "Inteligente", "Farol Xenon/LED", "Lanterna", "Lanterna LED", "Retrov.", "Retrovisor LED", "Auxiliar"],
        "Higienização": ["Higienização"],
        "Cristalização": ["Cristalização"],
        "Martelinho": ["Martelinho"],
        "SRA": ["SRA"],
        "RLP": ["RLP"],
        "RLPP": ["RLP","Troca - PC", "Reparo - PC"],
        "RPS": ["RPS"],
        "Pneu": ["Pneu"],
        "ADAS": ["ADAS"],
        "Polimento de Farol": ["Farol", "Inteligente", "Farol Xenon/LED"],
        "Reparo de Parabrisa": ["Parabrisa"],
        "Troca - PC": ["Troca - PC"],
        "Reparo - PC": ["Reparo - PC"]
    }

    # Agrupar todos os scripts dos tipos de coberturas selecionados
    scripts_filtrados = []
    for tipo in tipo_coberturas:
        scripts_filtrados.extend(mapeamento_coberturas.get(tipo, []))

    # 1. Imposto IPCA + Ajuste CMS
    with st.expander("1. Imposto + Ajuste CMS"):
        df_imposto_padrao = pd.DataFrame([
            {"Imposto (%)": 6.15, "Ajuste CMS (%)": 4.0}
        ])
        df_imposto_editado = st.data_editor(df_imposto_padrao, num_rows="dynamic", hide_index=True, use_container_width=True)

    # 2. LMI + Franquia por Script e Tipo de Veículo
    with st.expander("2. LMI e Franquia por Script e Tipo de Veículo"):
        df_param_padrao = pd.DataFrame([
            # --- Veículos de PASSEIO ---
            {"Tipo de Veículo": "Passeio", "Script": "Parabrisa", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Vigia", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Lateral", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "Máquina", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "Farol", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Inteligente", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Farol Xenon/LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Lanterna", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Lanterna LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Retrov.", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Retrovisor LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Auxiliar", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Passeio", "Script": "Higienização", "LMI (R$)": 0, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "Cristalização", "LMI (R$)": 0, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "RLP", "LMI (R$)": 1000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Passeio", "Script": "RPS", "LMI (R$)": 15000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Passeio", "Script": "Martelinho", "LMI (R$)": 1000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "SRA", "LMI (R$)": 1000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "Pneu", "LMI (R$)": 5000, "Franquia (R$)": 120},
            {"Tipo de Veículo": "Passeio", "Script": "ADAS", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Passeio", "Script": "Troca - PC", "LMI (R$)": 5000, "Franquia (R$)": 700},
            {"Tipo de Veículo": "Passeio", "Script": "Reparo - PC", "LMI (R$)": 5000, "Franquia (R$)": 700},
            {"Tipo de Veículo": "Passeio", "Script": "Teto Solar", "LMI (R$)": 10000, "Franquia (R$)": 250},

            # --- Veículos MOTO ---
            {"Tipo de Veículo": "Moto", "Script": "Farol", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Inteligente", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Farol Xenon/LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Lanterna", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Lanterna LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Retrov.", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Retrovisor LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "Auxiliar", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Moto", "Script": "RLP", "LMI (R$)": 600, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Moto", "Script": "RPS", "LMI (R$)": 5000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Moto", "Script": "Pneu", "LMI (R$)": 5000, "Franquia (R$)": 120},

            # --- Veículos PESADO ---
            {"Tipo de Veículo": "Pesado", "Script": "Parabrisa", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Vigia", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Lateral", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Pesado", "Script": "Máquina", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Pesado", "Script": "Farol", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Inteligente", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Farol Xenon/LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Lanterna", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Lanterna LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Retrov.", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Retrovisor LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "Auxiliar", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Pesado", "Script": "RLP", "LMI (R$)": 1000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Pesado", "Script": "RPS", "LMI (R$)": 5000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Pesado", "Script": "Pneu", "LMI (R$)": 5000, "Franquia (R$)": 120}
        ])

        df_param_filtrado = df_param_padrao[df_param_padrao["Tipo de Veículo"].isin(tipos_veiculos_selecionados)]
        df_param_filtrado = df_param_filtrado[df_param_filtrado["Script"].isin(scripts_filtrados)]
        df_param_editado = st.data_editor(
            df_param_filtrado.reset_index(drop=True),
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )

    # Coletar em dicionários para uso posterior (pode salvar no banco, cache, etc)
    parametros = {
        "imposto_ajuste": df_imposto_editado.to_dict(orient="records"),
        "lmi_franquia": df_param_editado.to_dict(orient="records")
    }
    
    return parametros