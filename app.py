import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Sunflower Land - Preços",
    page_icon="🌻",
    layout="wide"
)

# Título principal
st.title("🌻 Sunflower Land - Preços")

# Carregar variáveis de ambiente (se existirem)
load_dotenv()

# Configurações do banco de dados remoto
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sunflower_trade')

# Função para conectar ao banco de dados
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para obter a lista de itens
@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_all_items():
    connection = connect_to_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT item_name FROM item_prices ORDER BY item_name")
        items = [row[0] for row in cursor.fetchall()]
        return items
    except mysql.connector.Error as err:
        st.error(f"Erro ao buscar itens: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Função para obter o histórico de preços de um item
def get_item_price_history(item_name, days=30):
    connection = connect_to_db()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
        SELECT 
            item_name, 
            p2p_price, 
            usd_price,
            timestamp 
        FROM 
            item_prices 
        WHERE 
            item_name = %s AND 
            timestamp BETWEEN %s AND %s 
        ORDER BY 
            timestamp
        """
        
        cursor.execute(query, (item_name, start_date, end_date))
        results = cursor.fetchall()
        
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame(columns=['item_name', 'p2p_price', 'usd_price', 'timestamp'])
    except mysql.connector.Error as err:
        st.error(f"Erro ao buscar histórico de preços: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Carregar a lista de itens
items = get_all_items()

# Criar o seletor de itens
if items:
    selected_item = st.selectbox(
        "Selecione um item",
        options=items,
        index=0 if "Apple" in items else 0,
        format_func=lambda x: x  # Exibir o nome do item como está
    )
    
    # Criar controle deslizante para selecionar o número de dias
    days = st.slider("Últimos dias", min_value=1, max_value=90, value=30)
    
    # Obter dados do item selecionado
    df = get_item_price_history(selected_item, days)
    
    if df is not None and not df.empty:
        # Converter a coluna timestamp para datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Criar o gráfico
        st.subheader(f"Preços de {selected_item} nos últimos {days} dias")
        
        # Criar o gráfico usando Plotly
        fig = go.Figure()
        
        # Adicionar linha para preço P2P (Flower)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['p2p_price'],
            mode='lines',
            name='Preço em Flower',
            line=dict(color='#3366cc', width=3)
        ))
        
        # Adicionar linha para preço USD (se disponível)
        if 'usd_price' in df.columns and df['usd_price'].notnull().any():
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['usd_price'],
                mode='lines',
                name='Preço em USD',
                line=dict(color='#cc3366', width=3, dash='dot'),
                yaxis="y2"
            ))
            st.info("✅ Dados de preço em USD disponíveis para este item.")
        else:
            st.warning("⚠️ Dados de preço em USD não disponíveis para este item.")
        
        # Configurar o layout do gráfico
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Preço em Flower",
            legend_title="Tipo de Preço",
            hovermode="x unified",
            height=600,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis2=dict(
                title="Preço em USD",
                overlaying="y",
                side="right"
            )
        )
        
        # Mostrar o gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar os dados brutos (opcional, em um expansor)
        with st.expander("Ver dados brutos"):
            st.dataframe(df)
            
    else:
        st.warning(f"Nenhum dado disponível para {selected_item} nos últimos {days} dias.")
else:
    st.error("Não foi possível carregar a lista de itens. Verifique a conexão com o banco de dados.")

# Rodapé
st.divider()
st.caption("Dados extraídos do banco de dados Sunflower Trade") 