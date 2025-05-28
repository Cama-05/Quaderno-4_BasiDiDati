import streamlit as st
from sqlalchemy import create_engine,text

"""Raccoglie le principali funzioni condivise dalle varie pagine"""

#connettersi all'engine
def connect_db(dialect,username,password,host,dbname):
    try:
        engine=create_engine(f'{dialect}://{username}:{password}@{host}/{dbname}')
        conn=engine.connect()
        return conn
    except Exception as e:
        st.sidebar.error(f"Errore di connessione: {str(e)}")
        return False

def execute_query(conn,query):
    try:
        result = conn.execute(text(query))
        # Se la query è un INSERT, UPDATE o DELETE, fai il commit
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
        return result
    except Exception as e:
        # In caso di errore, fai il rollback
        conn.rollback()
        raise e

#Mostrare i numeri in una forma più compatta
def compact_format(num):
    num=float(num)
    if abs(num) >= 1e9:
        return "{:.2f}B".format(num / 1e9)
    elif abs(num) >= 1e6:
        return "{:.2f}M".format(num / 1e6)
    elif abs(num) >= 1e3:
        return "{:.2f}K".format(num / 1e3)
    else:
        return "{:.0f}".format(num)

#Controllare se la connessione al db è stata effettuata
def check_connection():
    if "connection" not in st.session_state.keys():
        st.session_state["connection"]=False

    if st.sidebar.button("Connettiti al Database"):
        myconnection=connect_db(dialect="mysql+pymysql",username="root",password="",host="localhost",dbname="PALESTRA")
        if myconnection is not False:
            st.session_state["connection"]=myconnection

        else:
            st.session_state["connection"]=False
            st.sidebar.error("Errore nella connessione al DB")

    if st.session_state["connection"]:
        st.sidebar.success("Connesso al DB")
        return True