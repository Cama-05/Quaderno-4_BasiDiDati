import streamlit as st
import pandas as pd
import datetime
from utils import *

st.set_page_config(page_title="Nuova Lezione", layout="wide")

st.title("📅 Inserimento Nuova Lezione")

if check_connection():
    # Ottieni la lista degli istruttori con codice fiscale
    result_istruttori = execute_query(st.session_state["connection"],
        "SELECT CodFisc, CONCAT(Nome, ' ', Cognome) as NomeCompleto FROM ISTRUTTORE ORDER BY Cognome, Nome")
    istruttori = pd.DataFrame(result_istruttori)
    
    # Ottieni la lista dei corsi
    result_corsi = execute_query(st.session_state["connection"], "SELECT CodC, Nome FROM CORSI ORDER BY Nome")
    corsi = pd.DataFrame(result_corsi)


    #FORM
    with st.form("nuova_lezione_form"):
        st.subheader("📝 Inserisci i dati della nuova lezione")
        
        col1, col2 = st.columns(2)
        with col1:
            #Selezione Istruttore
            istruttore_selezionato = st.selectbox(
                "👨‍🏫 Istruttore (Codice Fiscale)", 
                options=istruttori['CodFisc'].tolist()
            )
            #Selezione Corso
            corso_selezionato = st.selectbox(
                "🏋️ Corso", 
                options=corsi['CodC'].tolist()
            )
        with col2:
            #Selezione orario inizo
            orario_inizio = st.time_input(
                "🕒 Orario di inizio",
                value=datetime.time(),
                step=datetime.timedelta(minutes=15)
            )
            #Selezione durata
            durata = st.slider(
                "⏱️ Durata (minuti)", 
                min_value=15, 
                max_value=60, 
                value=60, 
                step=15
            )
        # Nuova riga per avere Giorno e Sala allineati
        col_giorno, col_sala = st.columns(2)
        with col_giorno:
            #Selezione giorno
            giorno = st.selectbox(
                "📅 Giorno", 
                options=['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']
            )
        with col_sala:
            #Inserimento sala
            sala = st.text_input(
                "🏢 Sala", 
                placeholder="Es: Sala A, Palestra 1, etc."
            )

        #Tasto submit
        submitted = st.form_submit_button("✅ Inserisci lezione", use_container_width=True)
        
        #Gestione degli errori
        if submitted:
            errori = []
            if not sala.strip():
                errori.append("Il campo Sala deve essere compilato")
            
            if errori:
                st.error("⚠️ Errori di validazione:")
                for errore in errori:
                    st.error(f"• {errore}")
            else:
                codfisc_istruttore = istruttore_selezionato
                codc_corso = corso_selezionato
                # Formatto l'orario in hh:mm:ss
                ora_inizio_str = orario_inizio.strftime("%H:%M:%S")
                #Controllo che non ci sia un'altra lezione dello stesso corso nello stesso giorno
                query_check = f"""
                SELECT COUNT(*) as count
                FROM PROGRAMMA 
                WHERE CodC = '{codc_corso}' AND Giorno = '{giorno}'
                """
                try:
                    result_check = execute_query(st.session_state["connection"], query_check)
                    result = pd.DataFrame(result_check) #Dataframe di una sola riga e colonna
                    if result.iloc[0]['count']>0: #Accesso e controllo al df
                        st.error(f"⚠️ Esiste già una lezione per il corso '{codc_corso}' il {giorno}")
                    else:
                        query_insert = f"""
                        INSERT INTO PROGRAMMA (CodFisc, Giorno, OraInizio, Durata, CodC, Sala)
                        VALUES ('{codfisc_istruttore}', '{giorno}', '{ora_inizio_str}', {durata}, '{codc_corso}', '{sala.strip()}')
                        """
                        execute_query(st.session_state["connection"], query_insert)
                        st.success(f"✅ Lezione inserita con successo! Corso '{codc_corso}' il {giorno} alle {ora_inizio_str} in {sala}")

                        with st.expander("📋 Riepilogo lezione inserita", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Istruttore (CodFisc):** {codfisc_istruttore}")
                                st.write(f"**Corso:** {codc_corso}")
                                st.write(f"**Giorno:** {giorno}")
                            with col2:
                                st.write(f"**Orario:** {ora_inizio_str}")
                                st.write(f"**Durata:** {durata} minuti")
                                st.write(f"**Sala:** {sala}")
                except Exception as e:
                    st.error(f"⚠️ Errore durante l'inserimento: {str(e)}")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")
