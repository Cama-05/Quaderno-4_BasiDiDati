import streamlit as st
import pandas as pd
import datetime
from utils import *

st.set_page_config(page_title="Nuova Lezione", layout="wide")

st.title("📅 Inserimento Nuova Lezione")

if check_connection():
    # Get instructors list with tax code
    instructor_result = execute_query(
        st.session_state["connection"],
        "SELECT CodFisc, CONCAT(Nome, ' ', Cognome) as NomeCompleto FROM ISTRUTTORE ORDER BY Cognome, Nome"
    )
    instructors_df = pd.DataFrame(instructor_result)

    # Get course list
    course_result = execute_query(
        st.session_state["connection"],
        "SELECT CodC, Nome FROM CORSI ORDER BY Nome"
    )
    courses_df = pd.DataFrame(course_result)

    # FORM
    with st.form("new_lesson_form"):
        st.subheader("📝 Inserisci i dati della nuova lezione")

        col_left, col_right = st.columns(2)
        with col_left:
            # Instructor selection
            selected_instructor = st.selectbox(
                "👨‍🏫 Istruttore (Codice Fiscale)",
                options=instructors_df['CodFisc'].tolist()
            )
            # Course selection
            selected_course = st.selectbox(
                "🏋️ Corso",
                options=courses_df['CodC'].tolist()
            )

        with col_right:
            # Start time input
            start_time = st.time_input(
                "🕒 Orario di inizio",
                value=datetime.time(),
                step=datetime.timedelta(minutes=15)
            )
            # Duration selection
            duration = st.slider(
                "⏱️ Durata (minuti)",
                min_value=15,
                max_value=60,
                value=60,
                step=15
            )

        # New row for aligned day and room
        col_day, col_room = st.columns(2)
        with col_day:
            # Day selection
            selected_day = st.selectbox(
                "📅 Giorno",
                options=['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']
            )
        with col_room:
            # Room input
            room = st.text_input(
                "🏢 Sala",
                placeholder="Es: Sala A, Palestra 1, etc."
            )

        # Submit button
        submitted = st.form_submit_button("✅ Inserisci lezione", use_container_width=True)

        # Error handling
        if submitted:
            errors = []
            if not room.strip():
                errors.append("Il campo Sala deve essere compilato")

            if errors:
                st.error("⚠️ Errori di validazione:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                instructor_code = selected_instructor
                course_code = selected_course
                start_time_str = start_time.strftime("%H:%M:%S")

                # Check for existing lesson for the same course on the same day
                check_query = f"""
                SELECT COUNT(*) as count
                FROM PROGRAMMA 
                WHERE CodC = '{course_code}' AND Giorno = '{selected_day}'
                """

                try:
                    check_result = execute_query(st.session_state["connection"], check_query)
                    count_df = pd.DataFrame(check_result)

                    if count_df.iloc[0]['count'] > 0:
                        st.error(f"⚠️ Esiste già una lezione per il corso '{course_code}' il {selected_day}")
                    else:
                        insert_query = f"""
                        INSERT INTO PROGRAMMA (CodFisc, Giorno, OraInizio, Durata, CodC, Sala)
                        VALUES ('{instructor_code}', '{selected_day}', '{start_time_str}', {duration}, '{course_code}', '{room.strip()}')
                        """
                        execute_query(st.session_state["connection"], insert_query)

                        st.success(f"✅ Lezione inserita con successo! Corso '{course_code}' il {selected_day} alle {start_time_str} in {room}")

                        with st.expander("📋 Riepilogo lezione inserita", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Istruttore (CodFisc):** {instructor_code}")
                                st.write(f"**Corso:** {course_code}")
                                st.write(f"**Giorno:** {selected_day}")
                            with col2:
                                st.write(f"**Orario:** {start_time_str}")
                                st.write(f"**Durata:** {duration} minuti")
                                st.write(f"**Sala:** {room}")

                except Exception as e:
                    st.error(f"⚠️ Errore durante l'inserimento: {str(e)}")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")