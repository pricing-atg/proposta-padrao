import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Tabela de markup
tabela_markup = {
    "Vidros": [1.8, 1.9, 2.0, 2.3],
    "ADAS": [1.8, 1.9, 2.0, 2.3],
    "Cristalização": [4.0, 4.2, 4.5, 5.2],
    "Higienização": [4.0, 4.2, 4.5, 5.2],
    "FLR": [1.8, 1.9, 2.0, 2.3],
    "Pesado": [2.0, 2.1, 2.2, 2.6],
    "Moto": [3.0, 3.2, 3.4, 3.9],
    "SRA": [0.43, 0.49, 0.52, 0.6],
    "Martelinho": [2.6, 2.7, 2.9, 3.4],
    "RLP": [2.6, 2.7, 2.9, 3.4],
    "RLPP": [3.0, 3.2, 3.4, 3.9],
    "RPS": [2.6, 2.7, 2.9, 3.4],
    "Pneu": [2.6, 2.7, 2.9, 3.4],
    "Polimento de Farol": [1.8, 1.9, 2.0, 2.3],
    "Reparo de Parabrisa": [1.8, 1.9, 2.0, 2.3],
    "RLPP": [1.8, 1.9, 2.0, 2.3],
    "Troca - PC": [1.8, 1.9, 2.0, 2.3],
    "Reparo - PC": [1.8, 1.9, 2.0, 2.3]
}

def show_proposta_ponto_frequencia(base_resumo_geral, parametros, tipo_precificacao):

    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")
    def f_dec(x): return f"{x:.2f}".replace(".", ",")

    df = base_resumo_geral.copy()
    
    # ✅ Adiciona linha "Vidros e ADAS" caso ambos existam para Auto
    cond_vidros = (df["Script"] == "Vidros") & (df["Tipo Veículo"] == "Auto")
    cond_adas = (df["Script"] == "ADAS") & (df["Tipo Veículo"] == "Auto")

    if cond_vidros.any() and cond_adas.any():
        freq_vidros = df.loc[cond_vidros, "Frequência"].values[0]
        freq_adas = df.loc[cond_adas, "Frequência"].values[0]
        cms_vidros = df.loc[cond_vidros, "CMS"].values[0]

        nova_linha = {
            "Tipo Veículo": "Auto",
            "Script": "Vidros e ADAS",
            "Frequência": freq_vidros + freq_adas,
            "CMS": cms_vidros
        }

        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    
    df["Frequência Mensal"] = df["Frequência"] / 12
    df_imposto_ajuste = pd.DataFrame(parametros["imposto_ajuste"])
    imposto = df_imposto_ajuste["Imposto (%)"].values[0] / 100

    def obter_markup(row):
        if row["Script"] == "SRA":
            pm_desejado = 0.60
            cms = row["CMS"]
            freq_mensal = row["Frequência"] / 12
            if cms > 0 and freq_mensal > 0:
                return (pm_desejado * (1 - imposto)) / (cms * freq_mensal)
            else:
                return 1.0
        elif row["Tipo Veículo"] == "Auto":
            return tabela_markup.get(row["Script"], [1])[-1]
        elif row["Tipo Veículo"] in ["Moto", "Carga"]:
            return tabela_markup.get(row["Tipo Veículo"], [1])[-1]
        else:
            return 1.0

    df["Markup"] = df.apply(obter_markup, axis=1)

    for tipo in df["Tipo Veículo"].unique():
        st.markdown(f"#### Proposta para o tipo de véiculo - **{tipo}**")
        df_tipo = df[df["Tipo Veículo"] == tipo].copy()

        with st.expander("##### ✏️ Informe a quantidade de Itens e Markup por Cobertura:"):
            itens_por_script = {}
            markup_por_script = {}
            for script in df_tipo["Script"].unique():
                valor_padrao_itens = 1000
                valor_padrao_markup = round(df_tipo[df_tipo["Script"] == script]["Markup"].iloc[0], 2)
                max_markup = max(20.0, valor_padrao_markup + 5)
                key_input_itens = f"input_itens_{tipo}_{script}"
                key_input_markup = f"input_markup_{tipo}_{script}"
                col1, col2 = st.columns(2)
                with col1:
                    itens_por_script[script] = st.number_input(
                        f"Itens - {script}", min_value=0, max_value=100000,
                        value=valor_padrao_itens, step=100, key=key_input_itens
                    )
                with col2:
                    markup_por_script[script] = st.number_input(
                        f"Markup - {script}", min_value=0.0, max_value=max_markup,
                        value=valor_padrao_markup, step=0.05, key=key_input_markup
                    )

        df_tipo["Itens"] = df_tipo["Script"].map(itens_por_script)
        df_tipo["Markup"] = df_tipo["Script"].map(markup_por_script)

        # Elaboração de planos
        qtd_planos = st.number_input(f"Quantos planos deseja criar para {tipo}?", min_value=0, max_value=10, value=0, key=f"qtd_planos_{tipo}")
        todos_scripts = df_tipo["Script"].unique().tolist()
        if qtd_planos > 0:
            planos_config = {}
            nomes_planos_completos = []
            with st.expander("##### ✏️ Seleção das coberturas por plano:"):
                for i in range(1, qtd_planos + 1):
                    selecao = st.multiselect(f"Plano {i}", todos_scripts, default=[], key=f"plano_{i}_{tipo}")
                    planos_config[f"Plano {i}"] = selecao
                    if selecao:
                        nome_completo = f"Plano {i} - " + " + ".join(selecao)
                    else:
                        nome_completo = f"Plano {i} - (vazio)"
                    nomes_planos_completos.append(nome_completo)

            for plano, scripts in planos_config.items():
                if not scripts: continue
                idx = int(plano.split()[-1]) - 1
                nome_plano = nomes_planos_completos[idx]
                df_sel = df_tipo[df_tipo["Script"].isin(scripts)].copy()
                freq_total = df_sel["Frequência Mensal"].sum()
                cms_total = (df_sel["CMS"] * df_sel["Frequência Mensal"]).sum()
                cms_plano = cms_total / freq_total if freq_total > 0 else 0
                markup_plano = df_sel["Markup"].mean()
                pm_pf = (cms_plano * freq_total * markup_plano) / (1 - imposto) if (1 - imposto) > 0 else 0
                itens_plano = df_sel["Itens"].max()
                receita = itens_plano * pm_pf
                despesa = cms_plano * itens_plano * freq_total
                sinistralidade = despesa / receita if receita > 0 else 0
                margem = receita - despesa
                df_tipo = pd.concat([df_tipo, pd.DataFrame.from_records([{ 
                    "Tipo Veículo": tipo, "Script": nome_plano, "Itens": itens_plano,
                    "CMS": cms_plano, "Frequência Mensal": freq_total, "Markup": markup_plano,
                    "PM - Ponto Frequência": pm_pf, "Receita": receita, "Despesa": despesa,
                    "Sinistralidade": sinistralidade, "Margem": margem
                }])], ignore_index=True)

        key_input_faixa_freq = f"faixa_freq_{tipo}"
        intervalo = st.number_input("Informe o intervalo da faixa de frequência (%)", 0.01, 5.0, 0.10, 0.01, format="%.2f", key=key_input_faixa_freq) / 100
        faixas_freq = np.arange(0, 0.300 + intervalo, intervalo)
        tabela3_rows = []
        pm_pf_dict = {}
        for i in range(len(faixas_freq) - 1):
            minimo, maximo = faixas_freq[i], faixas_freq[i + 1]
            freq_media = (minimo + maximo) / 2
            linha = {"Mínimo": f_perc(minimo), "Máximo": f_perc(maximo), "Faixa de Frequência": f"{f_perc(minimo)} a {f_perc(maximo)}", "Freq. Média": f_perc(freq_media)}
            for script in df_tipo["Script"].unique():
                row_script = df_tipo[df_tipo["Script"] == script].iloc[0]
                pm_pf = (row_script["CMS"] * freq_media * row_script["Markup"]) / (1 - imposto)
                linha[script] = f_valor(pm_pf)
                pm_pf_dict.setdefault(script, []).append((minimo, maximo, pm_pf))
            tabela3_rows.append(linha)

        tabela3_df = pd.DataFrame(tabela3_rows)
        df_tipo["PM - Ponto Frequência"] = df_tipo.apply(lambda row: next((pm for min_, max_, pm in pm_pf_dict.get(row["Script"], []) if min_ < row["Frequência Mensal"] <= max_), np.nan), axis=1)
        df_tipo["Receita"] = df_tipo["Itens"] * df_tipo["PM - Ponto Frequência"]
        df_tipo["Despesa"] = df_tipo["CMS"] * df_tipo["Itens"] * df_tipo["Frequência Mensal"]
        df_tipo["Sinistralidade"] = np.where(df_tipo["Receita"] > 0, df_tipo["Despesa"] / df_tipo["Receita"], 0)
        df_tipo["Margem"] = df_tipo["Receita"] - df_tipo["Despesa"]
        df_tipo["PM - Sem/MKP"] = (df_tipo["CMS"] * df_tipo["Frequência Mensal"]) / (1 - imposto)
        df_tipo["PM - Item Exposto"] = (df_tipo["CMS"] * df_tipo["Frequência Mensal"] * df_tipo["Markup"]) / (1 - imposto)

        ordem_colunas = ["Vidros", "FLR", "Higienização", "Cristalização", "Martelinho", "SRA", "RLP", "RPS", "Pneu", "ADAS", "Polimento de Farol", "Reparo de Parabrisa", "RLPP", "Troca - PC", "Reparo - PC"]
        scripts_presentes = [s for s in ordem_colunas if s in df_tipo["Script"].unique()] + [s for s in df_tipo["Script"].unique() if s not in ordem_colunas]

        tabela1 = df_tipo.pivot_table(index="Script", values=["Receita", "Despesa", "Sinistralidade", "Margem"]).T.reindex(columns=scripts_presentes)
        tabela1_formatada = tabela1.copy()
        for col in tabela1.columns:
            tabela1_formatada[col] = [f_valor(val) if idx in ["Receita", "Despesa", "Margem"] else f_perc(val) for idx, val in zip(tabela1.index, tabela1[col])]

        tabela2 = df_tipo.pivot_table(index="Script", values=["CMS", "Frequência Mensal", "Itens", "Markup", "PM - Ponto Frequência", "PM - Sem/MKP"]).T.reindex(columns=scripts_presentes)
        tabela2_formatada = tabela2.copy()
        for col in tabela2.columns:
            tabela2_formatada[col] = [f_valor(val) if idx in ["CMS", "PM - Ponto Frequência", "PM - Sem/MKP"] else f_perc(val) if idx == "Frequência Mensal" else f_dec(val) if idx == "Markup" else f"{int(val)}" for idx, val in zip(tabela2.index, tabela2[col])]

        st.markdown("##### 💰 Tabela 1 - Receita, Despesa, Sinistralidade e Margem")
        st.dataframe(tabela1_formatada)
        st.markdown("##### 📊 Tabela 2 - Detalhamento do Prêmio com PM - Ponto Frequência")
        st.dataframe(tabela2_formatada)
        st.markdown("##### 🔀 Tabela 3 - PM - Ponto Frequência por Faixa de Frequência")
        st.dataframe(tabela3_df, hide_index=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabela1.to_excel(writer, sheet_name="Resumo Geral")
            tabela2.to_excel(writer, sheet_name="Prêmio Mensal")
            tabela3_df.to_excel(writer, sheet_name="Tabela - Faixa Frequência")
        excel_data = output.getvalue()

        st.download_button(
            label="📅 Exportar tabelas para Excel",
            data=excel_data,
            file_name=f"Proposta Padrão - {tipo_precificacao} {tipo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


  
                
def show_proposta_item_exposto(base_resumo_geral, parametros, tipo_precificacao):
    
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")
    def f_dec(x): return f"{x:.2f}".replace(".", ",")

    df = base_resumo_geral.copy()
    df["Frequência Mensal"] = df["Frequência"] / 12

    df_imposto_ajuste = pd.DataFrame(parametros["imposto_ajuste"])
    imposto = df_imposto_ajuste["Imposto (%)"].values[0] / 100

    def obter_markup(row):
        if row["Script"] == "SRA":
            pm_desejado = 0.60
            cms = row["CMS"]
            freq_mensal = row["Frequência"] / 12
            if cms > 0 and freq_mensal > 0:
                return (pm_desejado * (1 - imposto)) / (cms * freq_mensal)
            else:
                return 1.0
        elif row["Tipo Veículo"] == "Auto":
            return tabela_markup.get(row["Script"], [1])[-1]
        elif row["Tipo Veículo"] in ["Moto", "Carga"]:
            return tabela_markup.get(row["Tipo Veículo"], [1])[-1]
        else:
            return 1.0

    df["Markup"] = df.apply(obter_markup, axis=1)

    for tipo in df["Tipo Veículo"].unique():
        
        st.divider()        
        st.markdown(f"#### Proposta para o tipo de véiculo - **{tipo}**")
        df_tipo = df[df["Tipo Veículo"] == tipo].copy()

        with st.expander("##### ✏️ Informe a quantidade de Itens e Markup por Cobertura:"):
            itens_por_script = {}
            markup_por_script = {}

            for script in df_tipo["Script"].unique():
                valor_padrao_itens = 1000
                valor_padrao_markup = round(df_tipo[df_tipo["Script"] == script]["Markup"].iloc[0], 2)
                max_markup = max(20.0, valor_padrao_markup + 5)

                key_input_itens = f"input_itens_{tipo}_{script}"
                key_input_markup = f"input_markup_{tipo}_{script}"

                col1, col2 = st.columns(2)
                with col1:
                    itens_por_script[script] = st.number_input(
                        f"Itens - {script}", min_value=0, max_value=100000,
                        value=valor_padrao_itens, step=100, key=key_input_itens
                    )
                with col2:
                    markup_por_script[script] = st.number_input(
                        f"Markup - {script}", min_value=0.0, max_value=max_markup,
                        value=valor_padrao_markup, step=0.05, key=key_input_markup
                    )

        df_tipo["Itens"] = df_tipo["Script"].map(itens_por_script)
        df_tipo["Markup"] = df_tipo["Script"].map(markup_por_script)

        df_tipo["PM - Sem/MKP"] = (df_tipo["CMS"] * df_tipo["Frequência Mensal"]) / (1 - imposto)
        df_tipo["PM - Item Exposto"] = (df_tipo["CMS"] * df_tipo["Frequência Mensal"] * df_tipo["Markup"]) / (1 - imposto)
        
        df_tipo["Receita"] = df_tipo["PM - Item Exposto"] * df_tipo["Itens"]
        df_tipo["Despesa"] = df_tipo["CMS"] * df_tipo["Itens"] * df_tipo["Frequência Mensal"]
        df_tipo["Sinistralidade"] = np.where(df_tipo["Receita"] > 0, df_tipo["Despesa"] / df_tipo["Receita"], 0)
        df_tipo["Margem"] = df_tipo["Receita"] - df_tipo["Despesa"]
        
        
        # Elaborar planos
        st.markdown("##### 🧩 Elaboração de Planos")
        
        qtd_planos = st.number_input(f"Quantos planos deseja criar para {tipo}?", min_value=0, max_value=10, value=0, key=f"qtd_planos_{tipo}")
        todos_scripts = df_tipo["Script"].unique().tolist()

        if qtd_planos > 0:
            planos_config = {}
            nomes_planos_completos = []

            with st.expander("##### ✏️ Seleção das coberturas por plano:"):
                for i in range(1, qtd_planos + 1):
                    st.markdown(f"**📦 Plano {i}**")
                    selecao = st.multiselect(
                        f"Selecione os scripts para o Plano {i} ({tipo})", 
                        options=todos_scripts,
                        default=todos_scripts,
                        placeholder=f"Selecione as coberturas do Plano {i} ({tipo})", 
                        key=f"selecionar_coberturas_plano_{i}_{tipo}"
                    )
                    planos_config[f"Plano {i}"] = selecao

                    if selecao:
                        nome_completo = f"Plano {i} - " + " + ".join(selecao)
                    else:
                        nome_completo = f"Plano {i} - (vazio)"
                    nomes_planos_completos.append(nome_completo)

            lista_df_planos = []

            for plano, scripts_selecionados in planos_config.items():
                if not scripts_selecionados:
                    continue

                df_sel = df_tipo[df_tipo["Script"].isin(scripts_selecionados)].copy()

                itens_plano = df_sel["Itens"].max()
                freq_total = df_sel["Frequência Mensal"].sum()
                cms_total = (df_sel["CMS"] * df_sel["Frequência Mensal"]).sum()
                cms_plano = cms_total / freq_total if freq_total > 0 else 0

                pm_item_exposto_total = (df_sel["PM - Item Exposto"] * df_sel["Itens"]).sum()
                pm_sem_mkp_total = (df_sel["PM - Sem/MKP"] * df_sel["Itens"]).sum()
                markup_plano = pm_item_exposto_total / pm_sem_mkp_total if pm_sem_mkp_total > 0 else 1.0

                pm_sem_mkp = (cms_plano * freq_total) / (1 - imposto) if (1 - imposto) > 0 else 0
                pm_item_exposto = (cms_plano * freq_total * markup_plano) / (1 - imposto) if (1 - imposto) > 0 else 0

                receita = pm_item_exposto * itens_plano
                despesa = cms_plano * itens_plano * freq_total
                sinistralidade = despesa / receita if receita > 0 else 0
                margem = receita - despesa

                idx = int(plano.split()[-1]) - 1
                nome_plano_completo = nomes_planos_completos[idx]

                linha_plano = {
                    "Tipo Veículo": tipo,
                    "Script": nome_plano_completo,
                    "Itens": itens_plano,
                    "CMS": cms_plano,
                    "Frequência Mensal": freq_total,
                    "Markup": markup_plano,
                    "PM - Sem/MKP": pm_sem_mkp,
                    "PM - Item Exposto": pm_item_exposto,
                    "Receita": receita,
                    "Despesa": despesa,
                    "Sinistralidade": sinistralidade,
                    "Margem": margem
                }

                df_plano = pd.DataFrame([linha_plano])
                lista_df_planos.append(df_plano)

            if lista_df_planos:
                df_tipo = pd.concat([df_tipo] + lista_df_planos, ignore_index=True)

                ordem_colunas = ["Vidros", "FLR", "Higienização", "Cristalização", "Martelinho", 
                                "SRA", "RLP", "RPS", "Pneu", "ADAS", "Polimento de Farol", 
                                "Reparo de Parabrisa", "RLPP", "Troca - PC", "Reparo - PC"]

                ordem_colunas += nomes_planos_completos
        else:
            ordem_colunas = ["Vidros", "FLR", "Higienização", "Cristalização", "Martelinho", 
                            "SRA", "RLP", "RPS", "Pneu", "ADAS", "Polimento de Farol", 
                            "Reparo de Parabrisa", "RLPP", "Troca - PC", "Reparo - PC"]

        scripts_presentes = [script for script in ordem_colunas if script in df_tipo["Script"].unique()]

        tabela1 = df_tipo.pivot_table(
            index="Script",
            values=["Receita", "Despesa", "Sinistralidade", "Margem"]
        ).T

        tabela1 = tabela1.loc[["Receita", "Despesa", "Sinistralidade", "Margem"]]
        tabela1 = tabela1.reindex(columns=scripts_presentes)

        tabela1_formatada = tabela1.copy()
        for col in tabela1.columns:
            tabela1_formatada[col] = [
                f_valor(val) if i in ["Receita", "Despesa", "Margem"]
                else f_perc(val)
                for i, val in zip(tabela1.index, tabela1[col])
            ]

        st.markdown("##### 💰 Tabela 1 - Receita, Despesa, Sinistralidade e Margem")
        st.dataframe(tabela1_formatada)

        tabela2 = df_tipo.pivot_table(
            index="Script",
            values=["CMS", "Frequência Mensal", "Itens", "Markup", "PM - Item Exposto", "PM - Sem/MKP"]
        ).T
        tabela2 = tabela2.reindex(columns=scripts_presentes)

        tabela2_formatada = tabela2.copy()
        for col in tabela2.columns:
            tabela2_formatada[col] = [
                f_valor(val) if i in ["CMS", "PM - Item Exposto", "PM - Sem/MKP"]
                else f_perc(val) if i == "Frequência Mensal"
                else f_dec(val) if i == "Markup"
                else f"{int(val)}"
                for i, val in zip(tabela2.index, tabela2[col])
            ]

        st.markdown("##### 📊 Tabela 2 - Detalhamento do Prêmio")
        st.dataframe(tabela2_formatada)

        # Exportar Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabela1.to_excel(writer, sheet_name="Resumo Geral", startrow=1, header=True)
            tabela2.to_excel(writer, sheet_name="Prêmio Mensal", startrow=1, header=True)

            workbook = writer.book

            formato_branco = workbook.add_format({'bg_color': '#FFFFFF'})
            formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#FFFFFF'})
            formato_perc = workbook.add_format({'num_format': '0.00%', 'bg_color': '#FFFFFF'})
            formato_inteiro = workbook.add_format({'num_format': '0', 'bg_color': '#FFFFFF'})
            formato_decimal = workbook.add_format({'num_format': '0.00', 'bg_color': '#FFFFFF'})

            worksheet1 = writer.sheets["Resumo Geral"]
            worksheet1.write(0, 0, "Tabela 1 - Receita, Despesa, Sinistralidade e Margem")

            for row_idx, index_name in enumerate(tabela1.index, start=2):
                for col_idx, value in enumerate(tabela1.loc[index_name], start=1):
                    if index_name in ["Receita", "Despesa", "Margem"]:
                        worksheet1.write(row_idx, col_idx, value, formato_moeda)
                    elif index_name == "Sinistralidade":
                        worksheet1.write(row_idx, col_idx, value, formato_perc)

            worksheet2 = writer.sheets["Prêmio Mensal"]
            worksheet2.write(0, 0, "Tabela 2 - Detalhamento do Prêmio")

            for row_idx, index_name in enumerate(tabela2.index, start=2):
                for col_idx, value in enumerate(tabela2.loc[index_name], start=1):
                    if index_name in ["CMS", "PM - Item Exposto", "PM - Sem/MKP"]:
                        worksheet2.write(row_idx, col_idx, value, formato_moeda)
                    elif index_name == "Frequência Mensal":
                        worksheet2.write(row_idx, col_idx, value, formato_perc)
                    elif index_name == "Markup":
                        worksheet2.write(row_idx, col_idx, value, formato_decimal)
                    elif index_name == "Itens":
                        worksheet2.write(row_idx, col_idx, value, formato_inteiro)

        excel_data = output.getvalue()

        st.download_button(
            label="📥 Exportar tabelas para Excel",
            data=excel_data,
            file_name=f"Proposta Padrão - {tipo_precificacao} {tipo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )