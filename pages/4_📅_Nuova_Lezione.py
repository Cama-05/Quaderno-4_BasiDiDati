import streamlit as st
import pandas as pd
from utils import check_connection, execute_query

st.set_page_config(page_title="Nuova Lezione", layout="wide")
st.title("📅 Inserimento Nuova Lezione")

if check_connection():
    # Ottieni la lista degli istruttori
    result_istruttori = execute_query(st.session_state["connection"], 
        "SELECT CodFisc, CONCAT(Nome, ' ', Cognome) as NomeCompleto FROM ISTRUTTORE ORDER BY Cognome, Nome")
    istruttori = pd.DataFrame(result_istruttori.fetchall(), columns=result_istruttori.keys())
    istruttori_dict = dict(zip(istruttori['NomeCompleto'], istruttori['CodFisc']))

    # Ottieni la lista dei corsi
    result_corsi = execute_query(st.session_state["connection"], 
        "SELECT CodC, Nome FROM CORSI ORDER BY Nome")
    corsi = pd.DataFrame(result_corsi.fetchall(), columns=result_corsi.keys())
    corsi_dict = dict(zip(corsi['Nome'], corsi['CodC']))

    with st.form("nuova_lezione_form"):
        st.subheader("Inserisci i dati della nuova lezione")
        
        col1, col2 = st.columns(2)
        
        with col1:
            istruttore = st.selectbox("Istruttore", options=list(istruttori_dict.keys()))
            corso = st.selectbox("Corso", options=list(corsi_dict.keys()))
            giorno = st.selectbox("Giorno", options=['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì'])
        
        with col2:
            ora_inizio = st.slider("Ora inizio", min_value=8, max_value=20, value=9)
            durata = st.slider("Durata (minuti)", min_value=30, max_value=60, value=60, step=30)
            sala = st.text_input("Sala")
        
        submitted = st.form_submit_button("Inserisci lezione")
        
        if submitted:
            if not sala:
                st.error("⚠️ Il campo Sala deve essere compilato")
            else:
                # Verifica se esiste già una lezione per lo stesso corso nello stesso giorno
                query_check = """
                SELECT COUNT(*) as count
                FROM PROGRAMMA
                WHERE CodC = %s AND Giorno = %s
                """
                result_check = execute_query(st.session_state["connection"], query_check, 
                    (corsi_dict[corso], giorno))
                count = pd.DataFrame(result_check.fetchall(), columns=result_check.keys()).iloc[0]['count']
                
                if count > 0:
                    st.error("⚠️ Esiste già una lezione per questo corso in questo giorno")
                else:
                    try:
                        query = """
                        INSERT INTO PROGRAMMA (CodFisc, Giorno, OraInizio, Durata, CodC, Sala)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        execute_query(st.session_state["connection"], query, (
                            istruttori_dict[istruttore],
                            giorno,
                            ora_inizio,
                            durata,
                            corsi_dict[corso],
                            sala
                        ))
                        st.success("✅ Lezione inserita con successo!")
                    except Exception as e:
                        st.error(f"⚠️ Errore durante l'inserimento: {str(e)}") 