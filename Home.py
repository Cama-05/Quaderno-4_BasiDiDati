import streamlit as st
import pandas as pd
from utils import check_connection, execute_query

st.set_page_config(
    page_title="Palestra App",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://dbdmg.polito.it/',
        'Report a bug': "https://dbdmg.polito.it/",
        'About': "# Corso di *Basi di Dati*"
    }
)

st.title("🏋️‍♂️ Gestione Palestra")

st.markdown("""
### Benvenuto nell'applicazione di gestione della palestra!
Questa applicazione permette di:
- Visualizzare le lezioni programmate
- Gestire i corsi disponibili
- Visualizzare gli istruttori
- Inserire nuovi corsi
- Programmare nuove lezioni
""")

if check_connection():
    # Query per ottenere i dati per i grafici
    query_lezioni = """
    SELECT Giorno, OraInizio, COUNT(*) as NumeroLezioni
    FROM PROGRAMMA
    GROUP BY Giorno, OraInizio
    ORDER BY Giorno, OraInizio
    """

    result = execute_query(st.session_state["connection"], query_lezioni)
    df_lezioni = pd.DataFrame(result.fetchall(), columns=result.keys())

    # Area Chart per le lezioni per slot temporale
    st.subheader("📈 Distribuzione delle lezioni per slot temporale")
    st.area_chart(
        df_lezioni.pivot(index='OraInizio', columns='Giorno', values='NumeroLezioni'),
        use_container_width=True
    )

    # Bar Chart per le lezioni per giorno
    st.subheader("📊 Distribuzione delle lezioni per giorno della settimana")
    query_giorni = """
    SELECT Giorno, COUNT(*) as NumeroLezioni
    FROM PROGRAMMA
    GROUP BY Giorno
    """
    
    result_giorni = execute_query(st.session_state["connection"], query_giorni)
    giorni_lezioni = pd.DataFrame(result_giorni.fetchall(), columns=result_giorni.keys())

    # Mappa per aggiungere il prefisso numerico per far comparire i giorni in ordine sull'istogramma
    mapping = {
        'Lunedì': '1_Lunedì',
        'Martedì': '2_Martedì',
        'Mercoledì': '3_Mercoledì',
        'Giovedì': '4_Giovedì',
        'Venerdì': '5_Venerdì'
    }

    giorni_lezioni['GiornoOrd'] = giorni_lezioni['Giorno'].map(mapping)
    giorni_lezioni = giorni_lezioni.sort_values('GiornoOrd')

    st.bar_chart(
        data=giorni_lezioni,
        x='Giorno',
        y='NumeroLezioni',
        use_container_width=True
    )