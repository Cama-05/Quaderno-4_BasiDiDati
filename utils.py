import streamlit as st
from sqlalchemy import create_engine, text

# Connect to the engine
def connect_db(dialect, username, password, host, dbname):
    try:
        engine = create_engine(f'{dialect}://{username}:{password}@{host}/{dbname}')
        connection = engine.connect()
        return connection
    except Exception as e:
        st.sidebar.error(f"Errore di connessione: {str(e)}")
        return False

def execute_query(connection, query):
    try:
        result = connection.execute(text(query))
        # If the query is an INSERT, UPDATE or DELETE, commit the transaction
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            connection.commit()
        return result
    except Exception as e:
        # On error, rollback the transaction
        connection.rollback()
        raise e

# Check if the database connection has been established
def check_connection():
    if "connection" not in st.session_state.keys():
        st.session_state["connection"] = False

    if st.sidebar.button("Connettiti al Database"):
        user = st.secrets["mysql"]["user"]
        password = st.secrets["mysql"]["password"]
        host = st.secrets["mysql"]["host"]
        port = st.secrets["mysql"]["port"]
        database = st.secrets["mysql"]["database"]
        db_connection = connect_db(dialect="mysql+pymysql", username=user, password=password, host=host+":"+port, dbname=database)
        if db_connection is not False:
            st.session_state["connection"] = db_connection
        else:
            st.session_state["connection"] = False
            st.sidebar.error("Errore nella connessione al DB")

    if st.session_state["connection"]:
        st.sidebar.success("Connesso al DB")
        return True