import streamlit as st
from sqlalchemy import text

def connect_db():
    try:
        conn = st.connection("neon", type="sql")
        return conn
    except Exception as e:
        st.sidebar.error(f"Errore di connessione: {e}")
        return None

def execute_query(connection, query):
    try:
        query_type = query.strip().split()[0].upper()
        if query_type == "SELECT":
            # Query di lettura
            df = connection.query(query, ttl="10m")
            return df
        elif query_type in ("INSERT", "UPDATE", "DELETE"):
            # Query di scrittura
            with connection.session as session:
                session.execute(text(query))
                session.commit()
            st.success("Query eseguita con successo!")
            return None
        else:
            st.warning("Tipo di query non riconosciuto o non supportato.")
            return None
    except Exception as e:
        st.error(f"Errore nell'esecuzione della query: {e}")
        return None

def check_connection():
    if "connection" not in st.session_state:
        st.session_state["connection"] = None

    if st.sidebar.button("Connettiti al Database"):
        db_connection = connect_db()
        if db_connection:
            st.session_state["connection"] = db_connection
            st.sidebar.success("Connesso al DB")
        else:
            st.session_state["connection"] = None
            st.sidebar.error("Errore nella connessione al DB")

    return st.session_state["connection"]
