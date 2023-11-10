import streamlit as st
import pandas as pd
import os
import openpyxl


# Configurar a página
st.set_page_config(
    page_title="Banco de Horas",
    page_icon=":hourglass:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para formatar timedelta
def format_timedelta(timedelta):
    total_seconds = int(timedelta.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{'-' if total_seconds < 0 else ''}{hours:02}:{minutes:02}:{seconds:02}"

# Obtém o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Constrói o caminho relativo ao diretório do script
file_path = os.path.join(script_dir, "Recursos", "Extensão de jornada x compensação.xlsx")

# Carregar os dados
extensao_jornada = pd.read_excel(file_path, sheet_name="EXTENSÃO DE JORNADA")
horas_compensadas = pd.read_excel(file_path, sheet_name="HORAS COMPENSADAS")

# ... (restante do código permanece o mesmo)

# Layout com containers
with st.container():
    col1, col2 = st.columns([1, 2])
    
    # Selecionar servidor
    with col1:
        servidor_selecionado = st.selectbox('Selecione um servidor:', banco_de_horas.index.unique())
    
    # Mostrar saldo do banco de horas
    with col2:
        saldo = banco_de_horas.loc[servidor_selecionado, "Saldo Banco de Horas"]
        st.metric("Saldo Banco de Horas", saldo)

# Mostrar datas e horas de compensação
with st.container():
    compensacoes = horas_compensadas[horas_compensadas["Servidor"] == servidor_selecionado][["Data_compensacao", "Horas a serem compensadas"]]
    compensacoes = compensacoes.dropna(subset=["Data_compensacao"])
    if compensacoes.empty:
        st.info('Este servidor não possui horas compensadas.')
    else:
        compensacoes = compensacoes.rename(columns={"Data_compensacao": "Data de compensação", "Horas a serem compensadas": "Horas utilizadas"})
        compensacoes["Data de compensação"] = compensacoes["Data de compensação"].dt.strftime('%Y-%m-%d')
        compensacoes["Horas utilizadas"] = compensacoes["Horas utilizadas"].apply(format_timedelta)
        st.table(compensacoes)
