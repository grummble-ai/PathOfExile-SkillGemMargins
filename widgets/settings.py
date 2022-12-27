from PIL import Image
import streamlit as st


def set_settings(title):
    img = Image.open("img/favicon.ico")
    st.set_page_config(
        page_title=title,
        page_icon=img,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://discord.com/channels/827836172184584214/981558870507929648',
            'Report a bug': "https://discord.com/channels/827836172184584214/981558870507929648",
            'About': "This app was made to help choosing the right gems to level for profit in Path of Exile."
        }
    )