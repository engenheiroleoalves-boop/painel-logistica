import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
def conecta_google_sheets():
    # O Streamlit Cloud vai ler as credenciais de um lugar seguro chamado "Secrets"
    info_chaves = dict(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info_chaves, scope)
    client = gspread.authorize(creds)
    return client.open("Dados_Logistica").sheet1

# --- INTERFACE ---
st.set_page_config(page_title="Logística Pro", layout="wide")

try:
    sheet = conecta_google_sheets()
except Exception as e:
    st.error("Erro na conexão. Verifique as chaves de segurança.")
    st.stop()

# Layout do Painel
st.title("🚀 Operação Logística")

menu = st.sidebar.selectbox("Navegação", ["Inserir Dados", "Visualizar Dashboard"])

if menu == "Inserir Dados":
    st.header("📥 Registro de Atividade")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", datetime.date.today()).strftime('%d/%m/%Y')
            operador = st.selectbox("Operador", ["João Silva", "Maria Souza", "Carlos Lima"])
        with col2:
            operacao = st.selectbox("Operação", ["Recebimento", "Picking", "Expedição"])
            quantidade = st.number_input("Quantidade", min_value=1)
        
        status = st.select_slider("Status da Operação", options=["Pendente", "Com Avaria", "Concluído"])
        botao = st.form_submit_button("REGISTRAR")

        if botao:
            sheet.append_row([data, operador, operacao, quantidade, status])
            st.success(f"Registrado: {quantidade} itens em {operacao} por {operador}")

elif menu == "Visualizar Dashboard":
    st.header("📊 Performance da Operação")
    dados = sheet.get_all_records()
    if dados:
        df = pd.DataFrame(dados)
        
        # Cards de Resumo
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Processado", df['Quantidade'].sum())
        m2.metric("Média por Operação", f"{df['Quantidade'].mean():.1f}")
        m3.metric("Ocorrências", len(df[df['Status'] == 'Com Avaria']))

        # Gráficos
        st.subheader("Produção por Operador")
        st.bar_chart(df.groupby('Operador')['Quantidade'].sum())
        
        st.subheader("Histórico Recente")
        st.table(df.tail(10))
    else:
        st.info("Ainda não há dados na planilha.")
