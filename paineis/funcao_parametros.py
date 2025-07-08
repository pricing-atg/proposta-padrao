import streamlit as st
import pandas as pd
import duckdb
import numpy as np

    
def show_parametrizacao(tipo_veiculo_selecionado, tipo_coberturas):
    
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
            # --- Veículos de Auto ---
            {"Tipo de Veículo": "Auto", "Script": "Parabrisa", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Vigia", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Lateral", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Auto", "Script": "Máquina", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Auto", "Script": "Farol", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Inteligente", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Farol Xenon/LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Lanterna", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Lanterna LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Retrov.", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Retrovisor LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "Auxiliar", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Auto", "Script": "RLP", "LMI (R$)": 1000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Auto", "Script": "RPS", "LMI (R$)": 15000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Auto", "Script": "Martelinho", "LMI (R$)": 1000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Auto", "Script": "SRA", "LMI (R$)": 1000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Auto", "Script": "Pneu", "LMI (R$)": 5000, "Franquia (R$)": 120},
            {"Tipo de Veículo": "Auto", "Script": "ADAS", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Auto", "Script": "Troca - PC", "LMI (R$)": 5000, "Franquia (R$)": 700},
            {"Tipo de Veículo": "Auto", "Script": "Reparo - PC", "LMI (R$)": 5000, "Franquia (R$)": 700},
            {"Tipo de Veículo": "Auto", "Script": "Teto Solar", "LMI (R$)": 10000, "Franquia (R$)": 250},

            # --- Veículos Moto ---
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

            # --- Veículos Carga ---
            {"Tipo de Veículo": "Carga", "Script": "Parabrisa", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Vigia", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Lateral", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Carga", "Script": "Máquina", "LMI (R$)": 10000, "Franquia (R$)": 0},
            {"Tipo de Veículo": "Carga", "Script": "Farol", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Inteligente", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Farol Xenon/LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Lanterna", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Lanterna LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Retrov.", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Retrovisor LED", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "Auxiliar", "LMI (R$)": 10000, "Franquia (R$)": 250},
            {"Tipo de Veículo": "Carga", "Script": "RLP", "LMI (R$)": 1000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Carga", "Script": "RPS", "LMI (R$)": 5000, "Franquia (R$)": 190},
            {"Tipo de Veículo": "Carga", "Script": "Pneu", "LMI (R$)": 5000, "Franquia (R$)": 120}
        ])

        df_param_filtrado = df_param_padrao[df_param_padrao["Tipo de Veículo"].isin(tipo_veiculo_selecionado)]
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