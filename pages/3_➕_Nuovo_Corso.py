import streamlit as st
from utils import check_connection, execute_query

st.set_page_config(page_title="Nuovo Corso", layout="wide")

st.title("➕ Inserimento Nuovo Corso")
st.markdown("**Aggiungi un nuovo corso al database della palestra**")

if check_connection():
    # Sezione informativa con expander
    with st.expander("📋 Informazioni sui corsi", expanded=False):
        st.markdown("I corsi nella palestra sono caratterizzati da un codice identificativo, nome, tipologia e livello di difficoltà.")
        
        # Layout con colonne per organizzare le informazioni
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Requisiti per il codice corso:**")
            st.markdown("""
            - Deve iniziare con "CT"
            - Deve essere univoco nel sistema
            - Esempi validi: CT001, CT_YOGA, CT-PILATES
            """)
        
        with col2:
            st.markdown("**Livelli disponibili:**")
            st.markdown("""
            - **Livello 1:** Principiante
            - **Livello 2:** Intermedio  
            - **Livello 3:** Avanzato
            - **Livello 4:** Esperto
            """)

    st.markdown("---")

    # Form per l'inserimento del nuovo corso
    with st.form("nuovo_corso_form", clear_on_submit=True):
        st.subheader("📊 Dati del nuovo corso")
        st.markdown("Inserisci le informazioni del corso che vuoi aggiungere al database:")
        
        # Colonne per i campi del form
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            st.markdown("**Identificazione del corso**")
            codc = st.text_input(
                "Codice Corso",
                placeholder="Inserisci codice (es. CT001)"
            )
            
            nome = st.text_input(
                "Nome del corso",
                placeholder="Inserisci il nome del corso"
            )
        
        with col_form2:
            st.markdown("**Caratteristiche del corso**")
            tipo = st.text_input(
                "Tipo di corso",
                placeholder="Inserisci la tipologia"
            )
            
            livello = st.number_input(
                "Livello (1-4)",
                min_value=1,
                max_value=4,
                step=1,
                value=1
            )

        # Bottone di submit del form
        submitted = st.form_submit_button("🚀 Inserisci corso", use_container_width=True)

        if submitted:
            # Validazione completa dei dati come richiesto dalle specifiche
            errori = []
            
            # Verifica che tutti i campi siano valorizzati
            if not codc.strip():
                errori.append("Il codice corso è obbligatorio")
            if not nome.strip():
                errori.append("Il nome del corso è obbligatorio")
            if not tipo.strip():
                errori.append("Il tipo di corso è obbligatorio")
            
            # Verifica struttura codice corso (deve iniziare con "CT")
            if codc.strip() and not codc.strip().upper().startswith("CT"):
                errori.append("Il codice corso deve iniziare con 'CT'")
            
            # Visualizzazione errori di validazione
            if errori:
                st.error("⚠️ **Errori di validazione rilevati:**")
                for errore in errori:
                    st.error(f"• {errore}")
            else:
                # Tentativo di inserimento nel database
                try:
                    # Query di inserimento
                    query = f"""
                    INSERT INTO CORSI (CodC, Nome, Tipo, Livello)
                    VALUES ('{codc.strip()}', '{nome.strip()}', '{tipo.strip()}', {livello})
                    """
                    
                    execute_query(st.session_state["connection"], query)# Il commit viene fatto automaticamente nella funzione execute_query
                    
                    # Messaggio di successo
                    st.success("✅ **Corso inserito con successo!**")
                    st.balloons()
                    
                    # Informazioni aggiuntive sul corso inserito
                    st.info(f"Il corso **{nome.strip()}** (codice: **{codc.strip()}**) è stato aggiunto al database.")

                except Exception as e:
                    error_message = str(e).lower()
                    
                    # Gestione errore chiave duplicata
                    if "duplicate" in error_message:
                        st.error("⚠️ **Errore: Codice corso già esistente**")
                        st.error(f"Il codice **{codc.strip()}** è già presente nel database. Scegli un codice diverso.")
                    else:
                        # Altri errori generici
                        st.error("⚠️ **Errore durante l'inserimento**")
                        st.error(f"Si è verificato un problema: {str(e)}")

    st.markdown("---")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")