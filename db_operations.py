import datetime

import firebase_admin
from firebase_admin import firestore, credentials
import json
import streamlit as st


def get_latest_id_from_document(db, document:str, field:str):
    # get latest entry and assign this for the session, holy shit is this convoluted
    views_ref = db.collection(f"{document}")
    doc = views_ref.order_by(u"time", direction=firestore.Query.DESCENDING).limit(1).get()
    my_dict = { el.id: el.to_dict() for el in doc }
    last_entry = next(iter(my_dict.values()))
    id = int(last_entry[field]) + 1
    return id


def add_new_entry_to_document(db, document:str, field:str, id:int):
    views_ref = db.collection(f"{document}")
    views_ref.document(str(id)).set({
        str(field): id,
        "time": datetime.datetime.utcnow()
    })
    return


def update_field_of_document(db, document:str, field:str, id:int, val):
    views_ref = db.collection(f"{document}")
    views_ref.document(str(id)).set({
        str(field): val,
        "time": datetime.datetime.utcnow()
    })


def create_db_connection():
    # create database connection
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()

    viewer_id = get_latest_id_from_document(db, u"views", u"number")

    add_new_entry_to_document(db, u"views", u"number", viewer_id)

    return db, viewer_id