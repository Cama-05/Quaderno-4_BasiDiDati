import streamlit as st
import pandas as pd
from datetime import datetime
from utils import check_connection, execute_query

st.set_page_config(page_title="Istruttori", layout="wide")
st.title("👥 Gestione Istruttori")

if check_connection():
    # Filtri
    st.subheader("🔍 Filtra gli istruttori")
    col1, col2 = st.columns(2)

    with col1:
        cognome = st.text_input("Cognome")

    with col2:
        data_min = st.date_input(
            "Data di nascita minima",
            value=datetime(1960, 1, 1)
        )
        data_max = st.date_input(
            "Data di nascita massima",
            value=datetime(2000, 12, 31)
        )

    # Query per ottenere gli istruttori filtrati
    query = """
    SELECT *
    FROM ISTRUTTORE
    WHERE 1=1
    """

    if cognome:
        query += f" AND Cognome LIKE '%{cognome}%'"
    query += f" AND DataNascita > '{data_min}' AND  DataNascita < '{data_max}'"
    query += " ORDER BY Cognome, Nome"

    result = execute_query(st.session_state["connection"], query)
    df_istruttori = pd.DataFrame(result.fetchall(), columns=result.keys())

    if len(df_istruttori) == 0:
        st.warning("⚠️ Nessun istruttore trovato con i filtri selezionati")
    else:
        for _, row in df_istruttori.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"### 👤")
                with col2:
                    st.markdown(f"### {row['Nome']} {row['Cognome']}")
                    st.markdown(f"**Codice Fiscale:** {row['CodFisc']}")
                    st.markdown(f"**Data di Nascita:** {row['DataNascita']}")
                    st.markdown(f"**Email:** {row['Email']}")
                    if pd.notna(row['Telefono']):
                        st.markdown(f"**Telefono:** {row['Telefono']}")
                st.markdown("---") 