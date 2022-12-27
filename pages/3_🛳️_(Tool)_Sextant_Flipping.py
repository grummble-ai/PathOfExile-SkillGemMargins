import streamlit as st
from utility.firebase_operations import add_action_to_db
import widgets.initializer as initializer
from PIL import Image

add_action_to_db(st.session_state.db_connection,
                 viewer_id=st.session_state.viewer_id,
                 document=u"actions_sextants")

# create welcome page
SUBHEADER = '''This tool is still under construction. You shouldn't be using it at this point.'''
VERSION = "0.1.0"
initializer.create_boilerplate(pagetitle="Tool: Sextant Flipper", version=VERSION, subheader=SUBHEADER)

image = Image.open("img/Under-Construction.png")
st.image(image, width=500)