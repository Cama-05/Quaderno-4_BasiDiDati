import streamlit as st
import pandas as pd
from utils import check_connection, execute_query

st.set_page_config(page_title="Corsi", layout="wide")
st.title("📚 Gestione Corsi")

if check_connection():
    # Query per ottenere i tipi di corsi disponibili
    result_tipi = execute_query(st.session_state["connection"], "SELECT DISTINCT Tipo FROM CORSI ORDER BY Tipo")
    tipi_corsi = pd.DataFrame(result_tipi.fetchall(), columns=result_tipi.keys())
    
    result_livelli = execute_query(st.session_state["connection"], "SELECT DISTINCT Livello FROM CORSI ORDER BY Livello")
    livelli = pd.DataFrame(result_livelli.fetchall(), columns=result_livelli.keys())

    # Metriche
    result_count = execute_query(st.session_state["connection"], "SELECT COUNT(*) as count FROM CORSI")
    num_corsi = pd.DataFrame(result_count.fetchall(), columns=result_count.keys()).iloc[0]['count']
    num_tipi = len(tipi_corsi)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Numero totale corsi", num_corsi)
    with col2:
        st.metric("Numero tipi di corsi", num_tipi)

    # Filtri
    st.subheader("🔍 Filtra i corsi")
    col1, col2 = st.columns(2)

    with col1:
        tipo_selezionato = st.multiselect(
            "Seleziona il tipo di corso",
            options=tipi_corsi['Tipo'].tolist()
        )

    with col2:
        livello_min = st.select_slider(
            "Livello minimo",
            options=livelli['Livello'].tolist(),
            value=min(livelli['Livello'].tolist())
        )
        livello_max = st.select_slider(
            "Livello massimo",
            options=livelli['Livello'].tolist(),
            value=max(livelli['Livello'].tolist())
        )

    # Query per ottenere i corsi filtrati
    query = """
    SELECT c.*, 
           CONCAT(i.Nome, ' ', i.Cognome) as Istruttore,
           i.Email
    FROM CORSI c
    LEFT JOIN PROGRAMMA p ON c.CodC = p.CodC
    LEFT JOIN ISTRUTTORE i ON p.CodFisc = i.CodFisc
    WHERE 1=1
    """

    if tipo_selezionato:
        query += f" AND c.Tipo IN {tuple(tipo_selezionato)}"
    query += f" AND c.Livello BETWEEN {livello_min} AND {livello_max}"
    query += " GROUP BY c.CodC"

    result_corsi = execute_query(st.session_state["connection"], query)
    df_corsi = pd.DataFrame(result_corsi.fetchall(), columns=result_corsi.keys()) #ATTENZIONE CONTROLLLA

    if len(df_corsi) == 0:
        st.warning("⚠️ Nessun corso trovato con i filtri selezionati")
    else:
        st.dataframe(df_corsi[['CodC', 'Nome', 'Tipo', 'Livello']], use_container_width=True)
        
        with st.expander("📅 Programma lezioni per i corsi selezionati"):
            if len(df_corsi) > 0:
                st.dataframe(df_corsi[['Nome', 'Istruttore', 'Email']], use_container_width=True) 