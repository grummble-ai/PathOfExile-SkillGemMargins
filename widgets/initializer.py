import widgets.settings as stgs
import widgets.stsidebar as side
import widgets.header as hd
import streamlit as st
import utility.firebase_operations as firebase_db


def create_boilerplate(pagetitle:str, version:str, subheader:str):
    stgs.set_settings(title=pagetitle)
    side.create_sidebar()
    hd.create_title(title=pagetitle, version=version, text=subheader)


def initialize_session_state():
    # initialize actions counter
    if 'actions' not in st.session_state:
        st.session_state["actions"] = 1

    if 'actions_skillgemleveling' not in st.session_state:
        st.session_state["actions_skillgemleveling"] = 0

    if 'actions_home' not in st.session_state:
        st.session_state["actions_home"] = 0

    if 'actions_toolbox' not in st.session_state:
        st.session_state["actions_toolbox"] = 0


@st.cache(ttl=43200) # 43200 seconds = 12 hours
def start_tracking():
    initialize_session_state()

    # create firebase connection
    db, viewer_id = firebase_db.create_db_connection()

    # add viewer id to state widget
    if 'viewer_id' not in st.session_state:
        st.session_state["viewer_id"] = viewer_id

    # save db connection to session state
    if "db_connection" not in st.session_state:
        st.session_state["db_connection"] = db

    # tracking active
    if 'tracking_active' not in st.session_state:
        st.session_state["tracking_active"] = True