import streamlit as st
import pandas as pd
import datetime
from utils import *

st.set_page_config(page_title="Istruttori", layout="wide")

st.title("👥 Gestione Istruttori")
st.markdown("**Visualizza e filtra gli istruttori disponibili nella palestra**")

if check_connection():
    # Filter section with descriptive text
    st.subheader("🔍 Filtra gli istruttori")
    st.markdown("Imposta i criteri di ricerca per visualizzare solo gli istruttori che ti interessano:")

    # Layout with columns for filters
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Ricerca per cognome**")
        last_name_filter = st.text_input(
            "Cognome:",
            placeholder="Inserisci il cognome da cercare...",
        )

        st.markdown("**Filtro telefono**")
        phone_only = st.checkbox(
            "Mostra solo istruttori con telefono",
            value=False,
        )

    with col_right:
        st.markdown("**Filtro per data di nascita**")

        # Query to get oldest birthdate
        birthdate_min_result = execute_query(
            st.session_state["connection"],
            "SELECT MIN(DataNascita) as data_min FROM ISTRUTTORE"
        )
        birthdate_min = [dict(zip(birthdate_min_result.keys(), row)) for row in birthdate_min_result]

        # Query to get most recent birthdate
        birthdate_max_result = execute_query(
            st.session_state["connection"],
            "SELECT MAX(DataNascita) as data_max FROM ISTRUTTORE"
        )
        birthdate_max = [dict(zip(birthdate_max_result.keys(), row)) for row in birthdate_max_result]

        # Date input fields
        date_min = st.date_input(
            "Data di nascita minima:",
            value=birthdate_min[0]['data_min'],
            min_value=birthdate_min[0]['data_min'],
            max_value=datetime.date.today()
        )

        date_max = st.date_input(
            "Data di nascita massima:",
            value=birthdate_max[0]['data_max'],
            min_value=birthdate_min[0]['data_min'],
            max_value=datetime.date.today()
        )

    # Validate date range
    if date_min > date_max:
        st.error("⚠️ Attenzione: La data minima non può essere successiva alla data massima!")
        st.stop()  # Stop if date range is invalid

    st.markdown("---")

    # Build SQL query
    query = f"""
    SELECT CodFisc, Nome, Cognome, DataNascita, Email, Telefono
    FROM ISTRUTTORE
    WHERE DataNascita >= '{str(date_min)}' AND DataNascita <= '{str(date_max)}'
    """

    # Add filters
    if last_name_filter.strip():  # Filter by last name prefix
        query += f" AND LOWER(Cognome) LIKE LOWER('{last_name_filter.strip()}%')"

    # Phone filter
    if phone_only:
        query += " AND Telefono IS NOT NULL AND Telefono != ''"

    # Order by last name, first name
    query += " ORDER BY Cognome, Nome"

    # Execute query
    instructor_results = execute_query(st.session_state["connection"], query)
    instructors_df = pd.DataFrame(instructor_results)

    # Results section with metrics
    st.subheader("📊 Risultati della ricerca")

    col_left, col_right = st.columns(2)
    with col_left:
        # Total number of instructors found
        st.metric("Istruttori trovati", len(instructors_df))
    with col_right:
        if len(instructors_df) > 0:
            # Number of instructors with phone
            with_phone = instructors_df['Telefono'].notna().sum()
            st.metric("Con telefono", f"{with_phone}/{len(instructors_df)}")

    st.markdown("---")

    # Handle empty results
    if len(instructors_df) == 0:
        st.warning("⚠️ Nessun istruttore trovato con i filtri selezionati.")
    else:
        # Display instructor list
        st.subheader("👨‍🏫 Elenco Istruttori")
        st.markdown(f"Di seguito sono riportati i **{len(instructors_df)} istruttori** che corrispondono ai criteri di ricerca:")

        for index, row in instructors_df.iterrows():
            with st.container():
                col_icon, col_info = st.columns([1, 8])

                with col_icon:
                    st.markdown(f"### 👨‍💼")

                with col_info:
                    st.markdown(f"### {row['Nome']} {row['Cognome']}")

                    info_col1, info_col2 = st.columns(2)

                    with info_col1:
                        st.markdown(f"**📋 Codice Fiscale:** `{row['CodFisc']}`")
                        st.markdown(f"**📅 Data di Nascita:** {row['DataNascita'].strftime('%d/%m/%Y')}")
                        birthdate = pd.to_datetime(row['DataNascita']).date()
                        age = (datetime.date.today() - birthdate).days // 365
                        st.markdown(f"**🎂 Età:** {age} anni")

                    with info_col2:
                        st.markdown(f"**📧 Email:** {row['Email']}")
                        if pd.notna(row['Telefono']) and str(row['Telefono']).strip():
                            st.markdown(f"**📞 Telefono:** {row['Telefono']}")
                        else:
                            st.markdown("**📞 Telefono:** *Non disponibile*")

                if index < len(instructors_df) - 1:
                    st.markdown("---")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")