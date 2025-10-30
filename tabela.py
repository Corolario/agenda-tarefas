# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd

def obter_dados_tarefas():
    """Lê os dados do banco de dados e retorna como DataFrame"""
    try:
        conn = sqlite3.connect('tarefas.db')
        df = pd.read_sql_query('SELECT data, tarefa FROM tarefas ORDER BY data', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
        return pd.DataFrame(columns=['id', 'data', 'tarefa'])

def imprimir_tabela_dataframe(df):
    """Exibe tabela HTML customizada com controle total sobre largura das colunas"""
    import streamlit.components.v1 as components
    import html as html_lib

    if df.empty:
        st.info("Nenhuma tarefa cadastrada")
        return

    # Formatar data
    df_display = df.copy()
    df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%y')

    # Construir HTML
    html_content = """
    <style>
    * {margin:0;padding:0;box-sizing:border-box;}
    body {font-family:sans-serif;font-size:14px;}
    table {width:100%;border-collapse:collapse;table-layout:fixed;}
    th,td {border:1px solid #ddd;padding:8px;text-align:left;}
    col.data {width:80px;}
    col.tarefa {width:auto;}
    </style>
    <table>
    <colgroup>
    <col class="data">
    <col class="tarefa">
    </colgroup>
    <thead><tr><th>Data</th><th>Tarefa</th></tr></thead>
    <tbody>
    """

    for _, row in df_display.iterrows():
        data_safe = html_lib.escape(str(row['data']))
        tarefa_safe = html_lib.escape(str(row['tarefa']))
        html_content += f"<tr><td>{data_safe}</td><td>{tarefa_safe}</td></tr>"

    html_content += "</tbody></table>"

    # Altura dinâmica
    altura = min(800, 40 + (len(df_display) * 33))
    components.html(html_content, height=altura, scrolling=False)

# Configuração da página
st.set_page_config(
    page_title="Tabela de Tarefas",
    page_icon="📋",
    layout="wide"
)

# Título
st.subheader("📋 Tarefas")

# Obter dados do banco
df_tarefas = obter_dados_tarefas()

# Imprimir tabela usando dataframe
imprimir_tabela_dataframe(df_tarefas)
