import streamlit as st
import pandas as pd
import requests
from io import BytesIO

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

# Carregar os dados
github_url = 'https://raw.githubusercontent.com/jairocandido/Banco-de-horas/master/Recursos/Extens%C3%A3o%20de%20jornada%20x%20compensa%C3%A7%C3%A3o.xlsx'
extensao_jornada = pd.read_excel(github_url, sheet_name="EXTENSÃO DE JORNADA")
horas_compensadas = pd.read_excel(github_url, sheet_name="HORAS COMPENSADAS")

# Renomear a coluna 'Cod_Guarda' para 'Servidor'
extensao_jornada = extensao_jornada.rename(columns={'Cod_Guarda': 'Servidor'})

# Tratar dados faltantes
extensao_jornada["Horas/minutos extras"] = extensao_jornada["Horas/minutos extras"].fillna("0:00:00")
horas_compensadas["Horas a serem compensadas"] = horas_compensadas["Horas a serem compensadas"].fillna("0:00:00")
extensao_jornada["Servidor"] = extensao_jornada["Servidor"].fillna("Dados Faltantes")
horas_compensadas["Servidor"] = horas_compensadas["Servidor"].fillna("Dados Faltantes")

# Converter as colunas de tempo para o formato de tempo
extensao_jornada["Horas/minutos extras"] = pd.to_timedelta(extensao_jornada["Horas/minutos extras"])
horas_compensadas["Horas a serem compensadas"] = pd.to_timedelta(horas_compensadas["Horas a serem compensadas"])

# Calcular o saldo do banco de horas
total_horas_extras = extensao_jornada.groupby("Servidor")["Horas/minutos extras"].sum()
total_horas_compensadas = horas_compensadas.groupby("Servidor")["Horas a serem compensadas"].sum()

# Layout com containers
with st.container():
    col1, col2 = st.columns([1, 2])
    
    # Selecionar servidor
    with col1:
        servidor_selecionado = st.selectbox('Selecione um servidor:', total_horas_extras.index.unique())
    
    # Calcular o saldo do banco de horas para o servidor selecionado
    saldo = (
        total_horas_extras[servidor_selecionado] - total_horas_compensadas[servidor_selecionado]
        if servidor_selecionado in total_horas_extras.index and servidor_selecionado in total_horas_compensadas.index
        else pd.to_timedelta(0, unit='s')
    )

    # Mostrar saldo do banco de horas
    with col2:
        st.metric("Saldo Banco de Horas", format_timedelta(saldo))

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

