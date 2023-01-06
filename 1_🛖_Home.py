import widgets.welcomepage as welcomepage
import widgets.initializer as initializer
import streamlit as st
from utility.firebase_operations import add_action_to_db

# initialize tracking
if 'tracking_active' not in st.session_state:
    initializer.start_tracking()

# add one to the counter in db whenever this site is refreshed
add_action_to_db(st.session_state.db_connection,
                 viewer_id=st.session_state.viewer_id,
                 document=u"actions_home")

# create welcome page
initializer.create_boilerplate(pagetitle="PoE Academy's Toolbox", version="", subheader="")
welcomepage.create_welcomepage()

