import streamlit as st
import pandas as pd
import numpy as np

def show_resultado_script(base_receita, base_despesa, tipo_veiculo, nome_script, nome_coluna_receita):
    
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")
    
    resultados_totais = []

    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita[nome_coluna_receita] == True) &
                (base_receita["TIPO_VEICULO"] == tipo)
            ].copy()

            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == nome_script) &
                (base_despesa["TIPO_VEICULO"] == tipo)
            ].copy()

            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0

            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0

            # Exibição final
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Resumo Frequência**")
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

            with col2:
                st.write("**Resumo CMS**")
                subcol4, subcol5, subcol6 = st.columns(3)
                subcol4.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_cms)}</div>", unsafe_allow_html=True)
                subcol5.markdown(f"<div style='font-size:18px;'><b>Total Despesa</b><br>{f_valor(total_despesa_cms)}</div>", unsafe_allow_html=True)
                subcol6.markdown(f"<div style='font-size:18px;'><b>CMS</b><br>{f_valor(total_cms)}</div>", unsafe_allow_html=True)

            # Salvar resultado para o resumo geral
            resultados_totais.append({
                "Script": nome_script,
                "Tipo Veículo": tipo,
                "CMS": total_cms,
                "Frequência": total_freq
            })
            
            st.divider()
            st.markdown("#### Análise de Franquia")
            
            despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
            
            # Agrupa as OSs com franquia acima de 70%
            total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

            # Agrupa o total geral de OSs por script
            total_os_script = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "Total OSs"})
                
            # Calcula o total geral de OSs
            total_geral_os = total_os_script["Total OSs"].sum()

            # Cria a coluna de representatividade (%)
            total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

            # Junta os dois dataframes
            total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
            
            # Cria a coluna de representatividade (%) de franquia acima de 70% 
            total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
            
            # Agrupa os valores da franquia para realizar a representatividade da franquia por script
            total_valor_franquia = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Franquia Ajustada": "sum"})

            # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
            total_valor_negociado = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Valor Ajustado CMS": "sum"})

            # Junta os dois dataframes
            total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
            total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
            
            # Exibe no Streamlit
            total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
            
            # Ordena do maior para o menor
            total_script = total_script.sort_values(by="Total OSs", ascending=False)
            
            total_script = total_script.copy()
            
            total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
            total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
            
            total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
            total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
            
            
            total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
            total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
            total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
            
            st.dataframe(total_script, hide_index=True)            

    df_resumo_geral = pd.DataFrame(resultados_totais)
    return df_resumo_geral

# Vidros
def validacao_funcao_freq_cms_vidros(base_receita, base_despesa):
    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["TIPO_VEICULO"] != "Moto"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

    # Funções auxiliares de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Cria a coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)
    
    df_vidros = show_resultado_script(base_receita, base_despesa, tipo_veiculo, nome_script="Vidros", nome_coluna_receita="VIDROS")
    
    return df_vidros
        
# FLR
def validacao_funcao_freq_cms_flr(base_receita, base_despesa):

    # ✅ Ordem personalizada dos tipos de guincho
    ordem_tipo_veiculo = ["Auto", "Moto", "Carga"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipo_veiculo_disponivel = base_receita["TIPO_VEICULO"].dropna().unique()
    tipo_veiculo = [tipo for tipo in ordem_tipo_veiculo if tipo in tipo_veiculo_disponivel]

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

    df_flr = show_resultado_script(base_receita, base_despesa, tipo_veiculo, nome_script="FLR", nome_coluna_receita="FLR")
    
    return df_flr 

# Higienização
def validacao_funcao_freq_cms_higienizacao(base_receita, base_despesa):
    # ❌ Filtra apenas os registros de guincho tipo "Auto"
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"]
    base_despesa = base_despesa[base_despesa["TIPO_VEICULO"] == "Auto"]
    
    # 🔄 Tipos de guincho disponíveis após o filtro
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()
    
    # Cria coluna AnoMes em ambas as bases
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"], errors="coerce").dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"], errors="coerce").dt.to_period("M").astype(str)

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):
            
            # ✅ Garante que valores nulos sejam tratados corretamente
            despesa_filtrada = base_despesa[
                (base_despesa["TIPO_VEICULO"] == tipo) & 
                (base_despesa["Script CMS"] == "Higienização")
            ]

            # Agrupamento por período apenas da despesa
            resultado_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
                "Qtd. OS's": "sum", 
                "Despesa": "sum"
            })

            # Cálculo das métricas
            resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
            resultado_mes["Frequência"] = np.nan  # Não há mais Qtd. Itens para calcular
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

# Cristalização
def validacao_funcao_freq_cms_cristalizacao(base_receita, base_despesa):
    
    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []
    
    # 🔁 Armazena os resultados no resumo geral
    resultados_totais.append({
        "Script": "Cristalização",
        "Tipo Veículo": "Auto",
        "CMS": 115,
        "Frequência": 0.0036 
    })
    
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Martelinho
def validacao_funcao_freq_cms_martelinho(base_receita, base_despesa):

    # ❌ Filtra apenas os registros do tipo "Auto"
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"]
    
    # 🔄 Atualiza os tipos disponíveis após o filtro
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

    df_martelinho = show_resultado_script(base_receita, base_despesa, tipo_veiculo, nome_script="Martelinho", nome_coluna_receita="MARTELINHO")
    
    return df_martelinho

# SRA
def validacao_funcao_freq_cms_sra(base_receita, base_despesa):
    # Filtra só registros tipo "Auto"
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"].copy()
    
    # Atualiza os tipos disponíveis (após filtro)
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

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

    df_sra = show_resultado_script(base_receita, base_despesa, tipo_veiculo, nome_script="SRA", nome_coluna_receita="SRA")
    
    return df_sra

# RLP
def validacao_funcao_freq_cms_rlp(base_receita, base_despesa, parametros):
    
    # ✅ Ordem personalizada
    ordem_tipo_veiculo = ["Auto", "Moto", "Carga"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipo_veiculo_disponivel = base_receita["TIPO_VEICULO"].dropna().unique()
    tipo_veiculo = [tipo for tipo in ordem_tipo_veiculo if tipo in tipo_veiculo_disponivel]
    
    # Funções auxiliares
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes para as duas bases
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)
    
    nome_coluna_receita = "RLP"
    nome_script = "RLP"

    # Obter o valor de LMI para Auto e Script "RLP", caso necessário
    lmi_rlp_auto = None
    if "Auto" in tipo_veiculo:
        df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
        filtro_auto_rlp = (df_lmi_franquia["Tipo de Veículo"] == "Auto") & (df_lmi_franquia["Script"] == "RLP")
        if not df_lmi_franquia[filtro_auto_rlp].empty:
            lmi_rlp_auto = df_lmi_franquia[filtro_auto_rlp]["LMI (R$)"].values[0]
            
    # Lista para armazenar os resultados por tipo de veículo
    resultados_totais = []
    
    # Processamento por tipo de veículo
    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):
            if tipo == "Auto" and lmi_rlp_auto == 1500:
                
                receita_filtrada = base_receita[
                    (base_receita[nome_coluna_receita] == True) &
                    (base_receita["TIPO_VEICULO"] == tipo)
                ].copy()

                receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

                despesa_filtrada = base_despesa[
                    (base_despesa["Script CMS"] == nome_script) &
                    (base_despesa["TIPO_VEICULO"] == tipo)
                ].copy()

                despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

                # Agrupamento por seguradora
                receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
                despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

                resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
                resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
                resultado_cia = resultado_cia.fillna(0)
                resultado_cia["Selecionar"] = True

                # Interface para selecionar seguradoras
                resultado_cia_exibe = resultado_cia.copy()
                resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
                resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
                resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
                resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
                resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

                col1, col2 = st.columns(2)
                with col1:
                    resultado_cia_exibe_freq_editado = st.data_editor(
                        resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                    )
                with col2:
                    resultado_cia_exibe_cms_editado = st.data_editor(
                        resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                    )

                # Filtragem das seguradoras
                segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
                segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

                receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
                despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
                despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

                # Tabelas por mês
                receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

                def gerar_resultado_mes(despesa_mes, label):
                    df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                    resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                    resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                    resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                    resultado = resultado.fillna(0)
                    resultado["Selecionar"] = True
                    return resultado

                resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
                resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

                # Interfaces de seleção por período
                def formatar_resultado_exibe(df):
                    df_exibe = df.copy()
                    df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                    df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                    df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                    df_exibe["CMS"] = df["CMS"].apply(f_valor)
                    df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                    return df_exibe

                col1, col2 = st.columns(2)
                with col1:
                    resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                    resultado_mes_exibe_freq_editado = st.data_editor(
                        resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                    )
                with col2:
                    resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                    resultado_mes_exibe_cms_editado = st.data_editor(
                        resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                    )

                # Filtro final por período
                periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
                periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

                receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
                despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
                despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]
                

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
                
                # LMI específico para Auto e Script "RLP"
                lmi_rlp_auto = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Auto") & 
                    (df_lmi_franquia["Script"] == "RLP")
                ]["LMI (R$)"].values[0]

                # Calculando as colunas finais
                col9 = col3 * (lmi_rlp_auto / 1000)
                
                # Calculando a nova col10 como a média ponderada das faixas de CMS
                soma_qtd_os = col4 + col5 + col6
                col10 = (
                    (col1 * col4) +
                    (col2 * col5) +
                    (col9 * col6)
                ) / soma_qtd_os if soma_qtd_os else 0

                franquia_rlp_auto = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Auto") & 
                    (df_lmi_franquia["Script"] == "RLP")
                ]["Franquia (R$)"].values[0]
                
                # Resultado final: col10 - franquia
                col11 = col10 - franquia_rlp_auto

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
                    "LMI RLP": f_valor(lmi_rlp_auto),
                    "Franquia RLP": f_valor(franquia_rlp_auto),
                    "CMS ajustado (CMS acima de R$ 800 * LMI / 1000)": f_valor(col9),
                    "CMS Geral": f_valor(col10),
                    "Resultado (CMS Geral - Franquia)": f_valor(col11)
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
                    
                # 🔁 Armazena os resultados no resumo geral
                resultados_totais.append({
                    "Script": "RLP",
                    "Tipo Veículo": "Auto",
                    "CMS": col11,
                    "Frequência": freq
                })
                
                st.divider()
                st.markdown("#### Análise de Franquia")
                
                despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
                
                # Agrupa as OSs com franquia acima de 70%
                total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

                # Agrupa o total geral de OSs por script
                total_os_script = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "Total OSs"})
                    
                # Calcula o total geral de OSs
                total_geral_os = total_os_script["Total OSs"].sum()

                # Cria a coluna de representatividade (%)
                total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

                # Junta os dois dataframes
                total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
                
                # Cria a coluna de representatividade (%) de franquia acima de 70% 
                total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
                
                # Agrupa os valores da franquia para realizar a representatividade da franquia por script
                total_valor_franquia = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Franquia Ajustada": "sum"})

                # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
                total_valor_negociado = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Valor Ajustado CMS": "sum"})

                # Junta os dois dataframes
                total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
                total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
                
                # Exibe no Streamlit
                total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
                
                # Ordena do maior para o menor
                total_script = total_script.sort_values(by="Total OSs", ascending=False)
                
                total_script = total_script.copy()
                
                total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
                total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
                
                total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
                total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
                
                
                total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
                total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
                total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
                
                st.dataframe(total_script, hide_index=True)   

            else:
                
                receita_filtrada = base_receita[
                    (base_receita[nome_coluna_receita] == True) &
                    (base_receita["TIPO_VEICULO"] == tipo)
                ].copy()

                receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

                despesa_filtrada = base_despesa[
                    (base_despesa["Script CMS"] == nome_script) &
                    (base_despesa["TIPO_VEICULO"] == tipo)
                ].copy()

                despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

                # Agrupamento por seguradora
                receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
                despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

                resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
                resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
                resultado_cia = resultado_cia.fillna(0)
                resultado_cia["Selecionar"] = True

                # Interface para selecionar seguradoras
                resultado_cia_exibe = resultado_cia.copy()
                resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
                resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
                resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
                resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
                resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

                col1, col2 = st.columns(2)
                with col1:
                    resultado_cia_exibe_freq_editado = st.data_editor(
                        resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                    )
                with col2:
                    resultado_cia_exibe_cms_editado = st.data_editor(
                        resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                    )

                # Filtragem das seguradoras
                segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
                segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

                receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
                despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
                despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

                # Tabelas por mês
                receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

                def gerar_resultado_mes(despesa_mes, label):
                    df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                    resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                    resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                    resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                    resultado = resultado.fillna(0)
                    resultado["Selecionar"] = True
                    return resultado

                resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
                resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

                # Interfaces de seleção por período
                def formatar_resultado_exibe(df):
                    df_exibe = df.copy()
                    df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                    df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                    df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                    df_exibe["CMS"] = df["CMS"].apply(f_valor)
                    df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                    return df_exibe

                col1, col2 = st.columns(2)
                with col1:
                    resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                    resultado_mes_exibe_freq_editado = st.data_editor(
                        resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                        key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                    )
                with col2:
                    resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                    resultado_mes_exibe_cms_editado = st.data_editor(
                        resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                        column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                        hide_index=True,
                        disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                        key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                    )

                # Filtro final por período
                periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
                periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

                receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
                despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
                despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

                total_itens_freq = receita_final_freq["ITENS"].sum()
                total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
                total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0

                total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
                total_despesa_cms = despesa_final_cms["Despesa"].sum()
                total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0

                # Exibição final
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Resumo Frequência**")
                    subcol1, subcol2, subcol3 = st.columns(3)
                    subcol1.markdown(f"<div style='font-size:18px;'><b>Total Itens</b><br>{f_int(total_itens_freq)}</div>", unsafe_allow_html=True)
                    subcol2.markdown(f"<div style='font-size:18px;'><b>Total OS's</b><br>{f_int(total_os_freq)}</div>", unsafe_allow_html=True)
                    subcol3.markdown(f"<div style='font-size:18px;'><b>Frequência</b><br>{f_perc(total_freq)}</div>", unsafe_allow_html=True)

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
                
                st.divider()
                st.markdown("#### Análise de Franquia")
                
                despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
                
                # Agrupa as OSs com franquia acima de 70%
                total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

                # Agrupa o total geral de OSs por script
                total_os_script = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "Total OSs"})
                    
                # Calcula o total geral de OSs
                total_geral_os = total_os_script["Total OSs"].sum()

                # Cria a coluna de representatividade (%)
                total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

                # Junta os dois dataframes
                total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
                
                # Cria a coluna de representatividade (%) de franquia acima de 70% 
                total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
                
                # Agrupa os valores da franquia para realizar a representatividade da franquia por script
                total_valor_franquia = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Franquia Ajustada": "sum"})

                # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
                total_valor_negociado = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Valor Ajustado CMS": "sum"})

                # Junta os dois dataframes
                total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
                total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
                
                # Exibe no Streamlit
                total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
                
                # Ordena do maior para o menor
                total_script = total_script.sort_values(by="Total OSs", ascending=False)
                
                total_script = total_script.copy()
                
                total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
                total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
                
                total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
                total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
                
                
                total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
                total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
                total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
                
                st.dataframe(total_script, hide_index=True)   
                
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# RPS
def validacao_funcao_freq_cms_rps(base_receita, base_despesa, parametros):
    
    # ✅ Ordem personalizada
    ordem_tipo_veiculo = ["Auto", "Moto", "Carga"]

    # Filtra e ordena os tipos de guincho conforme a ordem personalizada
    tipo_veiculo_disponivel = base_receita["TIPO_VEICULO"].dropna().unique()
    tipo_veiculo = [tipo for tipo in ordem_tipo_veiculo if tipo in tipo_veiculo_disponivel]

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)
    
    nome_coluna_receita = "RPS"
    nome_script = "RPS"

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    # Tipos de guincho disponíveis
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()
    
    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita[nome_coluna_receita] == True) &
                (base_receita["TIPO_VEICULO"] == tipo)
            ].copy()

            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == nome_script) &
                (base_despesa["TIPO_VEICULO"] == tipo)
            ].copy()

            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa"].sum()
            total_cms = total_despesa_cms / total_os_cms if total_os_cms > 0 else 0
            
            if tipo in "Auto":
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
                    (df_lmi_franquia["Tipo de Veículo"] == "Auto") &
                    (df_lmi_franquia["Script"] == "RPS")
                ]["LMI (R$)"].values[0]

                franquia_rps = df_lmi_franquia[
                    (df_lmi_franquia["Tipo de Veículo"] == "Auto") &
                    (df_lmi_franquia["Script"] == "RPS")
                ]["Franquia (R$)"].values[0]
                
                dados_rps2["LMI"] = lmi_rps
                dados_rps2["Franquia"] = franquia_rps
                
                dados_rps2["Despesa"] = np.minimum(
                    dados_rps2["VALOR NEGOCIADO"] - dados_rps2["Franquia"],
                    dados_rps2["LMI"]
                )
                
                despesa_media_cotacao = dados_rps2["Despesa"].mean().__round__(2)
                
                despesa_agravada = despesa_media_cotacao * 0.1 + total_cms * 0.9
                
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
                
                st.divider()
                st.markdown("#### Análise de Franquia")
                
                despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
                
                # Agrupa as OSs com franquia acima de 70%
                total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

                # Agrupa o total geral de OSs por script
                total_os_script = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "Total OSs"})
                    
                # Calcula o total geral de OSs
                total_geral_os = total_os_script["Total OSs"].sum()

                # Cria a coluna de representatividade (%)
                total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

                # Junta os dois dataframes
                total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
                
                # Cria a coluna de representatividade (%) de franquia acima de 70% 
                total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
                
                # Agrupa os valores da franquia para realizar a representatividade da franquia por script
                total_valor_franquia = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Franquia Ajustada": "sum"})

                # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
                total_valor_negociado = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Valor Ajustado CMS": "sum"})

                # Junta os dois dataframes
                total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
                total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
                
                # Exibe no Streamlit
                total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
                
                # Ordena do maior para o menor
                total_script = total_script.sort_values(by="Total OSs", ascending=False)
                
                total_script = total_script.copy()
                
                total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
                total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
                
                total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
                total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
                
                
                total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
                total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
                total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
                
                st.dataframe(total_script, hide_index=True)
                
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
                
                st.divider()
                st.markdown("#### Análise de Franquia")
                
                despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
                
                # Agrupa as OSs com franquia acima de 70%
                total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

                # Agrupa o total geral de OSs por script
                total_os_script = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Qtd. OS's": "sum"}) \
                    .rename(columns={"Qtd. OS's": "Total OSs"})
                    
                # Calcula o total geral de OSs
                total_geral_os = total_os_script["Total OSs"].sum()

                # Cria a coluna de representatividade (%)
                total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

                # Junta os dois dataframes
                total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
                
                # Cria a coluna de representatividade (%) de franquia acima de 70% 
                total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
                
                # Agrupa os valores da franquia para realizar a representatividade da franquia por script
                total_valor_franquia = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Franquia Ajustada": "sum"})

                # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
                total_valor_negociado = despesa_final_cms \
                    .groupby("Script Franquia", as_index=False) \
                    .agg({"Valor Ajustado CMS": "sum"})

                # Junta os dois dataframes
                total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
                total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
                
                # Exibe no Streamlit
                total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
                
                # Ordena do maior para o menor
                total_script = total_script.sort_values(by="Total OSs", ascending=False)
                
                total_script = total_script.copy()
                
                total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
                total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
                
                total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
                total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
                
                
                total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
                total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
                total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
                
                st.dataframe(total_script, hide_index=True)
                
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Pneu
def validacao_funcao_freq_cms_pneu(base_receita, base_despesa, parametros):
    
     # ✅ Ordem personalizada
    ordem_tipo_veiculo = ["Auto", "Moto", "Carga"]

    # Filtra e ordena os tipos de veículo conforme a ordem personalizada
    tipo_veiculo_disponivel = base_receita["TIPO_VEICULO"].dropna().unique()
    tipos_veiculo = [tipo for tipo in ordem_tipo_veiculo if tipo in tipo_veiculo_disponivel]

    # Funções de formatação
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    # Criação da coluna AnoMes
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)
    base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)
    
    nome_coluna_receita = "PNEU"
    nome_script = "Pneu"

    for tipo in tipos_veiculo:
        with st.expander(f"▶ {tipo}"):

            receita_filtrada = base_receita[
                (base_receita[nome_coluna_receita] == True) &
                (base_receita["TIPO_VEICULO"] == tipo)
            ].copy()

            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            despesa_filtrada = base_despesa[
                (base_despesa["TEM_PNEU"] == True) &
                (base_despesa["TIPO_VEICULO"] == tipo)
            ].copy()

            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa Pneu": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa Pneu"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa Pneu"] = resultado_cia["Despesa Pneu"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa Pneu", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa Pneu", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa Pneu": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa Pneu"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa Pneu"] = df["Despesa Pneu"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa Pneu", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa Pneu", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

            # Resumo final frequência
            total_itens_freq = receita_final_freq["ITENS"].sum()
            total_os_freq = despesa_final_freq["Qtd. OS's"].sum()
            total_freq = (total_os_freq * 12) / total_itens_freq if total_itens_freq > 0 else 0
            
            # Resumo final CMS
            total_os_cms = despesa_final_cms["Qtd. OS's"].sum()
            total_despesa_cms = despesa_final_cms["Despesa Pneu"].sum()
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
                
            st.divider()
            st.markdown("#### Análise de Franquia")
            
            despesa_final_cms["Script Franquia"] = "Pneu"
                
            despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia (R$) - Pneu"]/despesa_final_cms["Valor Ajustado CMS"]
            
            # Agrupa as OSs com franquia acima de 70%
            total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

            # Agrupa o total geral de OSs por script
            total_os_script = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "Total OSs"})
                
            # Calcula o total geral de OSs
            total_geral_os = total_os_script["Total OSs"].sum()

            # Cria a coluna de representatividade (%)
            total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

            # Junta os dois dataframes
            total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
            
            # Cria a coluna de representatividade (%) de franquia acima de 70% 
            total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
            
            # Agrupa os valores da franquia para realizar a representatividade da franquia por script
            total_valor_franquia = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Franquia (R$) - Pneu": "sum"})

            # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
            total_valor_negociado = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Valor Ajustado CMS": "sum"})

            # Junta os dois dataframes
            total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
            total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia (R$) - Pneu"]/total_valor_script["Valor Ajustado CMS"]
            
            # Exibe no Streamlit
            total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
            
            # Ordena do maior para o menor
            total_script = total_script.sort_values(by="Total OSs", ascending=False)
            
            total_script = total_script.copy()
            
            total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
            total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
            
            total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
            total_script["Franquia (R$) - Pneu"] = total_script["Franquia (R$) - Pneu"].apply(f_valor)
            
            
            total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
            total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
            total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
            
            st.dataframe(total_script, hide_index=True)
    
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)
    
    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# ADAS
def validacao_funcao_freq_cms_adas(base_receita, base_despesa, parametros):
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")

    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"]
    base_receita["AnoMes"] = pd.to_datetime(base_receita["DAT_REFERENCIA_MODIF"]).dt.to_period("M").astype(str)

    receita_filtrada = base_receita[base_receita["VIDROS"] == True].copy()
    receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

    seguradoras_com_adas = receita_filtrada[receita_filtrada["VEICULO_ADAS"] == "Sim"]["Seguradora"].unique()
    receita_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(seguradoras_com_adas)]

    with st.expander("▶ Auto"):
        st.markdown("### 🔎 Filtros")

        total_por_seguradora = receita_filtrada.groupby("Seguradora")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Total de Itens"})
        adas_por_seguradora = receita_filtrada[receita_filtrada["VEICULO_ADAS"] == "Sim"].groupby("Seguradora")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Itens com ADAS"})
        tabela_seguradora = pd.merge(total_por_seguradora, adas_por_seguradora, on="Seguradora", how="left")
        tabela_seguradora["Itens com ADAS"] = tabela_seguradora["Itens com ADAS"].fillna(0)
        tabela_seguradora["Proporção com ADAS"] = tabela_seguradora["Itens com ADAS"] / tabela_seguradora["Total de Itens"]

        tabela_seguradora["Total de Itens"] = tabela_seguradora["Total de Itens"].apply(f_int)
        tabela_seguradora["Itens com ADAS"] = tabela_seguradora["Itens com ADAS"].apply(f_int)
        tabela_seguradora["Proporção com ADAS"] = tabela_seguradora["Proporção com ADAS"].apply(f_perc)
        tabela_seguradora["Selecionar"] = True

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Por Seguradora")
            tabela_seguradora_editado = st.data_editor(
                tabela_seguradora,
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                use_container_width=True,
                hide_index=True,
                disabled=["Seguradora", "Total de Itens", "Itens com ADAS", "Proporção com ADAS"]
            )

        seguradoras_selecionadas = tabela_seguradora_editado.loc[
            tabela_seguradora_editado["Selecionar"], "Seguradora"
        ].tolist()

        receita_filtrada_mes = receita_filtrada[receita_filtrada["Seguradora"].isin(seguradoras_selecionadas)]

        total_por_mes = receita_filtrada_mes.groupby("AnoMes")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Total de Itens"})
        adas_por_mes = receita_filtrada_mes[receita_filtrada_mes["VEICULO_ADAS"] == "Sim"].groupby("AnoMes")["ITENS"].sum().reset_index().rename(columns={"ITENS": "Itens com ADAS"})
        tabela_mes = pd.merge(total_por_mes, adas_por_mes, on="AnoMes", how="left")
        tabela_mes["Itens com ADAS"] = tabela_mes["Itens com ADAS"].fillna(0)
        tabela_mes["Proporção com ADAS"] = tabela_mes["Itens com ADAS"] / tabela_mes["Total de Itens"]

        tabela_mes["AnoMes_dt"] = pd.to_datetime(tabela_mes["AnoMes"])
        tabela_mes = tabela_mes.sort_values("AnoMes_dt").reset_index(drop=True)

        if len(tabela_mes) >= 2:
            crescimento_medio_prop = (tabela_mes["Proporção com ADAS"].iloc[-1] - tabela_mes["Proporção com ADAS"].iloc[0]) / (len(tabela_mes) - 1)
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
                projecoes.append({"AnoMes": novo_mes_str, "Total de Itens": round(total_itens_atual), "Itens com ADAS": round(itens_adas_atual), "Proporção com ADAS": prop_adas_atual})
            df_proj = pd.DataFrame(projecoes)
        else:
            df_proj = pd.DataFrame(columns=["AnoMes", "Total de Itens", "Itens com ADAS", "Proporção com ADAS"])

        tabela_real = tabela_mes.drop(columns=["AnoMes_dt"]).copy()

        tabela_real["Total de Itens"] = tabela_real["Total de Itens"].apply(f_int)
        tabela_real["Itens com ADAS"] = tabela_real["Itens com ADAS"].apply(f_int)
        tabela_real["Proporção com ADAS"] = tabela_real["Proporção com ADAS"].apply(f_perc)
        tabela_real["Selecionar"] = True
        
        df_proj["Total de Itens"] = df_proj["Total de Itens"].apply(f_int)
        df_proj["Itens com ADAS"] = df_proj["Itens com ADAS"].apply(f_int)
        df_proj["Proporção com ADAS"] = df_proj["Proporção com ADAS"].apply(f_perc)

        with col2:
            st.markdown("#### 📆 Por Mês (Histórico)")
            tabela_mes_final_editado = st.data_editor(
                    tabela_real,
                    column_config={
                        "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                    },
                    use_container_width=True,
                    hide_index=True,
                    disabled=["AnoMes", "Total de Itens", "Itens com ADAS", "Proporção com ADAS"]
                )
            
            st.markdown("#### 📈 Projeção Futura")
            st.dataframe(df_proj, hide_index=True)

        meses_selecionados = tabela_mes_final_editado.loc[tabela_mes_final_editado["Selecionar"], "AnoMes"]

        base_despesa["AnoMes"] = pd.to_datetime(base_despesa["Data Realização OS"]).dt.to_period("M").astype(str)

        receita_filtrada = receita_filtrada[
            receita_filtrada["AnoMes"].isin(meses_selecionados) &
            receita_filtrada["Seguradora"].isin(seguradoras_selecionadas)
        ]
        despesa_filtrada = base_despesa[
            (base_despesa["AnoMes"].isin(meses_selecionados)) &
            (base_despesa["Seguradora"].isin(seguradoras_selecionadas)) &
            (base_despesa["TIPO_VEICULO"] == 'Auto') &
            (base_despesa["Script Franquia"] == 'Parabrisa') &
            (base_despesa["VEICULO_ADAS"] == 'Sim')
        ]

        total_itens = receita_filtrada["ITENS"].sum() / len(meses_selecionados)
        total_itens_adas = receita_filtrada[receita_filtrada["VEICULO_ADAS"] == "Sim"]["ITENS"].sum() / len(meses_selecionados)
        prop_geral_itens_adas = total_itens_adas / total_itens if total_itens > 0 else 0

        qtd_os_com_reparo = despesa_filtrada[despesa_filtrada["OS Reparo"] == "SIM"]["Qtd. OS's"].sum() / len(meses_selecionados)
        qtd_os_sem_reparo = despesa_filtrada[despesa_filtrada["OS Reparo"] == "NÃO"]["Qtd. OS's"].sum() / len(meses_selecionados)

        df_lmi_franquia = pd.DataFrame(parametros["lmi_franquia"])
        franquia_adas = df_lmi_franquia[(df_lmi_franquia["Tipo de Veículo"] == 'Auto') & (df_lmi_franquia["Script"] == "ADAS")]["Franquia (R$)"].values[0]

        col_input1, col_input2 = st.columns(2)
        valor_franquia_padrao = col_input1.number_input("Valor CMS com Franquia", min_value=0.0, value=450.0, step=50.0)
        valor_franquia_adas = col_input2.number_input("Valor da franquia ADAS (padrão)", min_value=0.0, value=float(franquia_adas), step=50.0)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total médio de itens por mês", f_int(total_itens))
        col2.metric("Total médio de itens ADAS por mês", f_int(total_itens_adas))
        col3.metric("Proporção de Itens de ADAS", f_perc(prop_geral_itens_adas))
        col4.metric("Qtd. média OS com reparo/mês", f_int(qtd_os_com_reparo))
        col5.metric("Qtd. média OS sem reparo/mês", f_int(qtd_os_sem_reparo))

        considerar_reparo = st.toggle("Considerar Reparo de PB?", value=True)
        total_os = (qtd_os_com_reparo + qtd_os_sem_reparo) if considerar_reparo else qtd_os_sem_reparo

        total_cms = valor_franquia_padrao - valor_franquia_adas
        total_freq = (total_os * 12) / total_itens_adas if total_itens_adas > 0 else 0

        col1b, col2b, col3b = st.columns(3)
        col1b.metric("Total de OS considerado", f_int(total_os))
        col2b.metric("Valor de CMS", f_valor(total_cms))
        col3b.metric("Frequência anual estimada", f_perc(total_freq))

        df_resumo_geral = pd.DataFrame([{
            "Script": "ADAS",
            "Tipo Veículo": "Auto",
            "CMS": total_cms,
            "Frequência": total_freq
        }])

    return df_resumo_geral

# Polimento de Farol
def validacao_funcao_freq_cms_polimento_farol(base_receita, base_despesa):

    # Filtra só registros tipo "Auto"
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"].copy()
    
    # Atualiza os tipos disponíveis (após filtro)
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

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
    
    nome_coluna_receita = "FLR"
    nome_script = "Polimento de Farol"

    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):
            
            receita_filtrada = base_receita[
                (base_receita[nome_coluna_receita] == True) & 
                (base_receita["TIPO_VEICULO"] == tipo)
            ].copy()

            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "FLR") & 
                (base_despesa["TIPO_VEICULO"] == tipo) & 
                (base_despesa["Polidor de Farol"] == "SIM")
            ].copy()

            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

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
            
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Reparo de PB
def validacao_funcao_freq_cms_reparo_parabrisa(base_receita, base_despesa):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["TIPO_VEICULO"] != "Moto"].copy()

    # 🔄 Atualiza os tipos disponíveis
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

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
    
    nome_coluna_receita = "VIDROS"
    nome_script = "Reparo de Parabrisa"

    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                (base_receita["VIDROS"] == True) & 
                (base_receita["TIPO_VEICULO"] == tipo)
            ].copy()
            
            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})
            
            despesa_filtrada = base_despesa[
                (base_despesa["Script Franquia"] == "Parabrisa") & 
                (base_despesa["TIPO_VEICULO"] == tipo) & 
                (base_despesa["OS Reparo"] == "SIM")
            ].copy()
            
            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

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
            
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# RLPP
def validacao_funcao_freq_cms_rlpp(base_receita, base_despesa, parametros):

    # ✅ Remove "Moto" e evita SettingWithCopyWarning
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"].copy()

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
    
    with st.expander("▶ Auto"):
        
        # Tabela de referência de troca e reparo de Para-choque - Tokio
        st.markdown("#### Análise Troca/Reparo de Para-choque Tokio")

        # Filtragem das bases
        receita_filtrada = base_receita[
            (base_receita["TROCA_DE_PARACHOQUE"] == True) & 
            (base_receita["TIPO_VEICULO"] == "Auto") & 
            (base_receita["SEGURADORA"].str.contains("TOKIO", na=False))
        ]
        despesa_filtrada = base_despesa[
            (base_despesa["Script CMS"] == "Para-choque") & 
            (base_despesa["TIPO_VEICULO"] == "Auto") & 
            (base_despesa["Seguradora"].str.contains("TOKIO", na=False))
        ]
    

        # Agrupamento por Mês
        receita_mes = receita_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum()
        receita_mes = receita_mes.rename(columns={"ITENS": "Qtd. Itens"})

        despesa_mes = despesa_filtrada.groupby("AnoMes", as_index=False).agg({
            "Qtd. OS's": "sum",
            "Despesa": "sum"
        })

        resultado_mes = pd.merge(receita_mes, despesa_mes, on="AnoMes", how="left").fillna(0)
        resultado_mes["CMS"] = resultado_mes["Despesa"] / resultado_mes["Qtd. OS's"].replace(0, np.nan)
        resultado_mes["Frequência"] = (resultado_mes["Qtd. OS's"] * 12) / resultado_mes["Qtd. Itens"].replace(0, np.nan)
        resultado_mes = resultado_mes.fillna(0)
        resultado_mes["Selecionar"] = True

        resultado_mes_exibe = resultado_mes.copy()
        resultado_mes_exibe["Qtd. Itens"] = resultado_mes["Qtd. Itens"].apply(f_int)
        resultado_mes_exibe["Qtd. OS's"] = resultado_mes["Qtd. OS's"].apply(f_int)
        resultado_mes_exibe["Despesa"] = resultado_mes["Despesa"].apply(f_valor)
        resultado_mes_exibe["CMS"] = resultado_mes["CMS"].apply(f_valor)
        resultado_mes_exibe["Frequência"] = resultado_mes["Frequência"].apply(f_perc)
        
        
        # Período e frequência
        colunas_ordem_mes = ["AnoMes", "Qtd. Itens", "Qtd. OS's", "Despesa", "Frequência", "CMS", "Selecionar"]
        resultado_mes_exibe_ajust = resultado_mes_exibe[colunas_ordem_mes]
            
        
        st.write("**Escolha do período para frequência e CMS**")
        resultado_mes_exibe_editado = st.data_editor(
            resultado_mes_exibe_ajust,
            column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
            use_container_width=True,
            hide_index=True,
            disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Despesa", "Frequência", "CMS"],
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
        
        tipo = "Auto"
        nome_coluna_receita = "RLP"
        nome_script = "RLP - Ajust. RLPP"
        
        
        receita_filtrada = base_receita[
            (base_receita[nome_coluna_receita] == True) &
            (base_receita["TIPO_VEICULO"] == tipo)
        ].copy()

        receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

        despesa_filtrada = base_despesa[
            (base_despesa["Script CMS"] == "RLP") &
            (base_despesa["TIPO_VEICULO"] == tipo)
        ].copy()

        despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

        # Agrupamento por seguradora
        receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
        despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
        resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

        resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
        resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
        resultado_cia = resultado_cia.fillna(0)
        resultado_cia["Selecionar"] = True

        # Interface para selecionar seguradoras
        resultado_cia_exibe = resultado_cia.copy()
        resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
        resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
        resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
        resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
        resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

        col1, col2 = st.columns(2)
        with col1:
            resultado_cia_exibe_freq_editado = st.data_editor(
                resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                hide_index=True,
                disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
            )
        with col2:
            resultado_cia_exibe_cms_editado = st.data_editor(
                resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                hide_index=True,
                disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
            )

        # Filtragem das seguradoras
        segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
        segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

        receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
        despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
        despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

        # Tabelas por mês
        receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

        def gerar_resultado_mes(despesa_mes, label):
            df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
            resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
            resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
            resultado = resultado.fillna(0)
            resultado["Selecionar"] = True
            return resultado

        resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
        resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

        # Interfaces de seleção por período
        def formatar_resultado_exibe(df):
            df_exibe = df.copy()
            df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
            df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
            df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
            df_exibe["CMS"] = df["CMS"].apply(f_valor)
            df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
            return df_exibe

        col1, col2 = st.columns(2)
        with col1:
            resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
            resultado_mes_exibe_freq_editado = st.data_editor(
                resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                hide_index=True,
                disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
            )
        with col2:
            resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
            resultado_mes_exibe_cms_editado = st.data_editor(
                resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                hide_index=True,
                disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
            )

        # Filtro final por período
        periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
        periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

        receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
        despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
        despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]
        
        

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
            (df_lmi_franquia["Tipo de Veículo"] == "Auto") & 
            (df_lmi_franquia["Script"] == "RLP")
        ]["LMI (R$)"].values[0]

        franquia_padrao = df_lmi_franquia[
            (df_lmi_franquia["Tipo de Veículo"] == "Auto") & 
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
        
        st.markdown("#### Análise Peças Complementares ao Parachoque")
        st.write('Fonte: Planilha enviada pelo CECOM')
        
        # Dados fornecidos
        dados = {
            "Cobertura de Complementos": [
                "Emblemas/\nFrisos",
                "Grade de Parachoque (ATG atende)",
                "Grade Radiador (MG trabalha)",
                "Moldura de Farol Auxiliar (ATG atende)",
                "Guia Para-choque (ATG atende)",
                "Moldura plama (ATG atende)",
                "Spoiler (Parachoque dianteiro inferior)",
                "Polaina (Parachoque traseiro)",
                "Overbumper",
                "Cobertura de Complementos"
            ],
            "OS Anual": [294, 220, 220, 220, 294, 294, 147, 73, 7, 734],
            "Frequência Anual": ["0,8%", "0,6%", "0,6%", "0,6%", "0,8%", "0,8%", "0,4%", "0,2%", "0,0%", "1,9%"],
            "CMS Cheio": ["R$ 143,85", "R$ 171,22", "R$ 271,76", "R$ 69,28", "R$ 48,03", "R$ 270,00", "R$ 420,00", "R$ 300,00", "R$ 1.200,00", "R$ 464,43"],
            "Franquia Estimada": ["R$ 50,35", "R$ 59,93", "R$ 95,12", "R$ 24,25", "R$ 16,81", "R$ 94,50", "R$ 147,00", "R$ 105,00", "R$ 420,00", "R$ 162,55"],
            "CMS s/ Franquia": ["R$ 93,50", "R$ 111,29", "R$ 176,64", "R$ 45,03", "R$ 31,22", "R$ 175,50", "R$ 273,00", "R$ 195,00", "R$ 780,00", "R$ 301,88"],
            "Probabilidade": ["40,0%", "30,0%", "30,0%", "30,0%", "40,0%", "40,0%", "20,0%", "10,0%", "1,0%", "75,0%"]
        }

        # Criação do DataFrame
        df = pd.DataFrame(dados)

        # Função de estilo para destacar a última linha
        def highlight_last_row(x):
            color = 'background-color: #f5f5f5'  # cinza claro
            df_style = pd.DataFrame('', index=x.index, columns=x.columns)
            df_style.loc[x.index[-1], :] = color
            return df_style

        # Exibir no Streamlit com estilo
        st.dataframe(df.style.apply(highlight_last_row, axis=None), use_container_width=True, hide_index=True)
        
        freq_compl_pc = 0.019 * (1 + 0.25)
        cms_compl_pc = 301.88
        
        st.divider()
        
        st.markdown("#### Tabela com o resultado para RLPP")
        
        freq_rlpp = freq + total_freq
        
        porc_os_troca_reparo_para_choque = total_freq/freq_rlpp
        porc_os_compl_pc = freq_compl_pc/freq_rlpp
        porc_os_rlp = freq/freq_rlpp
        
        cms_rlpp = (porc_os_troca_reparo_para_choque*total_cms) + (porc_os_compl_pc*cms_compl_pc) + (porc_os_rlp*col11)
        
        
        
        df_resultado_rlpp = pd.DataFrame([
            {
                "Cobertura": "Troca/Reparo de Para-choque",
                "CMS s/Franquia": f_valor(total_cms),
                "%OS Totais": f_perc(porc_os_troca_reparo_para_choque),
                "Frequência": f_perc(total_freq)
            },
            {
                "Cobertura": "Complementos de Lataria e PC",
                "CMS s/Franquia": f_valor(301.88),
                "%OS Totais": f_perc(porc_os_compl_pc),
                "Frequência": f_perc(freq_compl_pc)
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
        def highlight_last_row(x):
            color = 'background-color: #f5f5f5'  # cinza claro
            df_style = pd.DataFrame('', index=x.index, columns=x.columns)
            df_style.loc[x.index[-1], :] = color
            return df_style

        # Exibir no Streamlit com estilo
        st.dataframe(df_resultado_rlpp.style.apply(highlight_last_row, axis=None), use_container_width=True, hide_index=True) 
        
        # 🔁 Armazena os resultados no resumo geral
        resultados_totais.append({
            "Script": "RLPP",
            "Tipo Veículo": "Auto",
            "CMS": cms_rlpp,
            "Frequência": freq_rlpp
        })
        
        
        
        st.write("")
        
        

    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Troca - PC
def validacao_funcao_freq_cms_troca_pc(base_receita, base_despesa):
    
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"].copy()
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

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

    nome_script = "Troca - PC"
    
    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                ((base_receita["PARACHOQUE"] == True) | (base_receita["TROCA_DE_PARACHOQUE"] == True)) & 
                (base_receita["TIPO_VEICULO"] == tipo)
            ]
        
            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})
            
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Para-choque") & 
                (base_despesa["TIPO_VEICULO"] == tipo) & 
                (base_despesa["OS Reparo"] == "NÃO")
            ]
        
            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})

            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

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
            
            st.divider()
            st.markdown("#### Análise de Franquia")
            
            despesa_final_cms["Script Franquia"] = "Troca - PC"
            
            despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
            
            # Agrupa as OSs com franquia acima de 70%
            total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

            # Agrupa o total geral de OSs por script
            total_os_script = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "Total OSs"})
                
            # Calcula o total geral de OSs
            total_geral_os = total_os_script["Total OSs"].sum()

            # Cria a coluna de representatividade (%)
            total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

            # Junta os dois dataframes
            total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
            
            # Cria a coluna de representatividade (%) de franquia acima de 70% 
            total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
            
            # Agrupa os valores da franquia para realizar a representatividade da franquia por script
            total_valor_franquia = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Franquia Ajustada": "sum"})

            # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
            total_valor_negociado = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Valor Ajustado CMS": "sum"})

            # Junta os dois dataframes
            total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
            total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
            
            # Exibe no Streamlit
            total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
            
            # Ordena do maior para o menor
            total_script = total_script.sort_values(by="Total OSs", ascending=False)
            
            total_script = total_script.copy()
            
            total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
            total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
            
            total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
            total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
            
            
            total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
            total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
            total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
            
            st.dataframe(total_script, hide_index=True)
            
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Reparo - PC
def validacao_funcao_freq_cms_reparo_pc(base_receita, base_despesa):
    
    base_receita = base_receita[base_receita["TIPO_VEICULO"] == "Auto"].copy()
    tipo_veiculo = base_receita["TIPO_VEICULO"].dropna().unique()

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

    nome_script = "Reparo - PC"
    
    # Lista para armazenar os resultados por tipo de guincho
    resultados_totais = []

    for tipo in tipo_veiculo:
        with st.expander(f"▶ {tipo}"):

            # Filtragem das bases
            receita_filtrada = base_receita[
                ((base_receita["PARACHOQUE"] == True) | (base_receita["TROCA_DE_PARACHOQUE"] == True)) & 
                (base_receita["TIPO_VEICULO"] == tipo)
            ]
        
            receita_filtrada = receita_filtrada.rename(columns={"SEGURADORA": "Seguradora"})
            
            despesa_filtrada = base_despesa[
                (base_despesa["Script CMS"] == "Para-choque") & 
                (base_despesa["TIPO_VEICULO"] == tipo) & 
                (base_despesa["OS Reparo"] == "SIM")
            ]
        
            despesa_filtrada = despesa_filtrada.rename(columns={"SEGURADORA": "Seguradora"})
            
            # Agrupamento por seguradora
            receita_cia = receita_filtrada.groupby("Seguradora", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})
            despesa_cia = despesa_filtrada.groupby("Seguradora", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
            resultado_cia = pd.merge(receita_cia, despesa_cia, on="Seguradora", how="left").fillna(0)

            resultado_cia["CMS"] = resultado_cia["Despesa"] / resultado_cia["Qtd. OS's"].replace(0, np.nan)
            resultado_cia["Frequência"] = (resultado_cia["Qtd. OS's"] * 12) / resultado_cia["Qtd. Itens"].replace(0, np.nan)
            resultado_cia = resultado_cia.fillna(0)
            resultado_cia["Selecionar"] = True

            # Interface para selecionar seguradoras
            resultado_cia_exibe = resultado_cia.copy()
            resultado_cia_exibe["Qtd. Itens"] = resultado_cia["Qtd. Itens"].apply(f_int)
            resultado_cia_exibe["Qtd. OS's"] = resultado_cia["Qtd. OS's"].apply(f_int)
            resultado_cia_exibe["Despesa"] = resultado_cia["Despesa"].apply(f_valor)
            resultado_cia_exibe["CMS"] = resultado_cia["CMS"].apply(f_valor)
            resultado_cia_exibe["Frequência"] = resultado_cia["Frequência"].apply(f_perc)

            col1, col2 = st.columns(2)
            with col1:
                resultado_cia_exibe_freq_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_seguradora_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_cia_exibe_cms_editado = st.data_editor(
                    resultado_cia_exibe[["Seguradora", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["Seguradora", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_seguradora_cms_{nome_script}_{tipo}"
                )

            # Filtragem das seguradoras
            segs_freq = resultado_cia.loc[resultado_cia_exibe_freq_editado["Selecionar"], "Seguradora"].tolist()
            segs_cms = resultado_cia.loc[resultado_cia_exibe_cms_editado["Selecionar"], "Seguradora"].tolist()

            receita_mes_filtrada = receita_filtrada[receita_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_freq = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_freq)].copy()
            despesa_mes_cms = despesa_filtrada[despesa_filtrada["Seguradora"].isin(segs_cms)].copy()

            # Tabelas por mês
            receita_mes = receita_mes_filtrada.groupby("AnoMes", as_index=False)["ITENS"].sum().rename(columns={"ITENS": "Qtd. Itens"})

            def gerar_resultado_mes(despesa_mes, label):
                df = despesa_mes.groupby("AnoMes", as_index=False).agg({"Qtd. OS's": "sum", "Despesa": "sum"})
                resultado = pd.merge(receita_mes, df, on="AnoMes", how="left").fillna(0)
                resultado["CMS"] = resultado["Despesa"] / resultado["Qtd. OS's"].replace(0, np.nan)
                resultado["Frequência"] = (resultado["Qtd. OS's"] * 12) / resultado["Qtd. Itens"].replace(0, np.nan)
                resultado = resultado.fillna(0)
                resultado["Selecionar"] = True
                return resultado

            resultado_mes_freq = gerar_resultado_mes(despesa_mes_freq, "freq")
            resultado_mes_cms = gerar_resultado_mes(despesa_mes_cms, "cms")

            # Interfaces de seleção por período
            def formatar_resultado_exibe(df):
                df_exibe = df.copy()
                df_exibe["Qtd. Itens"] = df["Qtd. Itens"].apply(f_int)
                df_exibe["Qtd. OS's"] = df["Qtd. OS's"].apply(f_int)
                df_exibe["Despesa"] = df["Despesa"].apply(f_valor)
                df_exibe["CMS"] = df["CMS"].apply(f_valor)
                df_exibe["Frequência"] = df["Frequência"].apply(f_perc)
                return df_exibe

            col1, col2 = st.columns(2)
            with col1:
                resultado_mes_exibe_freq = formatar_resultado_exibe(resultado_mes_freq)
                resultado_mes_exibe_freq_editado = st.data_editor(
                    resultado_mes_exibe_freq[["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. Itens", "Qtd. OS's", "Frequência"],
                    key=f"data_editor_periodo_freq_{nome_script}_{tipo}"
                )
            with col2:
                resultado_mes_exibe_cms = formatar_resultado_exibe(resultado_mes_cms)
                resultado_mes_exibe_cms_editado = st.data_editor(
                    resultado_mes_exibe_cms[["AnoMes", "Qtd. OS's", "Despesa", "CMS", "Selecionar"]],
                    column_config={"Selecionar": st.column_config.CheckboxColumn("Selecionar")},
                    hide_index=True,
                    disabled=["AnoMes", "Qtd. OS's", "Despesa", "CMS"],
                    key=f"data_editor_periodo_cms_{nome_script}_{tipo}"
                )

            # Filtro final por período
            periodos_freq = resultado_mes_freq.loc[resultado_mes_exibe_freq_editado["Selecionar"], "AnoMes"]
            periodos_cms = resultado_mes_cms.loc[resultado_mes_exibe_cms_editado["Selecionar"], "AnoMes"]

            receita_final_freq = receita_mes_filtrada[receita_mes_filtrada["AnoMes"].isin(periodos_freq)]
            despesa_final_freq = despesa_mes_freq[despesa_mes_freq["AnoMes"].isin(periodos_freq)]
            despesa_final_cms = despesa_mes_cms[despesa_mes_cms["AnoMes"].isin(periodos_cms)]

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
            
            st.divider()
            st.markdown("#### Análise de Franquia")
            
            despesa_final_cms["Script Franquia"] = "Reparo - PC"
            
            despesa_final_cms["% Franquia"] = despesa_final_cms["Franquia Ajustada"]/despesa_final_cms["Valor Ajustado CMS"]
            
            # Agrupa as OSs com franquia acima de 70%
            total_os_70porc = despesa_final_cms[despesa_final_cms["% Franquia"] > 0.7] \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "OSs Franquia > 70%"})

            # Agrupa o total geral de OSs por script
            total_os_script = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Qtd. OS's": "sum"}) \
                .rename(columns={"Qtd. OS's": "Total OSs"})
                
            # Calcula o total geral de OSs
            total_geral_os = total_os_script["Total OSs"].sum()

            # Cria a coluna de representatividade (%)
            total_os_script["% Representatividade OSs"] = (total_os_script["Total OSs"] / total_geral_os)

            # Junta os dois dataframes
            total_os_script = pd.merge(total_os_script, total_os_70porc, on="Script Franquia", how="left").fillna(0)
            
            # Cria a coluna de representatividade (%) de franquia acima de 70% 
            total_os_script["% Representatividade OSs Franquia > 70%"] = (total_os_script["OSs Franquia > 70%"] / total_os_script["Total OSs"])
            
            # Agrupa os valores da franquia para realizar a representatividade da franquia por script
            total_valor_franquia = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Franquia Ajustada": "sum"})

            # Agrupa os valores do valor total negociado para realizar a representatividade da franquia por script
            total_valor_negociado = despesa_final_cms \
                .groupby("Script Franquia", as_index=False) \
                .agg({"Valor Ajustado CMS": "sum"})

            # Junta os dois dataframes
            total_valor_script = pd.merge(total_valor_negociado, total_valor_franquia, on="Script Franquia", how="left").fillna(0)
            total_valor_script["% Representatividade de Franquia"] = total_valor_script["Franquia Ajustada"]/total_valor_script["Valor Ajustado CMS"]
            
            # Exibe no Streamlit
            total_script = pd.merge(total_valor_script, total_os_script, on="Script Franquia", how="left").fillna(0)
            
            # Ordena do maior para o menor
            total_script = total_script.sort_values(by="Total OSs", ascending=False)
            
            total_script = total_script.copy()
            
            total_script["Total OSs"] = total_script["Total OSs"].apply(f_int)
            total_script["OSs Franquia > 70%"] = total_script["OSs Franquia > 70%"].apply(f_int)
            
            total_script["Valor Ajustado CMS"] = total_script["Valor Ajustado CMS"].apply(f_valor)
            total_script["Franquia Ajustada"] = total_script["Franquia Ajustada"].apply(f_valor)
            
            
            total_script["% Representatividade de Franquia"] = total_script["% Representatividade de Franquia"].apply(f_perc)
            total_script["% Representatividade OSs"] = total_script["% Representatividade OSs"].apply(f_perc)
            total_script["% Representatividade OSs Franquia > 70%"] = total_script["% Representatividade OSs Franquia > 70%"].apply(f_perc)
            
            st.dataframe(total_script, hide_index=True)
            
    # 📦 Converte a lista em DataFrame
    df_resumo_geral = pd.DataFrame(resultados_totais)

    # 🔚 Retorna o DataFrame com os resumos
    return df_resumo_geral

# Resumo de todas as tabelas e suas coberturas
def show_validacao_freq_cms(tipo_coberturas, base_receita, base_despesa, parametros):

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
    