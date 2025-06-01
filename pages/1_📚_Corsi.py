import streamlit as st
import pandas as pd
from utils import *

st.set_page_config(page_title="Corsi", layout="wide")
st.title("📚 Gestione Corsi")

if check_connection():
    # Query to get distinct course types
    result_types = execute_query(st.session_state["connection"], "SELECT DISTINCT Tipo FROM CORSI ORDER BY Tipo")
    course_types = [dict(zip(result_types.keys(), result)) for result in result_types]
    
    result_levels = execute_query(st.session_state["connection"], "SELECT DISTINCT Livello FROM CORSI ORDER BY Livello")
    levels = [dict(zip(result_levels.keys(), result)) for result in result_levels]

    # Metrics
    result_count = execute_query(st.session_state["connection"], "SELECT COUNT(*) as count FROM CORSI")
    total_courses = [dict(zip(result_count.keys(), result)) for result in result_count]
    total_types = len(course_types)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Numero totale corsi", total_courses[0].get('count'))
    with col2:
        st.metric("Numero tipi di corsi", total_types)

    # Filters
    st.subheader("🔍 Filtra i corsi")
    col1, col2 = st.columns(2)

    with col1:
        selected_types = st.multiselect("Seleziona il tipo di corso", options=[tipo.get('tipo') for tipo in course_types])

    with col2:
        levels_values = [level.get('Livello') for level in levels]
        min_level = st.slider("Livello minimo", min_value=min(levels_values), max_value=max(levels_values))
        max_level = st.slider("Livello massimo", min_value=min(levels_values), max_value=max(levels_values), value=max(levels_values))
        if min_level > max_level:
            st.warning("⚠️Il livello minimo non può essere maggiore del livello massimo")

    # Query to get filtered courses
    query = f"""
    SELECT c.CodC, c.Nome, c.Tipo, c.Livello
    FROM CORSI c
    WHERE c.Livello >= {min_level} AND c.Livello <= {max_level}
    """

    # Append type filter to the query
    if max_level > min_level:
        if selected_types:
            query += " AND ("
            for i, tipo in enumerate(selected_types):
                query += f"c.Tipo = '{tipo}'"
                if i < len(selected_types) - 1:
                    query += "OR "
            query += ")"
    
    query += " GROUP BY c.CodC"

    result_courses = execute_query(st.session_state["connection"], query)
    df_courses = pd.DataFrame(result_courses)

    if len(df_courses) == 0:
        if max_level > min_level:
            st.warning("⚠️ Nessun corso trovato con i filtri selezionati")
    else:
        st.dataframe(df_courses[['CodC', 'Nome', 'Tipo', 'Livello']], use_container_width=True, hide_index=True)
        
        with st.expander("📅 Programma lezioni per i corsi selezionati"):
            if len(df_courses) > 0:
                # Create a list of filtered course codes
                course_codes = tuple(df_courses['CodC'].tolist())
                
                # Query to get class schedule details
                query_schedule = f"""
                SELECT 
                    c.CodC as 'Codice Corso',
                    c.Nome as 'Nome Corso',
                    CONCAT(i.Nome, ' ', i.Cognome) as 'Istruttore',
                    i.Email,
                    p.Giorno,
                    p.OraInizio as 'Orario Inizio',
                    p.Durata as 'Durata',
                    p.Sala
                FROM CORSI c,PROGRAMMA p, ISTRUTTORE i
                WHERE c.CodC = p.CodC
                AND p.CodFisc = i.CodFisc
                """
                # Add course filter to the schedule query
                if max_level > min_level:
                    if len(course_codes) > 0:
                        query_schedule += " AND ("
                        for i, code in enumerate(course_codes):
                            query_schedule += f"c.CodC = '{code}'"
                            if i < len(course_codes) - 1:
                                query_schedule += "OR "
                        query_schedule += ")"

                query_schedule += f"ORDER BY c.Nome, p.OraInizio"
                
                result_schedule = execute_query(st.session_state["connection"], query_schedule)
                df_schedule = pd.DataFrame(result_schedule)
                
                if len(df_schedule) > 0:
                    st.dataframe(
                        df_schedule,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Nessuna lezione programmata per i corsi selezionati")
            else:
                st.info("Nessun corso selezionato")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")
