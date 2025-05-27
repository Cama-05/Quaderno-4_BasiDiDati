import streamlit as st
from utils import check_connection, execute_query

st.set_page_config(page_title="Nuovo Corso", layout="wide")
st.title("➕ Inserimento Nuovo Corso")

if check_connection():
    with st.form("nuovo_corso_form"):
        st.subheader("Inserisci i dati del nuovo corso")
        
        codc = st.text_input("Codice Corso (deve iniziare con 'CT')")
        nome = st.text_input("Nome del corso")
        tipo = st.text_input("Tipo di corso")
        livello = st.number_input("Livello (1-4)", min_value=1, max_value=4, step=1)
        
        submitted = st.form_submit_button("Inserisci corso")
        
        if submitted:
            if not all([codc, nome, tipo]):
                st.error("⚠️ Tutti i campi devono essere compilati")
            elif not codc.startswith("CT"):
                st.error("⚠️ Il codice corso deve iniziare con 'CT'")
            else:
                try:
                    query = """
                    INSERT INTO CORSI (CodC, Nome, Tipo, Livello)
                    VALUES (%s, %s, %s, %s)
                    """
                    execute_query(st.session_state["connection"], query, (codc, nome, tipo, livello))
                    st.success("✅ Corso inserito con successo!")
                except Exception as e:
                    if "Duplicate entry" in str(e):
                        st.error("⚠️ Errore: Codice corso già esistente")
                    else:
                        st.error(f"⚠️ Errore durante l'inserimento: {str(e)}") 