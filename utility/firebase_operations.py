import datetime
import firebase_admin
from firebase_admin import firestore, credentials
import json
import streamlit as st


def get_latest_id_from_document(db, document: str, field: str):
    # get latest entry and assign this for the session, holy shit is this convoluted
    views_ref = db.collection(f"{document}")
    doc = views_ref.order_by(u"time", direction=firestore.Query.DESCENDING).limit(1).get()
    my_dict = {el.id: el.to_dict() for el in doc}
    last_entry = next(iter(my_dict.values()))
    id = int(last_entry[field]) + 1
    return id


def update_field_of_document(db, document: str, field: str, id: int, val):
    views_ref = db.collection(f"{document}")
    views_ref.document(str(id)).set({
        str(field): val,
        "time": datetime.datetime.utcnow()
    })


def add_action_to_db(db, viewer_id:int, document:str):
    # first add one to the counter
    st.session_state.actions += 1
    # update general field
    update_field_of_document(db, document=u"actions", field=u"number", id=viewer_id, val=st.session_state.actions)

    # then update page specific document
    if document == "actions_skillgemleveling":
        st.session_state.actions_skillgemleveling += 1
        # then add to specific db field
        update_field_of_document(db,
                                 document=document,
                                 field=u"number",
                                 id=viewer_id,
                                 val=st.session_state.actions_skillgemleveling)

    elif document == "actions_home":
        st.session_state.actions_home += 1
        update_field_of_document(db,
                                 document=document,
                                 field=u"number",
                                 id=viewer_id,
                                 val=st.session_state.actions_home)
    elif document == "actions_toolbox":
        st.session_state.actions_toolbox += 1
        update_field_of_document(db,
                                 document=document,
                                 field=u"number",
                                 id=viewer_id,
                                 val=st.session_state.actions_toolbox)
    else:
        ValueError("Provide a suitable firestore document name.")


def create_db_connection():
    # create database connection
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()

    viewer_id = get_latest_id_from_document(db, u"views", u"number")

    update_field_of_document(db, document=u"views", field=u"number", id=viewer_id, val=viewer_id)
    update_field_of_document(db, document=u"actions", field=u"number", id=viewer_id, val="1")

    return db, viewer_id



