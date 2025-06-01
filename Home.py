import streamlit as st
import pandas as pd
import altair as alt
from utils import *

st.set_page_config(
    page_title="Gym App",
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
    col1, col2 = st.columns(2)

    # Query for area chart
    query_schedule_by_time = """
    SELECT OraInizio, COUNT(*) as NumeroLezioni
    FROM Programma
    GROUP BY OraInizio
    ORDER BY OraInizio
    """

    result_time = execute_query(st.session_state["connection"], query_schedule_by_time)
    df_schedule_by_time = pd.DataFrame(result_time)

    # Query for bar chart
    query_schedule_by_day = """
    SELECT Giorno, COUNT(*) as NumeroLezioni
    FROM Programma
    GROUP BY Giorno
    """

    result_day = execute_query(st.session_state["connection"], query_schedule_by_day)
    df_schedule_by_day = pd.DataFrame(result_day)

    with col1:
        # Area Chart: number of classes per time slot
        st.subheader("📈 Lezioni per slot orario")
        st.area_chart(
            df_schedule_by_time.set_index('OraInizio'),
            use_container_width=True
        )

    with col2:
        # Bar Chart: number of classes per weekday
        st.subheader("📊 Lezioni per giorno della settimana")

        chart = alt.Chart(df_schedule_by_day).mark_bar().encode(
            x=alt.X('Giorno:N', title='Giorno della setttimana'),
            y=alt.Y('NumeroLezioni:Q', title='Numero di Lezioni'),
            tooltip=['Giorno', 'NumeroLezioni']
        ).properties(
            height=400
        )

        st.altair_chart(chart, use_container_width=True)