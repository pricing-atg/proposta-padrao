import streamlit as st
import pandas as pd
import numpy as np

# Vidros - Ok
def validacao_funcao_freq_cms_vidros(base_receita, base_despesa):
    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["tipo_guincho"] != "Moto"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções auxiliares de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Cria a coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista de resultados por tipo
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita["VIDROS"] == True) &
                (base_receita["tipo_guincho"] == tipo)
            ].copy()

            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Vidros") &
                (base_despesa["tipo_guincho"] == tipo)
            ].copy()
            
            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]
            
            

            

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_vidros_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_vidros_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_vidros_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_vidros_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # Resultado para o resumo geral
            resultados_totais.append({
                "Script": "Vidros",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
                        
            
            
    # DataFrame com o resumo geral
    df_resumo_geral = pd.DataFrame(resultados_totais)
    return df_resumo_geral  
            
# FLR - Ok
def validacao_funcao_freq_cms_flr(base_receita, base_despesa):

    # ✅ Ordem personalizada dos tipos de guincho
    ordem_tipo_guincho = ["Passeio", "Moto", "Pesado"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipos_disponiveis = base_receita["tipo_guincho"].dropna().unique()
    tipos_guincho = [tipo for tipo in ordem_tipo_guincho if tipo in tipos_disponiveis]

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                (base_receita["FLR"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "FLR") & 
                (base_despesa["tipo_guincho"] == tipo)
            ]
            
            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
            
            

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_flr_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_flr_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_flr_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_flr_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "FLR",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Higienização - Ok
def validacao_funcao_freq_cms_higienizacao(base_receita, base_despesa):
    # ❌ Filtra apenas os registros de guincho tipo "Passeio"
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"]
    base_despesa = base_despesa[base_despesa["tipo_guincho"] == "Passeio"]
    
    # 🔄 Tipos de guincho disponíveis após o filtro
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()
    
    # Cria coluna AnoMes em ambas as bases
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"], errors="coerce").dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"], errors="coerce").dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):
            
            # ✅ Garante que valores nulos sejam tratados corretamente
            receita_filtrada = base_receita[
                (base_receita["tipo_guincho"] == tipo) & 
                (base_receita["VIDROS"].fillna(False) == True)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["tipo_guincho"] == tipo) & 
                (base_despesa["Script CMS"] == "Higienização")
            ]

            # Agrupamento por período apenas da despesa
            resultado_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", 
                "Despesa": "sum"
            })

            # Cálculo das métricas
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = np.nan  # Não há mais Qtd Itens para calcular
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Funções de formatação
            def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            def f_int(x): return f"{int(x):,}".replace(",", ".")

            # Cópia para exibição formatada
            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)

            colunas_ordem = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe = resultado_mes_exibe[colunas_ordem]

            st.write("**Escolha do período para CMS**")
            
            # Exibe a tabela editável
            resultado_mes_editado = st.data_editor(
                resultado_mes_exibe,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                key=f"data_editor_periodo_higienizacao_{tipo}"
            )

            # Filtros aplicados
            periodos_selecionados = resultado_mes.loc[resultado_mes_editado["Selecionar"] == True, "AnoMes"]
            despesa_final = despesa_filtrada[despesa_filtrada["AnoMes"].isin(periodos_selecionados)]

            # Resumo total
            total_os = despesa_final["Qtd. OS's"].sum()
            total_despesa = despesa_final["Despesa"].sum()
            total_cms = total_despesa / total_os if total_os > 0 else 0

            st.divider()
            st.write("**Resumo CMS**")
            col1, col2, col3 = st.columns(3)

            col1.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os)}</div>", unsafe_allow_html=True)
            col2.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa)}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Higienização",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": 0.0036  # Valor fixo informado
            })
            
            st.write("")
    
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Cristalização - Ok
def validacao_funcao_freq_cms_cristalizacao(base_receita, base_despesa):
    
    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    # 🔁 Armazena os resultados no resumo geral
    resultados_totais.append({
        "Script": "Cristalização",
        "Tipo Veículo": "Passeio",
        "CMS": 115,
        "Frequência": 0.0036 
    })
    
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Martelinho - Ok
def validacao_funcao_freq_cms_martelinho(base_receita, base_despesa):

    # ❌ Filtra apenas os registros do tipo "Passeio"
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"]
    
    # 🔄 Atualiza os tipos disponíveis após o filtro
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):
            st.markdown("#### Tabelas por Seguradora e por Período")

            # Filtrando por Martelinho e tipo
            receita_filtrada = base_receita[
                (base_receita["MARTELINHO"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Martelinho") & 
                (base_despesa["tipo_guincho"] == tipo)
            ]

            # 📊 Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # 📆 Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]



            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_martelinho_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_martelinho_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_martelinho_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_martelinho_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Martelinho",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# SRA - Ok
def validacao_funcao_freq_cms_sra(base_receita, base_despesa):
    # Filtra só registros tipo "Passeio"
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"].copy()
    
    # Atualiza os tipos disponíveis (após filtro)
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções de formatação para exibição
    def f_valor(x): 
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): 
        return f"{int(x):,}".replace(",", ".")
    def f_perc(x): 
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes usando .loc para evitar warning
    base_receita.loc[:, "AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa.loc[:, "AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):
            st.markdown("#### Tabelas por Seguradora e por Período")

            receita_filtrada = base_receita[
                (base_receita["SRA"] == True) &
                (base_receita["tipo_guincho"] == tipo)
            ].copy()

            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "SRA") &
                (base_despesa["tipo_guincho"] == tipo)
            ].copy()

            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_sra_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_sra_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_sra_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_sra_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            resultados_totais.append({
                "Script": "SRA",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")

    df_resumo_geral = pd.DataFrame(resultados_totais)

    return df_resumo_geral

# RLP - Ok
def validacao_funcao_freq_cms_rlp(base_receita, base_despesa, parametros):
    # ✅ Ordem personalizada para os tipos de guincho
    ordem_tipo_guincho = ["Passeio", "Moto", "Pesado"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipos_disponiveis = base_receita["tipo_guincho"].dropna().unique()
    tipos_guincho = [tipo for tipo in ordem_tipo_guincho if tipo in tipos_disponiveis]

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    # Funções auxiliares
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes para as duas bases
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Obter o valor de LMI para Passeio e Script "RLP", caso necessário
    lmi_rlp_passeio = None
    if "Passeio" in tipos_guincho:
        df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
        filtro_passeio_rlp = (df_lmi_franquia["Tipo de Veículo"] == "Passeio") & (df_lmi_franquia["Script"] == "RLP")
        if not df_lmi_franquia[filtro_passeio_rlp].empty:
            lmi_rlp_passeio = df_lmi_franquia[filtro_passeio_rlp]["LMI (R$)"].values[0]
    
    # Processamento por tipo de guincho
    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):
            if tipo == "Passeio" and lmi_rlp_passeio == 1500:
                
                receita_filtrada = base_receita[
                    (base_receita["RLP"] == True) & 
                    (base_receita["tipo_guincho"] == tipo)
                ]
                despesa_filtrada = base_despesa[
                    (base_despesa["Script CMS"] == "RLP") & 
                    (base_despesa["tipo_guincho"] == tipo)
                ]

                # Agrupamento por Seguradora
                receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
                receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

                despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                    "Qtd. OS's": "sum", "Despesa": "sum"
                })

                resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
                resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
                resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
                resultado_cia = resultado_cia.fillna(0)
                resultado_cia["Selecionar"] = True

                # Agrupamento por Mês
                receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
                receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

                despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                    "Qtd. OS's": "sum", "Despesa": "sum"
                })

                resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
                resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
                resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
                resultado_mes = resultado_mes.fillna(0)
                resultado_mes["Selecionar"] = True

                # Formatação para exibição
                resultado_cia_exibe = resultado_cia.copy()
                resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
                resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
                resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
                resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
                resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

                resultado_mes_exibe = resultado_mes.copy()
                resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
                resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
                resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
                resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
                resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

                # Reordenação de colunas
                # Seguradora e frequência
                colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
                resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
                
                # Seguradora e CMS
                colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
                resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
                
                
                # Período e frequência
                colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
                resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
                
                # Período e CMS
                colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
                resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Escolha das Seguradoras para frequência**")
                    resultado_cia_exibe_freq_editado = st.data_editor(
                        resultado_cia_exibe_freq,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_seguradora_rlp_freq_{tipo}"
                    )

                # Editor por mês
                with col2:
                    st.write("**Escolha das Seguradoras para CMS**")
                    resultado_cia_exibe_cms_editado = st.data_editor(
                        resultado_cia_exibe_cms,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_seguradora_rlp_cms_{tipo}"
                    )
                    
                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Escolha do período para frequência**")
                    resultado_mes_exibe_freq_editado = st.data_editor(
                        resultado_mes_exibe_freq,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_periodo_rlp_freq_{tipo}"
                    )

                # Editor por mês
                with col2:
                    st.write("**Escolha do período para CMS**")
                    resultado_mes_exibe_cms_editado = st.data_editor(
                        resultado_mes_exibe_cms,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_periodo_rlp_cms_{tipo}"
                    )
                
                
                
                # Filtros aplicados
                seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
                seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
                
                periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
                periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

                receita_final_freq = receita_filtrada[
                    receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                    receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
                ]
                
                despesa_final_freq = despesa_filtrada[
                    despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                    despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
                ]
                despesa_final_cms = despesa_filtrada[
                    despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                    despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
                ]
                
                

                # Criação das faixas
                faixa1 = despesa_final_cms[
                    (despesa_final_cms["Valor Ajustado CMS"] > 0) &
                    (despesa_final_cms["Valor Ajustado CMS"] <= 500)
                ]
                faixa2 = despesa_final_cms[
                    (despesa_final_cms["Valor Ajustado CMS"] > 500) &
                    (despesa_final_cms["Valor Ajustado CMS"] <= 800)
                ]
                faixa3 = despesa_final_cms[
                    (despesa_final_cms["Valor Ajustado CMS"] > 800)
                ]

                # Calculando os valores
                col1 = faixa1["Valor Ajustado CMS"].sum() / faixa1["Qtd. OS's"].sum() if faixa1["Qtd. OS's"].sum() else 0
                col2 = faixa2["Valor Ajustado CMS"].sum() / faixa2["Qtd. OS's"].sum() if faixa2["Qtd. OS's"].sum() else 0
                col3 = faixa3["Valor Ajustado CMS"].sum() / faixa3["Qtd. OS's"].sum() if faixa3["Qtd. OS's"].sum() else 0
                col4 = faixa1["Qtd. OS's"].sum()
                col5 = faixa2["Qtd. OS's"].sum()
                col6 = faixa3["Qtd. OS's"].sum()

                # Pega os dados do parâmetro
                df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
                
                # LMI específico para Passeio e Script "RLP"
                lmi_rlp_passeio = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Passeio") & 
                    (df_lmi_franquia["Script"] == "RLP")
                ]["LMI (R$)"].values[0]

                # Calculando as colunas finais
                col9 = col3 * (lmi_rlp_passeio / 1000)
                
                # Calculando a nova col10 como a média ponderada das faixas de CMS
                soma_qtd_os = col4 + col5 + col6
                col10 = (
                    (col1 * col4) +
                    (col2 * col5) +
                    (col9 * col6)
                ) / soma_qtd_os if soma_qtd_os else 0

                franquia_rlp_passeio = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Passeio") & 
                    (df_lmi_franquia["Script"] == "RLP")
                ]["Franquia (R$)"].values[0]
                
                # Resultado final: col10 - franquia
                col11 = col10 - franquia_rlp_passeio

                # Montando o DataFrame com valores formatados
                df_resultado_faixa_cms_os = pd.DataFrame([{
                    "CMS até R$500": f_valor(col1),
                    "CMS entre R$500-R$800": f_valor(col2),
                    "CMS acima de R$800": f_valor(col3),
                    "Qtd. OS's até R$500": f_int(col4),
                    "Qtd. OS's entre R$500-R$800": f_int(col5),
                    "Qtd. OS's acima de R$800": f_int(col6)
                }])
                
                df_resultado = pd.DataFrame([{
                    "LMI RLP": f_valor(lmi_rlp_passeio),
                    "Franquia RLP": f_valor(franquia_rlp_passeio),
                    "CMS ajustado (CMS acima de R$ 800 * LMI / 1000)": f_valor(col9),
                    "CMS Geral": f_valor(col10),
                    "Resultado (CMS Geral - franquia)": f_valor(col11)
                }])

                
                # --- Resumo Total (Interseção dos Filtros) ---
                st.divider()
                st.markdown("### Resumo")
                
                st.dataframe(df_resultado_faixa_cms_os, use_container_width=True, hide_index=True)
                
                st.dataframe(df_resultado, use_container_width=True, hide_index=True)
                
                col1, col2 = st.columns(2)

                # Cálculo da frequência
                total_qtd_os = despesa_final_freq["Qtd. OS's"].sum()
                total_itens = receita_final_freq["ITENS"].sum()

                freq = (total_qtd_os * 12) / total_itens if total_itens else 0

                col1.markdown(f"<div style='font-size:18px;'><b>CMS de RLP Agravado</b><br>{f_valor(col11)}</div>", unsafe_allow_html=True)
                col2.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(freq)}</div>", unsafe_allow_html=True)

                # Lista para armazenar os resultados por tipo de guincho
                resultados_totais = []
                    
                # 🔁 Armazena os resultados no resumo geral
                resultados_totais.append({
                    "Script": "RLP",
                    "Tipo Veículo": "Passeio",
                    "CMS": col11,
                    "Frequência": freq
                })
                
                st.write("")

            else:
                
                receita_filtrada = base_receita[
                    (base_receita["RLP"] == True) & 
                    (base_receita["tipo_guincho"] == tipo)
                ]
                despesa_filtrada = base_despesa[
                    (base_despesa["Script CMS"] == "RLP") & 
                    (base_despesa["tipo_guincho"] == tipo)
                ]

                # Agrupamento por Seguradora
                receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
                receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

                despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                    "Qtd. OS's": "sum", "Despesa": "sum"
                })

                resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
                resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
                resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
                resultado_cia = resultado_cia.fillna(0)
                resultado_cia["Selecionar"] = True

                # Agrupamento por Mês
                receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
                receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

                despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                    "Qtd. OS's": "sum", "Despesa": "sum"
                })

                resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
                resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
                resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
                resultado_mes = resultado_mes.fillna(0)
                resultado_mes["Selecionar"] = True

                # Formatação para exibição
                resultado_cia_exibe = resultado_cia.copy()
                resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
                resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
                resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
                resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
                resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

                resultado_mes_exibe = resultado_mes.copy()
                resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
                resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
                resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
                resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
                resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

                # Reordenação de colunas
                # Seguradora e frequência
                colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
                resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
                
                # Seguradora e CMS
                colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
                resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
                
                
                # Período e frequência
                colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
                resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
                
                # Período e CMS
                colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
                resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Escolha das Seguradoras para frequência**")
                    resultado_cia_exibe_freq_editado = st.data_editor(
                        resultado_cia_exibe_freq,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_seguradora_rlp_freq_{tipo}"
                    )

                # Editor por mês
                with col2:
                    st.write("**Escolha das Seguradoras para CMS**")
                    resultado_cia_exibe_cms_editado = st.data_editor(
                        resultado_cia_exibe_cms,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_seguradora_rlp_cms_{tipo}"
                    )
                    
                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Escolha do período para frequência**")
                    resultado_mes_exibe_freq_editado = st.data_editor(
                        resultado_mes_exibe_freq,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_periodo_rlp_freq_{tipo}"
                    )

                # Editor por mês
                with col2:
                    st.write("**Escolha do período para CMS**")
                    resultado_mes_exibe_cms_editado = st.data_editor(
                        resultado_mes_exibe_cms,
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        use_container_width=True,
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_periodo_rlp_cms_{tipo}"
                    )
                
                
                
                # Filtros aplicados
                seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
                seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
                
                periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
                periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

                receita_final_freq = receita_filtrada[
                    receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                    receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
                ]
                
                despesa_final_freq = despesa_filtrada[
                    despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                    despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
                ]
                despesa_final_cms = despesa_filtrada[
                    despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                    despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
                ]

                # Resumo final frequência
                total_itens_freq = receita_final_freq["ITENS"].sum()
                total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
                total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
                
                # Resumo final CMS
                total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
                total_despesa_cms = despesa_final_cms["Despesa"].sum()
                total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
                
                
                
                st.divider()
                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Resumo Frequência**")
                    subcol1, subcol2, subcol3 = st.columns(3)
                    subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                    subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                    subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

                # Editor por mês
                with col2:
                    st.write("**Resumo CMS**")
                    subcol4, subcol5, subcol6 = st.columns(3)
                    subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                    subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                    subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
                
                
                
                # 🔁 Armazena os resultados no resumo geral
                resultados_totais.append({
                    "Script": "RLP",
                    "Tipo Veículo": tipo,
                    "CMS": total_cms,
                    "Frequência": total_freq
                })
                
                st.write("")
                
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# RPS - Ok
def validacao_funcao_freq_cms_rps(base_receita, base_despesa, parametros):
    
    # ✅ Ordem personalizada
    ordem_tipo_guincho = ["Passeio", "Moto", "Pesado"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipos_disponiveis = base_receita["tipo_guincho"].dropna().unique()
    tipos_guincho = [tipo for tipo in ordem_tipo_guincho if tipo in tipos_disponiveis]

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    # Tipos de guincho disponíveis
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()
    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita["RPS"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "RPS") & 
                (base_despesa["tipo_guincho"] == tipo)
            ]

            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]
            
            

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_rps_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_rps_cms_{tipo}"
                )
            
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_rps_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_rps_cms_{tipo}"
                )

            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            if tipo in "Passeio":
                # Dados em formato de lista de dicionários
                dados_rps2 = [
                    {"ATENDIMENTO": 19044143, "VALOR NEGOCIADO": "R$ 2.010,00"},
                    {"ATENDIMENTO": 19016860, "VALOR NEGOCIADO": "R$ 3.867,23"},
                    {"ATENDIMENTO": 19021026, "VALOR NEGOCIADO": "R$ 1.392,00"},
                    {"ATENDIMENTO": 19051107, "VALOR NEGOCIADO": "R$ 2.054,00"},
                    {"ATENDIMENTO": 19062265, "VALOR NEGOCIADO": "R$ 3.100,00"},
                    {"ATENDIMENTO": 19045910, "VALOR NEGOCIADO": "R$ 2.000,00"},
                    {"ATENDIMENTO": 19056465, "VALOR NEGOCIADO": "R$ 1.010,00"},
                    {"ATENDIMENTO": 19071576, "VALOR NEGOCIADO": "R$ 3.630,00"},
                    {"ATENDIMENTO": 19073196, "VALOR NEGOCIADO": "R$ 1.098,00"},
                    {"ATENDIMENTO": 19071562, "VALOR NEGOCIADO": "R$ 650,00"},
                    {"ATENDIMENTO": 19068413, "VALOR NEGOCIADO": "R$ 1.800,00"},
                    {"ATENDIMENTO": 19121460, "VALOR NEGOCIADO": "R$ 1.780,00"},
                    {"ATENDIMENTO": 19090054, "VALOR NEGOCIADO": "R$ 950,00"},
                    {"ATENDIMENTO": 19077898, "VALOR NEGOCIADO": "R$ 2.600,00"},
                    {"ATENDIMENTO": 18915573, "VALOR NEGOCIADO": "R$ 2.737,00"},
                    {"ATENDIMENTO": 19107809, "VALOR NEGOCIADO": "R$ 20.909,94"},
                    {"ATENDIMENTO": 19122406, "VALOR NEGOCIADO": "R$ 3.000,00"},
                ]

                # Criar o DataFrame
                dados_rps2 = pd.DataFrame(dados_rps2)

                # Converter os valores negociados para float
                dados_rps2["VALOR NEGOCIADO"] = dados_rps2["VALOR NEGOCIADO"].str.replace("R$ ", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
                
                # Pega os dados do parâmetro
                df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])

                lmi_rps = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Passeio") &
                    (df_lmi_franquia["Script"] == "RPS")
                ]["LMI (R$)"].values[0]

                franquia_rps = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Passeio") &
                    (df_lmi_franquia["Script"] == "RPS")
                ]["Franquia (R$)"].values[0]
                
                dados_rps2["LMI"] = lmi_rps
                dados_rps2["Franquia"] = franquia_rps
                
                dados_rps2["Despesa"] = np.minimum(
                    dados_rps2["VALOR NEGOCIADO"] - dados_rps2["Franquia"],
                    dados_rps2["LMI"]
                )
                
                despesa_media_cotacao = dados_rps2["Despesa"].mean().__round__(2)
                
                despesa_agravada = despesa_media_cotacao *0.1 + total_cms * 0.9
                
                total_freq_agravada = total_freq * (1.08)
                
                st.divider()
                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Resumo Frequência**")
                    subcol1, subcol2, subcol3, subcol4 = st.columns(4)
                    subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                    subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                    subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)
                    subcol4.markdown(f"<div style='font-size:18px;'><b>Freq. Agravada (8%)</b><br>{f_perc(total_freq_agravada)}</div>", unsafe_allow_html=True)

                # Editor por mês
                with col2:
                    st.write("**Resumo CMS**")
                    subcol5, subcol6, subcol7, subcol8 = st.columns(4)
                    subcol5.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                    subcol6.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                    subcol7.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)
                    subcol8.markdown(f"<div style='font-size:18px;'><b>CMS Agravado</b><br>{f_valor(despesa_agravada)}</div>", unsafe_allow_html=True)
                
                
                
                # 🔁 Armazena os resultados no resumo geral
                resultados_totais.append({
                    "Script": "RPS",
                    "Tipo Veículo": tipo,
                    "CMS": despesa_agravada,
                    "Frequência": total_freq_agravada
                })
                
                st.write("")
                
            else:
                st.divider()
                col1, col2 = st.columns(2)

                # Editor por seguradora
                with col1:
                    st.write("**Resumo Frequência**")
                    subcol1, subcol2, subcol3 = st.columns(3)
                    subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                    subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                    subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

                # Editor por mês
                with col2:
                    st.write("**Resumo CMS**")
                    subcol4, subcol5, subcol6 = st.columns(3)
                    subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                    subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                    subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)

                
                
                # 🔁 Armazena os resultados no resumo geral
                resultados_totais.append({
                    "Script": "RPS",
                    "Tipo Veículo": tipo,
                    "CMS": total_cms,
                    "Frequência": total_freq
                })
                
                st.write("")
                
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Pneu - Ok
def validacao_funcao_freq_cms_pneu(base_receita, base_despesa, parametros):
    
     # ✅ Ordem personalizada
    ordem_tipo_guincho = ["Passeio", "Moto", "Pesado"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipos_disponiveis = base_receita["tipo_guincho"].dropna().unique()
    tipos_guincho = [tipo for tipo in ordem_tipo_guincho if tipo in tipos_disponiveis]

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita["PNEU"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["tem_pneu"] == True) & 
                (base_despesa["tipo_guincho"] == tipo)
            ]
            
            # Pega os dados do parâmetro
            df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
            
            lmi_pneu = df_lmi_franquia[
                (df_lmi_franquia["Tipo de Veículo"] == tipo) &
                (df_lmi_franquia["Script"] == "Pneu")
            ]["LMI (R$)"].values[0]

            franquia_pneu = df_lmi_franquia[
                (df_lmi_franquia["Tipo de Veículo"] == tipo) &
                (df_lmi_franquia["Script"] == "Pneu")
            ]["Franquia (R$)"].values[0]
            
            # Critério de LMI e Franquia diferente para Pneu que não foi coletado no join anterior
            
            despesa_filtrada["lmi_pneu"] = lmi_pneu
            
            despesa_filtrada["franquia_pneu"] = franquia_pneu
            
            valor_base = np.maximum(despesa_filtrada["Valor Ajustado CMS"] - despesa_filtrada["franquia_pneu"], 0)
            
            despesa_filtrada["Despesa"] = np.minimum(despesa_filtrada["lmi_pneu"], valor_base)

            # Arredondar se desejar:
            despesa_filtrada["Despesa"] = despesa_filtrada["Despesa"].round(2)

            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia,despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes,despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]
            
            

            

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_pneu_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_pneu_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_pneu_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_pneu_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Pneu",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            st.write("")
    
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# ADAS - Ok
def validacao_funcao_freq_cms_adas(base_receita, base_despesa, parametros):

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    # Filtra tipo de guincho e gera coluna AnoMes
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"]
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)

    # Filtragem de ADAS
    receita_filtrada = base_receita[base_receita["VIDROS"] == True]
    seguradoras_com_adas = receita_filtrada[receita_filtrada["Veículo ADAS"] == "Sim"]["Seguradora"].unique()
    receita_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(seguradoras_com_adas)]

    with st.expander("▶ Passeio"):
        
        # Interface Streamlit
        st.markdown("### 🔎 Filtros")

        meses_disponiveis = sorted(receita_filtrada["AnoMes"].unique())
        seguradoras_disponiveis = sorted(receita_filtrada["Seguradora"].unique())

        meses_selecionados = st.multiselect("Selecionar meses (Ano/Mês):", meses_disponiveis, default=meses_disponiveis)
        seguradoras_selecionadas = st.multiselect("Selecionar seguradoras:", seguradoras_disponiveis, default=seguradoras_disponiveis)

        receita_filtrada = receita_filtrada[
            receita_filtrada["AnoMes"].isin(meses_selecionados) &
            receita_filtrada["Seguradora"].isin(seguradoras_selecionadas)
        ]

        # TABELA 1 - Por Seguradora
        total_por_seguradora = (
            receita_filtrada.groupby("Seguradora")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Total de Itens"})
        )
        adas_por_seguradora = (
            receita_filtrada[receita_filtrada["Veículo ADAS"] == "Sim"]
            .groupby("Seguradora")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Itens com ADAS"})
        )

        tabela_seguradora = pd.merge(total_por_seguradora, adas_por_seguradora, on="Seguradora", how="left")
        tabela_seguradora["Itens com ADAS"] = tabela_seguradora["Itens com ADAS"].fillna(0)
        tabela_seguradora["Proporção com ADAS"] = tabela_seguradora["Itens com ADAS"] / tabela_seguradora["Total de Itens"]

        # TABELA 2 - Por Mês
        total_por_mes = (
            receita_filtrada.groupby("AnoMes")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Total de Itens"})
        )
        adas_por_mes = (
            receita_filtrada[receita_filtrada["Veículo ADAS"] == "Sim"]
            .groupby("AnoMes")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Itens com ADAS"})
        )

        tabela_mes = pd.merge(total_por_mes, adas_por_mes, on="AnoMes", how="left")
        tabela_mes["Itens com ADAS"] = tabela_mes["Itens com ADAS"].fillna(0)
        tabela_mes["Proporção com ADAS"] = tabela_mes["Itens com ADAS"] / tabela_mes["Total de Itens"]

        # --- PROJEÇÃO CUMULATIVA DA PROPORÇÃO COM ADAS ---

        # Ordenar por data
        tabela_mes["AnoMes_dt"] = pd.to_datetime(tabela_mes["AnoMes"])
        tabela_mes = tabela_mes.sort_values("AnoMes_dt").reset_index(drop=True)

        if len(tabela_mes) >= 2:
            crescimento_medio_prop = (
                tabela_mes["Proporção com ADAS"].iloc[-1] - tabela_mes["Proporção com ADAS"].iloc[0]
            ) / (len(tabela_mes) - 1)

            # Inicializar últimos valores
            ultimo_mes_dt = tabela_mes["AnoMes_dt"].iloc[-1]
            prop_adas_atual = tabela_mes["Proporção com ADAS"].iloc[-1]
            total_itens_atual = tabela_mes["Total de Itens"].iloc[-1]

            projecoes = []

            for i in range(1, 7):
                novo_mes_dt = ultimo_mes_dt + pd.DateOffset(months=i)
                novo_mes_str = novo_mes_dt.to_period("M").strftime("%Y-%m")

                prop_adas_atual += crescimento_medio_prop
                total_itens_atual = (prop_adas_atual / (prop_adas_atual - crescimento_medio_prop)) * total_itens_atual
                itens_adas_atual = total_itens_atual * prop_adas_atual

                projecoes.append({
                    "AnoMes": novo_mes_str,
                    "Total de Itens": round(total_itens_atual),
                    "Itens com ADAS": round(itens_adas_atual),
                    "Proporção com ADAS": prop_adas_atual
                })

            df_projecoes = pd.DataFrame(projecoes)

            tabela_mes_final = pd.concat([
                tabela_mes.drop(columns=["AnoMes_dt"]),
                df_projecoes
            ], ignore_index=True)
        else:
            tabela_mes_final = tabela_mes.drop(columns=["AnoMes_dt"])

        # Exibir tabelas lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Por Seguradora")
            st.dataframe(
                tabela_seguradora.style.format({
                    "Total de Itens": f_int,
                    "Itens com ADAS": f_int,
                    "Proporção com ADAS": "{:.2%}"
                }),
                hide_index=True
            )

        with col2:
            st.markdown("#### 📆 Por Mês com Projeções")
            st.dataframe(
                tabela_mes_final.style.format({
                    "Total de Itens": f_int,
                    "Itens com ADAS": f_int,
                    "Proporção com ADAS": "{:.2%}"
                }),
                hide_index=True
            )
            
        st.markdown("---")
        st.markdown("### Resumo")
        
        base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)
        
        despesa_filtrada = base_despesa[
            base_despesa["AnoMes"].isin(meses_selecionados) &
            base_despesa["Seguradora"].isin(seguradoras_selecionadas) &
            (base_despesa["tipo_guincho"] == 'Passeio') &
            (base_despesa["Script Franquia"] == 'Parabrisa') &
            (base_despesa["Veículo ADAS"] == 'Sim')
        ]

        # 1ª linha: totais médios e valores de franquia
        total_itens = receita_filtrada["ITENS"].sum() / len(meses_selecionados)
        total_itens_adas = receita_filtrada[receita_filtrada["Veículo ADAS"] == "Sim"]["ITENS"].sum() / len(meses_selecionados)
        prop_geral_itens_adas = total_itens_adas/total_itens

        qtd_os_com_reparo = despesa_filtrada[despesa_filtrada["OS Reparo"] == "SIM"]["Qtd. OS's"].sum() / len(meses_selecionados)
        qtd_os_sem_reparo = despesa_filtrada[despesa_filtrada["OS Reparo"] == "NÃO"]["Qtd. OS's"].sum() / len(meses_selecionados)

        # Pega os dados do parâmetro
        df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
        franquia_adas = df_lmi_franquia[
            (df_lmi_franquia["Tipo de Veículo"] == 'Passeio') &
            (df_lmi_franquia["Script"] == "ADAS")
        ]["Franquia (R$)"].values[0]

        # Parâmetros lado a lado: CMS com Franquia e ADAS
        col_input1, col_input2 = st.columns(2)
        valor_franquia_padrao = col_input1.number_input("Valor CMS com Franquia", min_value=0.0, value=450.0, step=50.0)
        valor_franquia_adas = col_input2.number_input("Valor da franquia ADAS (padrão)", min_value=0.0, value=float(franquia_adas), step=50.0)

        # Mostrar 1ª linha dos valores
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total médio de itens por mês", f_int(total_itens))
        col2.metric("Total médio de itens ADAS por mês", f_int(total_itens_adas))
        col3.metric("Proporção de Itens de ADAS", f_perc(prop_geral_itens_adas))
        col4.metric("Qtd. média OS com reparo/mês", f_int(qtd_os_com_reparo))
        col5.metric("Qtd. média OS sem reparo/mês", f_int(qtd_os_sem_reparo))

        # 2ª linha: considerar reparo de PB e cálculo total
        considerar_reparo = st.toggle("Considerar Reparo de PB?", value=True)

        if considerar_reparo:
            total_os = (qtd_os_com_reparo + qtd_os_sem_reparo)
        else:
            total_os = qtd_os_sem_reparo

        # CMS real ajustado
        total_cms = valor_franquia_padrao - valor_franquia_adas

        # Frequência anual estimada
        if total_itens_adas > 0:
            total_freq = (total_os * 12) / total_itens_adas
        else:
            total_freq = 0

        # Mostrar 2ª linha dos valores
        col1b, col2b, col3b = st.columns(3)
        col1b.metric("Total de OS considerado", f_int(total_os))
        col2b.metric("Valor de CMS", f_valor(total_cms))
        col3b.metric("Frequência anual estimada", f_perc(total_freq))
    
    # 🔁 Armazena os resultados no resumo geral
    resultados_totais.append({
        "Script": "ADAS",
        "Tipo Veículo": "Passeio",
        "CMS": total_cms,
        "Frequência": total_freq
    })

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Polimento de Farol - Ok
def validacao_funcao_freq_cms_polimento_farol(base_receita, base_despesa):

    # ✅ Ordem personalizada dos tipos de guincho
    ordem_tipo_guincho = ["Passeio", "Moto", "Pesado"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipos_disponiveis = base_receita["tipo_guincho"].dropna().unique()
    tipos_guincho = [tipo for tipo in ordem_tipo_guincho if tipo in tipos_disponiveis]

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                (base_receita["FLR"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "FLR") & 
                (base_despesa["tipo_guincho"] == tipo) & 
                (base_despesa["Polidor de Farol"] == "SIM")
            ]
            
            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
            
            

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_polimento_farol_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_polimento_farol_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_polimento_farol_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_polimento_farol_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Polimento de Farol",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Reparo de PB - Ok
def validacao_funcao_freq_cms_reparo_parabrisa(base_receita, base_despesa):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["tipo_guincho"] != "Moto"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                (base_receita["VIDROS"] == True) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script Franquia"] == "Parabrisa") & 
                (base_despesa["tipo_guincho"] == tipo) & 
                (base_despesa["OS Reparo"] == "SIM")
            ]
            
            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
            
            

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_reparo_parabrisa_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_reparo_parabrisa_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_reparo_parabrisa_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_reparo_parabrisa_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Reparo de Parabrisa",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# RLPP - Ok
def validacao_funcao_freq_cms_rlpp(base_receita, base_despesa, parametros):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"].copy()

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    resultados_totais = []
    
    with st.expander("▶ Passeio"):
        
        # Tabela de referência de troca e reparo de Para-choque - Tokio
        st.markdown("#### Análise Troca/Reparo de Para-choque Tokio")

        # Filtragem das bases
        receita_filtrada = base_receita[
            (base_receita["TROCA_DE_PARACHOQUE"] == True) & 
            (base_receita["tipo_guincho"] == "Passeio") & 
            (base_receita["Seguradora"].str.contains("TOKIO", na=False))
        ]
        despesa_filtrada = base_despesa[
            (base_despesa["Script CMS"] == "Para-choque") & 
            (base_despesa["tipo_guincho"] == "Passeio") & 
            (base_despesa["Seguradora"].str.contains("TOKIO", na=False))
        ]
    

        # Agrupamento por Mês
        receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
        receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

        despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
            "Qtd. OS's": "sum",
            "Despesa": "sum"
        })

        resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
        resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
        resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
        resultado_mes = resultado_mes.fillna(0)
        resultado_mes["Selecionar"] = True

        resultado_mes_exibe = resultado_mes.copy()
        resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
        resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
        resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
        resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
        resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
        
        
        # Período e frequência
        colunas_ordem_mes = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Despesa", "Frequência", "CMS", "Selecionar"]
        resultado_mes_exibe_ajust = resultado_mes_exibe[colunas_ordem_mes]
            
        
        st.write("**Escolha do período para frequência e CMS**")
        resultado_mes_exibe_editado = st.data_editor(
            resultado_mes_exibe_ajust,
            column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
            use_container_width=True,
            hide_index=True,
            disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Despesa", "Frequência", "CMS"],
            key=f"data_editor_periodo_rlpp_passeio"
        )

        
        
        # Filtros aplicados
        periodos_selecionados = resultado_mes.loc[resultado_mes_exibe_editado["Selecionar"], "AnoMes"]

        receita_final = receita_filtrada[
            receita_filtrada["AnoMes"].isin(periodos_selecionados)
        ]
        
        despesa_final = despesa_filtrada[
            despesa_filtrada["AnoMes"].isin(periodos_selecionados)
        ]
        
        qtd_periodos = len(periodos_selecionados)

        # Resumo final frequência e CMS
        total_itens = receita_final["ITENS"].sum() / qtd_periodos if qtd_periodos > 0 else 0  # Média mensal de itens
        total_os = despesa_final["Qtd. OS's"].sum() / qtd_periodos if qtd_periodos > 0 else 0  # Média mensal de OSs
        total_freq = (total_os * 12) / total_itens if total_itens > 0 else 0  # Frequência anualizada
        total_despesa_cms = despesa_final["Despesa"].sum()  # Soma total das despesas
        total_cms = total_despesa_cms / despesa_final["Qtd. OS's"].sum() if despesa_final["Qtd. OS's"].sum() > 0 else 0  # CMS médio
        
        st.write("**Resumo Frequência e CMS**")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens)}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os)}</div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)
        col4.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
        col5.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("#### Análise de criação do CMS RLP")
        
        receita_filtrada = base_receita[
            (base_receita["RLP"] == True) & 
            (base_receita["tipo_guincho"] == "Passeio")
        ]
        despesa_filtrada = base_despesa[
            (base_despesa["Script CMS"] == "RLP") & 
            (base_despesa["tipo_guincho"] == "Passeio")
        ]

        # Agrupamento por Seguradora
        receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
        receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

        despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
            "Qtd. OS's": "sum", "Despesa": "sum"
        })

        resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
        resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
        resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
        resultado_cia = resultado_cia.fillna(0)
        resultado_cia["Selecionar"] = True

        # Agrupamento por Mês
        receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
        receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

        despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
            "Qtd. OS's": "sum", "Despesa": "sum"
        })

        resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
        resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
        resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
        resultado_mes = resultado_mes.fillna(0)
        resultado_mes["Selecionar"] = True

        # Formatação para exibição
        resultado_cia_exibe = resultado_cia.copy()
        resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
        resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
        resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
        resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
        resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

        resultado_mes_exibe = resultado_mes.copy()
        resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
        resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
        resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
        resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
        resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)

        # Reordenação de colunas
        # Seguradora e frequência
        colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
        resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
        
        # Seguradora e CMS
        colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
        resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
        
        
        # Período e frequência
        colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
        resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
        
        # Período e CMS
        colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
        resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

        col1, col2 = st.columns(2)

        # Editor por seguradora
        with col1:
            st.write("**Escolha das Seguradoras para frequência**")
            resultado_cia_exibe_freq_editado = st.data_editor(
                resultado_cia_exibe_freq,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                key=f"data_editor_seguradora_rlp_freq_Passeio_rlpp"
            )

        # Editor por mês
        with col2:
            st.write("**Escolha das Seguradoras para CMS**")
            resultado_cia_exibe_cms_editado = st.data_editor(
                resultado_cia_exibe_cms,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                key=f"data_editor_seguradora_rlp_cms_Passeio_rlpp"
            )
            
        col1, col2 = st.columns(2)

        # Editor por seguradora
        with col1:
            st.write("**Escolha do período para frequência**")
            resultado_mes_exibe_freq_editado = st.data_editor(
                resultado_mes_exibe_freq,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                key=f"data_editor_periodo_rlp_freq_Passeio_rlpp"
            )

        # Editor por mês
        with col2:
            st.write("**Escolha do período para CMS**")
            resultado_mes_exibe_cms_editado = st.data_editor(
                resultado_mes_exibe_cms,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                key=f"data_editor_periodo_rlp_cms_Passeio_rlpp"
            )
        
        
        
        # Filtros aplicados
        seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
        seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
        
        periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
        periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

        receita_final_freq = receita_filtrada[
            receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
            receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
        ]
        
        despesa_final_freq = despesa_filtrada[
            despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
            despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
        ]
        despesa_final_cms = despesa_filtrada[
            despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
            despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
        ]
        
        

        # Criação das faixas
        faixa1 = despesa_final_cms[
            (despesa_final_cms["Valor Ajustado CMS"] > 0) &
            (despesa_final_cms["Valor Ajustado CMS"] <= 500)
        ]
        faixa2 = despesa_final_cms[
            (despesa_final_cms["Valor Ajustado CMS"] > 500) &
            (despesa_final_cms["Valor Ajustado CMS"] <= 800)
        ]
        faixa3 = despesa_final_cms[
            (despesa_final_cms["Valor Ajustado CMS"] > 800)
        ]

        # Calculando os valores
        col1 = faixa1["Valor Ajustado CMS"].sum() / faixa1["Qtd. OS's"].sum() if faixa1["Qtd. OS's"].sum() else 0
        col2 = faixa2["Valor Ajustado CMS"].sum() / faixa2["Qtd. OS's"].sum() if faixa2["Qtd. OS's"].sum() else 0
        col3 = faixa3["Valor Ajustado CMS"].sum() / faixa3["Qtd. OS's"].sum() if faixa3["Qtd. OS's"].sum() else 0
        col4 = faixa1["Qtd. OS's"].sum()
        col5 = faixa2["Qtd. OS's"].sum()
        col6 = faixa3["Qtd. OS's"].sum()

        # Pega os dados do parâmetro
        df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])

        # Valores padrão de LMI e Franquia
        lmi_padrao = df_lmi_franquia[
            (df_lmi_franquia["Tipo de Veículo"] == "Passeio") & 
            (df_lmi_franquia["Script"] == "RLP")
        ]["LMI (R$)"].values[0]

        franquia_padrao = df_lmi_franquia[
            (df_lmi_franquia["Tipo de Veículo"] == "Passeio") & 
            (df_lmi_franquia["Script"] == "RLP")
        ]["Franquia (R$)"].values[0]

        # Criação de um dataframe editável com os parâmetros
        df_parametros_editaveis = pd.DataFrame([{
            "LMI RLP": lmi_padrao,
            "Franquia RLP": franquia_padrao
        }])

        # Exibe a tabela para o usuário editar
        df_parametros_editado = st.data_editor(
            df_parametros_editaveis,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed"
        )

        # Recupera os valores editados
        lmi_rlp_passeio = df_parametros_editado["LMI RLP"].iloc[0]
        franquia_rlp_passeio = df_parametros_editado["Franquia RLP"].iloc[0]

        # Calculando as colunas finais
        col9 = col3 * (lmi_rlp_passeio / 1000)

        soma_qtd_os = col4 + col5 + col6
        col10 = (
            (col1 * col4) +
            (col2 * col5) +
            (col9 * col6)
        ) / soma_qtd_os if soma_qtd_os else 0

        col11 = col10 - franquia_rlp_passeio
        
        # Cálculo da frequência
        total_qtd_os = despesa_final_freq["Qtd. OS's"].sum()
        total_itens = receita_final_freq["ITENS"].sum()

        freq = (total_qtd_os * 12) / total_itens if total_itens else 0

        # Resultados
        df_resultado_faixa_cms_os = pd.DataFrame([{
            "CMS até R$500": f_valor(col1),
            "CMS entre R$500-R$800": f_valor(col2),
            "CMS acima de R$800": f_valor(col3),
            "Qtd. OS's até R$500": f_int(col4),
            "Qtd. OS's entre R$500-R$800": f_int(col5),
            "Qtd. OS's acima de R$800": f_int(col6)
        }])

        df_resultado = pd.DataFrame([{
            "CMS ajustado (CMS acima de R$ 800 * LMI / 1000)": f_valor(col9),
            "CMS Geral": f_valor(col10),
            "Resultado (CMS Geral - franquia)": f_valor(col11),
            "Resultado (Frequência)": f_perc(freq)
        }])

        # Exibindo as tabelas
        st.dataframe(df_resultado_faixa_cms_os, use_container_width=True, hide_index=True)
        st.dataframe(df_resultado, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.markdown("#### Tabela com o resultado para RLPP")
        
        freq_rlpp = freq + total_freq
        
        porc_os_troca_reparo_para_choque = total_freq/freq_rlpp
        porc_os_rlp = freq/freq_rlpp
        
        cms_rlpp = (porc_os_troca_reparo_para_choque*total_cms) + (porc_os_rlp*col11)
        
        
        
        df_resultado_rlpp = pd.DataFrame([
            {
                "Cobertura": "Troca/Reparo de Para-choque",
                "CMS s/Franquia": f_valor(total_cms),
                "%OS Totais": f_perc(porc_os_troca_reparo_para_choque),
                "Frequência": f_perc(total_freq)
            },
            {
                "Cobertura": "RLP",
                "CMS s/Franquia": f_valor(col11),
                "%OS Totais": f_perc(porc_os_rlp),
                "Frequência": f_perc(freq)
            },
            {
                "Cobertura": "RLP Premium",
                "CMS s/Franquia": f_valor(cms_rlpp),
                "%OS Totais": f_perc(1),
                "Frequência": f_perc(freq_rlpp)
            }
        ])
                                         
        st.dataframe(df_resultado_rlpp, use_container_width=True, hide_index=True)        
        
        # 🔁 Armazena os resultados no resumo geral
        resultados_totais.append({
            "Script": "RLPP",
            "Tipo Veículo": "Passeio",
            "CMS": cms_rlpp,
            "Frequência": freq_rlpp
        })
        
        
        
        st.write("")
        
        

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Troca - PC - Ok
def validacao_funcao_freq_cms_troca_pc(base_receita, base_despesa):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                ((base_receita["PARACHOQUE"] == True) | (base_receita["TROCA_DE_PARACHOQUE"] == True)) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Para-choque") & 
                (base_despesa["tipo_guincho"] == tipo) & 
                (base_despesa["OS Reparo"] == "NÃO")
            ]
            
            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
            
            

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_troca_pc_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_troca_pc_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_troca_pc_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_troca_pc_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Troca - PC",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Reparo - PC - Ok
def validacao_funcao_freq_cms_reparo_pc(base_receita, base_despesa):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["tipo_guincho"] == "Passeio"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipos_guincho = base_receita["tipo_guincho"].dropna().unique()

    # Funções de formatação
    def f_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def f_int(x):
        return f"{int(x):,}".replace(",", ".")
    
    def f_perc(x):
        return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipos_guincho:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                ((base_receita["PARACHOQUE"] == True) | (base_receita["TROCA_DE_PARACHOQUE"] == True)) & 
                (base_receita["tipo_guincho"] == tipo)
            ]
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Para-choque") & 
                (base_despesa["tipo_guincho"] == tipo) & 
                (base_despesa["OS Reparo"] == "SIM")
            ]
            
            # Agrupamento por Seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum()
            receita_cia = receita_cia.rename(columns={"ITENS": "Qtd Itens"})

            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)
            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Agrupamento por Mês
            receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
            receita_mes = receita_mes.rename(columns={"ITENS": "Qtd Itens"})

            despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum",
                "Despesa": "sum"
            })

            resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd Itens"].replace(0, np.nan)
            resultado_mes = resultado_mes.fillna(0)
            resultado_mes["Selecionar"] = True

            # Formatação para exibição
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd Itens"] = resultado_cia["Qtd Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            resultado_mes_exibe = resultado_mes.copy()
            resultado_mes_exibe["Qtd Itens"] = resultado_mes["Qtd Itens"].apply(f_int)
            resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
            resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
            resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
            resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
            
            

            # Reordenação de colunas
            # Seguradora e frequência
            colunas_ordem_cia_freq = ["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_cia_exibe_freq = resultado_cia_exibe[colunas_ordem_cia_freq]
            
            # Seguradora e CMS
            colunas_ordem_cia_cms = ["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_cia_exibe_cms = resultado_cia_exibe[colunas_ordem_cia_cms]
            
            
            # Período e frequência
            colunas_ordem_mes_freq = ["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência", "Selecionar"]
            resultado_mes_exibe_freq = resultado_mes_exibe[colunas_ordem_mes_freq]
            
            # Período e CMS
            colunas_ordem_mes_cms = ["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]
            resultado_mes_exibe_cms = resultado_mes_exibe[colunas_ordem_mes_cms]

            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha das Seguradoras para frequência**")
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_reparo_pc_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha das Seguradoras para CMS**")
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_reparo_pc_cms_{tipo}"
                )
                
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Escolha do período para frequência**")
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_reparo_pc_freq_{tipo}"
                )

            # Editor por mês
            with col2:
                st.write("**Escolha do período para CMS**")
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms,
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_reparo_pc_cms_{tipo}"
                )
            
            
            
            # Filtros aplicados
            seguradoras_selecionadas_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"]
            seguradoras_selecionadas_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"]
            
            periodos_selecionados_freq = resultado_mes.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_selecionados_cms = resultado_mes.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_filtrada[
                receita_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                receita_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            
            despesa_final_freq = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_freq) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_freq)
            ]
            despesa_final_cms = despesa_filtrada[
                despesa_filtrada["Seguradora"].isin(seguradoras_selecionadas_cms) &
                despesa_filtrada["AnoMes"].isin(periodos_selecionados_cms)
            ]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            
            
            st.divider()
            col1, col2 = st.columns(2)

            # Editor por seguradora
            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            # Editor por mês
            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)    
            
            
            
            # 🔁 Armazena os resultados no resumo geral
            resultados_totais.append({
                "Script": "Reparo - PC",
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            
            
            st.write("")
            
            

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral


# Resumo de todas as tabelas e suas coberturas
def show_validacao_freq_cms(tipo_coberturas, base_receita, base_despesa, parametros):
    st.markdown("## Resumo CMS e Frequência - Por Seguradora e Mês de Referência")

    # Dicionário com funções de validação
    funcoes_validacao = {
        "Vidros": validacao_funcao_freq_cms_vidros,
        "FLR": validacao_funcao_freq_cms_flr,
        "Higienização": validacao_funcao_freq_cms_higienizacao,
        "Cristalização": validacao_funcao_freq_cms_cristalizacao,
        "Martelinho": validacao_funcao_freq_cms_martelinho,
        "SRA": validacao_funcao_freq_cms_sra,
        "RLP": validacao_funcao_freq_cms_rlp,
        "RPS": validacao_funcao_freq_cms_rps,
        "Pneu": validacao_funcao_freq_cms_pneu,
        "ADAS": validacao_funcao_freq_cms_adas,
        "Polimento de Farol": validacao_funcao_freq_cms_polimento_farol,
        "Reparo de Parabrisa": validacao_funcao_freq_cms_reparo_parabrisa,
        "RLPP": validacao_funcao_freq_cms_rlpp,
        "Troca - PC": validacao_funcao_freq_cms_troca_pc,
        "Reparo - PC": validacao_funcao_freq_cms_reparo_pc
    }

    # Lista para armazenar os resumos de todas as coberturas
    lista_resumos = []

    for cobertura in tipo_coberturas:
        funcao = funcoes_validacao.get(cobertura)
        if funcao:
            if cobertura in ["RLP", "RPS", "ADAS", "Pneu", "RLPP"]:
                st.subheader(f"Resultados para cobertura: {cobertura}")
                df_resumo = funcao(base_receita, base_despesa, parametros)
                
            elif cobertura in ["Cristalização"]:
                df_resumo = funcao(base_receita, base_despesa)
                
            else:
                st.subheader(f"Resultados para cobertura: {cobertura}")
                df_resumo = funcao(base_receita, base_despesa)

            # Armazena o DataFrame de resumo da cobertura
            if df_resumo is not None:
                lista_resumos.append(df_resumo)

    # Junta todos os resumos em um único DataFrame
    
    if lista_resumos:
        base_resumo_geral = pd.concat(lista_resumos, ignore_index=True)
        
        return base_resumo_geral
    
    else:
        return None
    