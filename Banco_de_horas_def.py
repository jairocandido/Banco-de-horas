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

# Permitir upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

try:
    if uploaded_file:
        # Carregar os dados a partir do arquivo enviado
        extensao_jornada = pd.read_excel(uploaded_file, sheet_name="EXTENSÃO DE JORNADA")
        horas_compensadas = pd.read_excel(uploaded_file, sheet_name="HORAS COMPENSADAS")
    else:
        # Se nenhum arquivo for enviado, usar a URL do GitHub
        github_url = "https://raw.githubusercontent.com/jairocandido/Banco-de-horas/master/Recursos/Extens%C3%A3o%20de%20jornada%20x%20compensa%C3%A7%C3%A3o.xlsx"
        response = requests.get(github_url)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        content = BytesIO(response.content)
        extensao_jornada = pd.read_excel(content, sheet_name="EXTENSÃO DE JORNADA")
        horas_compensadas = pd.read_excel(content, sheet_name="HORAS COMPENSADAS")

    # Renomear a coluna 'Cod_Guarda' para 'Servidor'
    extensao_jornada = extensao_jornada.rename(columns={'Cod_Guarda': 'Servidor'})

    # Tratar dados faltantes
    extensao_jornada["Horas/minutos extras"] = extensao_jornada["Horas/minutos extras"].fillna("0:00:00")
    horas_compensadas["Horas a serem compensadas"] = horas_compensadas["Horas a serem compensadas"].fillna("0:00:00")
    extensao_jornada["Servidor"] = extensao_jornada["Servidor"].fillna("Dados Faltantes")
    horas_compensadas["Servidor"] = horas_compensadas["Servidor"].fillna("Dados Faltantes")

    # Restante do seu código permanece inalterado
    # ...

    # Calcular o saldo do banco de horas
    total_horas_extras = extensao_jornada.groupby("Servidor")["Horas/minutos extras"].sum()
    total_horas_compensadas = horas_compensadas.groupby("Servidor")["Horas a serem compensadas"].sum()
    banco_de_horas = pd.DataFrame({
        "Total Horas Extras": total_horas_extras,
        "Total Horas Compensadas": total_horas_compensadas
    })
    # ...

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

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")
