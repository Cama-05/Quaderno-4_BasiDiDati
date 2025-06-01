import streamlit as st
import pandas as pd
from utils import *

st.set_page_config(page_title="Corsi", layout="wide")
st.title("📚 Gestione Corsi")

if check_connection():
    # Query per ottenere i tipi di corsi disponibili
    result_tipi = execute_query(st.session_state["connection"], "SELECT DISTINCT Tipo FROM CORSI ORDER BY Tipo")
    tipi_corsi = [dict(zip(result_tipi.keys(), result)) for result in result_tipi]
    
    result_livelli = execute_query(st.session_state["connection"], "SELECT DISTINCT Livello FROM CORSI ORDER BY Livello")
    livelli = [dict(zip(result_livelli.keys(), result)) for result in result_livelli]

    # Metriche
    result_count = execute_query(st.session_state["connection"], "SELECT COUNT(*) as count FROM CORSI")
    num_corsi = [dict(zip(result_count.keys(), result)) for result in result_count]
    num_tipi = len(tipi_corsi)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Numero totale corsi", num_corsi[0]['count'])
    with col2:
        st.metric("Numero tipi di corsi", num_tipi)

    # Filtri
    st.subheader("🔍 Filtra i corsi")
    col1, col2 = st.columns(2)

    with col1:
        tipo_selezionato = st.multiselect("Seleziona il tipo di corso", options=[tipo.get('Tipo') for tipo in tipi_corsi])

    with col2:
        livelli=[livello.get('Livello') for livello in livelli]
        livello_min = st.slider("Livello minimo",min_value=min(livelli),max_value=max(livelli))
        livello_max = st.slider("Livello massimo",min_value=min(livelli),max_value=max(livelli), value=max(livelli))
        if(livello_min > livello_max):
            st.warning("⚠️Il livello minimo non può essere maggiore del livello massimo")

    # Query per ottenere i corsi filtrati
    query =f"""
    SELECT c.CodC, c.Nome, c.Tipo, c.Livello
    FROM CORSI c
    WHERE c.Livello >= {livello_min} AND c.Livello <= {livello_max}
    """

    #Completamento opportuno della query
    if livello_max > livello_min:
        if tipo_selezionato:
            query += " AND ("
            for (i,tipo) in enumerate(tipo_selezionato):
                query += f"c.Tipo = '{tipo}'"
                if i < len(tipo_selezionato) - 1:
                    query += "OR "
            query += ")"
    
    query += " GROUP BY c.CodC"


    result_corsi = execute_query(st.session_state["connection"], query)
    df_corsi = pd.DataFrame(result_corsi)

    if len(df_corsi) == 0:
        if livello_max > livello_min:
            st.warning("⚠️ Nessun corso trovato con i filtri selezionati")
    else:
        st.dataframe(df_corsi[['CodC', 'Nome', 'Tipo', 'Livello']], use_container_width=True, hide_index=True)
        
        with st.expander("📅 Programma lezioni per i corsi selezionati"):
            if len(df_corsi) > 0:
                # Creo una lista dei codici corso filtrati
                codici_corsi = tuple(df_corsi['CodC'].tolist())
                
                # Nuova query per ottenere i dettagli delle lezioni
                query_lezioni = f"""
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
                #Completamento opportuno della query
                if livello_max > livello_min:
                    if len(codici_corsi)>0:
                        query_lezioni+= " AND ("
                        for (i,codice) in enumerate(codici_corsi):
                            query_lezioni+= f"c.CodC = '{codice}'"
                            if i < len(codici_corsi) - 1:
                                query_lezioni+= "OR "
                    query_lezioni+= ")"

                query_lezioni +=f"ORDER BY c.Nome, p.OraInizio"
                
                result_lezioni = execute_query(st.session_state["connection"], query_lezioni)
                df_lezioni = pd.DataFrame(result_lezioni)
                
                if len(df_lezioni) > 0:
                    st.dataframe(
                        df_lezioni,
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