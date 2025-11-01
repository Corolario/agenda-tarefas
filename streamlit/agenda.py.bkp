import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Configuracao da pagina
st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="✅")

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect('tarefas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tarefas
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         data TEXT NOT NULL,
         tarefa TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

# Funcao para adicionar tarefa
def adicionar_tarefa(data, tarefa):
    conn = sqlite3.connect('tarefas.db')
    c = conn.cursor()
    c.execute('INSERT INTO tarefas (data, tarefa) VALUES (?, ?)', (data, tarefa))
    conn.commit()
    conn.close()

# Funcao para obter todas as tarefas
def obter_tarefas():
    conn = sqlite3.connect('tarefas.db')
    df = pd.read_sql_query('SELECT id, data, tarefa FROM tarefas', conn)
    conn.close()
    # Converter a coluna data para datetime e ordenar corretamente
    df['data_ordenacao'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df = df.sort_values('data_ordenacao')
    df = df.drop('data_ordenacao', axis=1)
    df = df.reset_index(drop=True)
    return df

# Funcao para editar tarefa
def editar_tarefa(id_tarefa, nova_data, nova_tarefa):
    conn = sqlite3.connect('tarefas.db')
    c = conn.cursor()
    c.execute('UPDATE tarefas SET data = ?, tarefa = ? WHERE id = ?', (nova_data, nova_tarefa, id_tarefa))
    conn.commit()
    conn.close()

# Funcao para deletar tarefa
def deletar_tarefa(id_tarefa):
    conn = sqlite3.connect('tarefas.db')
    c = conn.cursor()
    c.execute('DELETE FROM tarefas WHERE id = ?', (id_tarefa,))
    conn.commit()
    conn.close()

# Dialog para cadastrar nova tarefa
@st.dialog("Nova Tarefa")
def cadastrar_tarefa():
    data = st.date_input("Data", value=datetime.now(), format="DD/MM/YYYY")
    tarefa = st.text_area("Tarefa", placeholder="Descreva sua tarefa...")

    if st.button("Salvar", use_container_width=True):
        if tarefa.strip():
            data_formatada = data.strftime("%Y-%m-%d")
            adicionar_tarefa(data_formatada, tarefa)
            st.success("Tarefa adicionada com sucesso!")
            st.rerun()
        else:
            st.error("Por favor, preencha a descricao da tarefa.")

# Dialog para editar tarefa
@st.dialog("Editar Tarefa")
def editar_tarefa_dialog(id_tarefa, data_atual, tarefa_atual):
    # Converter a data string para datetime
    data_obj = datetime.strptime(data_atual, "%Y-%m-%d")

    nova_data = st.date_input("Data", value=data_obj, format="DD/MM/YYYY")
    nova_tarefa = st.text_area("Tarefa", value=tarefa_atual)

    if st.button("Salvar", use_container_width=True):
        if nova_tarefa.strip():
            data_formatada = nova_data.strftime("%Y-%m-%d")
            editar_tarefa(id_tarefa, data_formatada, nova_tarefa)
            st.success("Tarefa editada com sucesso!")
            st.rerun()
        else:
            st.error("Por favor, preencha a descricao da tarefa.")

# Inicializar banco de dados
init_db()

# Exibir tarefas
tarefas_df = obter_tarefas()

if not tarefas_df.empty:
    st.subheader("Tarefas")

    # Exibir tabela sem o ID e com titulos personalizados
    tarefas_exibir = tarefas_df[['data', 'tarefa']].copy()
    tarefas_exibir.columns = ['Data', 'Tarefa']

    # CSS para definir largura da coluna
    st.markdown("""
        <style>
        table td:nth-child(2) {
            width: 120px !important;
            max-width: 120px !important;
        }
        table th:nth-child(2) {
            width: 120px !important;
            max-width: 120px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.table(tarefas_exibir)

    # Secao para editar tarefas
    with st.expander("✏️ Editar Tarefa"):
        id_editar = st.selectbox(
            "Selecione a tarefa para editar",
            options=tarefas_df['id'].tolist(),
            format_func=lambda x: f"{tarefas_df[tarefas_df['id']==x]['data'].values[0]} - {tarefas_df[tarefas_df['id']==x]['tarefa'].values[0][:50]}...",
            key="select_editar"
        )

        if st.button("Editar", type="primary", key="btn_editar"):
            tarefa_selecionada = tarefas_df[tarefas_df['id']==id_editar].iloc[0]
            editar_tarefa_dialog(id_editar, tarefa_selecionada['data'], tarefa_selecionada['tarefa'])

    # Secao para deletar tarefas
    with st.expander("🗑️ Deletar Tarefa"):
        id_deletar = st.selectbox(
            "Selecione a tarefa para deletar",
            options=tarefas_df['id'].tolist(),
            format_func=lambda x: f"{tarefas_df[tarefas_df['id']==x]['data'].values[0]} - {tarefas_df[tarefas_df['id']==x]['tarefa'].values[0][:50]}..."
        )

        if st.button("Deletar", type="primary"):
            deletar_tarefa(id_deletar)
            st.success("Tarefa deletada!")
            st.rerun()
else:
    st.info("Nenhuma tarefa cadastrada. Clique em 'Nova Tarefa' para comecar!")

# Botao para abrir dialog de nova tarefa
if st.button("➕ Nova Tarefa", use_container_width=True):
    cadastrar_tarefa()