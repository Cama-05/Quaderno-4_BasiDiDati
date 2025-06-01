import streamlit as st
from utils import *

st.set_page_config(page_title="Nuovo Corso", layout="wide")

st.title("➕ Inserimento Nuovo Corso")
st.markdown("**Aggiungi un nuovo corso al database della palestra**")

if check_connection():
    # Informative section with expander
    with st.expander("📋 Informazioni sui corsi", expanded=False):
        st.markdown("I corsi nella palestra sono caratterizzati da un codice identificativo, nome, tipologia e livello di difficoltà.")

        # Layout with columns for structured info
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Requisiti per il codice corso:**")
            st.markdown("""
            - Deve iniziare con "CT"
            - Deve essere univoco nel sistema
            - Esempi validi: CT001, CT_YOGA, CT-PILATES
            """)

        with col_right:
            st.markdown("**Livelli disponibili:**")
            st.markdown("""
            - **Livello 1:** Principiante
            - **Livello 2:** Intermedio  
            - **Livello 3:** Avanzato
            - **Livello 4:** Esperto
            """)

    st.markdown("---")

    # Form for inserting new course
    with st.form("new_course_form", clear_on_submit=True):
        st.subheader("📊 Dati del nuovo corso")
        st.markdown("Inserisci le informazioni del corso che vuoi aggiungere al database:")

        # Form fields in columns
        form_col_left, form_col_right = st.columns(2)

        with form_col_left:
            st.markdown("**Identificazione del corso**")
            course_code = st.text_input(
                "Codice Corso",
                placeholder="Inserisci codice (es. CT001)"
            )

            course_name = st.text_input(
                "Nome del corso",
                placeholder="Inserisci il nome del corso"
            )

        with form_col_right:
            st.markdown("**Caratteristiche del corso**")
            course_type = st.text_input(
                "Tipo di corso",
                placeholder="Inserisci la tipologia"
            )

            course_level = st.number_input(
                "Livello (1-4)",
                min_value=1,
                max_value=4,
                step=1,
                value=1
            )

        # Submit button
        submitted = st.form_submit_button("🚀 Inserisci corso", use_container_width=True)

        if submitted:
            # Full validation of course data
            validation_errors = []

            # Check required fields
            if not course_code.strip():
                validation_errors.append("Il codice corso è obbligatorio")
            if not course_name.strip():
                validation_errors.append("Il nome del corso è obbligatorio")
            if not course_type.strip():
                validation_errors.append("Il tipo di corso è obbligatorio")

            # Check course code format
            if course_code.strip() and not course_code.strip().upper().startswith("CT"):
                validation_errors.append("Il codice corso deve iniziare con 'CT'")

            # Show validation errors
            if validation_errors:
                st.error("⚠️ **Errori di validazione rilevati:**")
                for error in validation_errors:
                    st.error(f"• {error}")
            else:
                # Attempt to insert course into DB
                try:
                    insert_query = f"""
                    INSERT INTO CORSI (CodC, Nome, Tipo, Livello)
                    VALUES ('{course_code.strip()}', '{course_name.strip()}', '{course_type.strip()}', {course_level})
                    """

                    execute_query(st.session_state["connection"], insert_query)

                    # Success message
                    st.success("✅ **Corso inserito con successo!**")
                    st.balloons()

                    # Additional info
                    st.info(f"Il corso **{course_name.strip()}** (codice: **{course_code.strip()}**) è stato aggiunto al database.")

                except Exception as e:
                    error_msg = str(e).lower()

                    # Handle duplicate key error
                    if "duplicate" in error_msg:
                        st.error("⚠️ **Errore: Codice corso già esistente**")
                        st.error(f"Il codice **{course_code.strip()}** è già presente nel database. Scegli un codice diverso.")
                    else:
                        # Generic error
                        st.error("⚠️ **Errore durante l'inserimento**")
                        st.error(f"Si è verificato un problema: {str(e)}")

    st.markdown("---")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")