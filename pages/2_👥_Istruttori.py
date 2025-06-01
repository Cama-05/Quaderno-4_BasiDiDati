import streamlit as st
import pandas as pd
import datetime
from utils import *

st.set_page_config(page_title="Istruttori", layout="wide")

st.title("👥 Gestione Istruttori")
st.markdown("**Visualizza e filtra gli istruttori disponibili nella palestra**")

if check_connection():
    # Sezione filtri con elementi di testo descrittivi
    st.subheader("🔍 Filtra gli istruttori")
    st.markdown("Imposta i criteri di ricerca per visualizzare solo gli istruttori che ti interessano:")
    
    # Layout con colonne per organizzare i filtri
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Ricerca per cognome**")
        cognome = st.text_input(
            "Cognome:", 
            placeholder="Inserisci il cognome da cercare...",
        )
        
        st.markdown("**Filtro telefono**")
        solo_con_telefono = st.checkbox(
            "Mostra solo istruttori con telefono",
            value=False,
        )
    
    with col2:
        st.markdown("**Filtro per data di nascita**")
        
        # Query per trovare la data di nascita più antica
        result_data_min = execute_query(st.session_state["connection"], "SELECT MIN(DataNascita) as data_min FROM ISTRUTTORE")
        data_min_db = [dict(zip(result_data_min.keys(), result)) for result in result_data_min]

        # Query per trovare la data di nascita più recente
        result_data_max = execute_query(st.session_state["connection"], "SELECT MAX(DataNascita) as data_max FROM ISTRUTTORE")
        data_max_db = [dict(zip(result_data_max.keys(), result)) for result in result_data_max]

        #Campi di input delle date
        data_min = st.date_input(
            "Data di nascita minima:",
            value = data_min_db[0]['data_min'],
            min_value=data_min_db[0]['data_min'],
            max_value=datetime.date.today()
        )
        
        data_max = st.date_input(
            "Data di nascita massima:", 
            value=data_max_db[0]['data_max'],
            min_value=data_min_db[0]['data_min'],
            max_value=datetime.date.today()
        )

    # Validazione del range di date
    if data_min > data_max:
        st.error("⚠️ Attenzione: La data minima non può essere successiva alla data massima!")
        st.stop() #Per evitare che venga visualizzata la parte sottostante inutilmente se il filtro è privo di senso

    st.markdown("---")

    # Costruzione query
    query = f"""
    SELECT CodFisc, Nome, Cognome, DataNascita, Email, Telefono
    FROM ISTRUTTORE
    WHERE DataNascita >= '{str(data_min)}' AND DataNascita <= '{str(data_max)}'
    """
    
    # Aggiunta filtri
    if cognome.strip(): #vengono selezionati solo quelli il cui cognome inizia con la stringa inserita in input dall'utente (anche parzialmente)
        query += f" AND LOWER(Cognome) LIKE LOWER('{cognome.strip()}%')"
    
    # Filtro telefono con checkbox
    if solo_con_telefono:
        query += " AND Telefono IS NOT NULL AND Telefono != ''"
    
    # Ordinamento per cognome e nome
    query += " ORDER BY Cognome, Nome"

    # Esecuzione query
    result_istruttori= execute_query(st.session_state["connection"], query)
    df_istruttori = pd.DataFrame(result_istruttori)
    


    # Sezione risultati con metriche informative
    st.subheader("📊 Risultati della ricerca")
    
    col1, col2 = st.columns(2)
    with col1:
        #N° totale di istruttori compatibili
        st.metric("Istruttori trovati", len(df_istruttori))
    with col2:
        if len(df_istruttori) > 0:
            #N° di Istruttori con telefono
            con_telefono = df_istruttori['Telefono'].notna().sum()
            st.metric("Con telefono", f"{con_telefono}/{len(df_istruttori)}")

    st.markdown("---")

    # Gestione risultati vuoti
    if len(df_istruttori) == 0:
        st.warning("⚠️ Nessun istruttore trovato con i filtri selezionati.")
    else:
        # Visualizzazione elemento per elemento
        st.subheader("👨‍🏫 Elenco Istruttori")
        st.markdown(f"Di seguito sono riportati i **{len(df_istruttori)} istruttori** che corrispondono ai criteri di ricerca:")
        
        for index, row in df_istruttori.iterrows():
            with st.container():
                col_icon, col_info = st.columns([1, 8])
                
                with col_icon:
                    # Icona per ogni 
                    st.markdown(f"### 👨‍💼")
                
                with col_info:
                    # Nome e cognome in evidenza
                    st.markdown(f"### {row['Nome']} {row['Cognome']}")
                    
                    # Informazioni organizzate in colonne
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.markdown(f"**📋 Codice Fiscale:** `{row['CodFisc']}`")
                        st.markdown(f"**📅 Data di Nascita:** {row['DataNascita'].strftime('%d/%m/%Y')}")
                        
                        # Calcolo e visualizzazione età
                        data_nascita = pd.to_datetime(row['DataNascita']).date()
                        eta = (datetime.date.today() - data_nascita).days // 365
                        st.markdown(f"**🎂 Età:** {eta} anni")
                    
                    with info_col2:
                        st.markdown(f"**📧 Email:** {row['Email']}")
                        
                        # Gestione telefono con controllo valori nulli o stringhe vuote
                        if pd.notna(row['Telefono']) and str(row['Telefono']).strip():
                            st.markdown(f"**📞 Telefono:** {row['Telefono']}")
                        else:
                            st.markdown("**📞 Telefono:** *Non disponibile*")
                
                # Separatore tra elementi (tranne per l'ultimo)
                if index < len(df_istruttori) - 1:
                    st.markdown("---")
else:
    st.warning("🔌 Connettiti al database per utilizzare questa funzionalità")
    st.info("Utilizza il pulsante 'Connettiti al Database' nella barra laterale")