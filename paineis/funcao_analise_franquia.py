import streamlit as st
import pandas as pd
import numpy as np

def show_analise_franquias(tipo_coberturas, base_despesa, parametros):
    
    def f_valor(x): return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def f_int(x): return f"{int(x):,}".replace(",", ".")
    def f_perc(x): return f"{x * 100:.2f}%".replace(".", ",")
    
    st.write(tipo_coberturas)
    
    
    
    