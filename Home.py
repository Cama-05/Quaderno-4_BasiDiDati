import streamlit as st
import pandas as pd
import altair as alt
from utils import *

st.set_page_config(
    page_title="Palestra App",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Cama-05',
        'Report a bug': "https://github.com/Cama-05",
        'About': "# Corso di *Basi di Dati*"
    }
)

st.title("🏋️‍♂️ Gestione Palestra con :red[Streamlit]")

st.markdown("""
### Benvenuto nell'applicazione di gestione della palestra!
Questa applicazione permette di:
* Visualizzare le lezioni programmate
* Gestire i corsi disponibili
* Visualizzare gli istruttori
* Inserire nuovi corsi
* Programmare nuove lezioni
""")

if check_connection():
    col1,col2=st.columns(2)

    # Query per area chart
    query_lezioni = """
    SELECT OraInizio, COUNT(*) as NumeroLezioni
    FROM PROGRAMMA
    GROUP BY OraInizio
    ORDER BY OraInizio
    """

    result = execute_query(st.session_state["connection"], query_lezioni)
    df_lezioni = pd.DataFrame(result)

    #Query per bar chart , con mapping dei nomi dei giorni in modo da ordinarli nella rappresentazione nel bar chart
    query_giorni ="""
    SELECT Giorno, COUNT(*) as NumeroLezioni
    FROM PROGRAMMA
    GROUP BY Giorno
    """

    result_giorni = execute_query(st.session_state["connection"], query_giorni)
    giorni_lezioni = pd.DataFrame(result_giorni)


    with col1:
        # Area Chart per le lezioni per slot temporale
        st.subheader("📈 Lezioni per slot temporale")
        st.area_chart(
            df_lezioni.set_index('OraInizio'),
            use_container_width=True
        )

    with col2:
        # Bar Chart per le lezioni per giorno
        st.subheader("📊 Lezioni per giorno della settimana")

        # Ordine esplicito dei giorni
        giorni_settimana = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

        chart = alt.Chart(giorni_lezioni).mark_bar().encode(
            x=alt.X('Giorno:N', sort=giorni_settimana, title='Giorno della settimana'),
            y=alt.Y('NumeroLezioni:Q', title='Numero di lezioni'),
            tooltip=['Giorno', 'NumeroLezioni']
        ).properties(
            height=400
        )

        st.altair_chart(chart, use_container_width=True)