import streamlit as st


def create_title(title:str, version:str, text:str):
    st.title(f"{title} ")
    if version:
        st.caption(f"You are using {version}. This site is not affiliated with, funded, or in any way associated with "
                     f"Grinding Gear Games or the TFT Discord.")
    if text:
        st.write(text)
        st.markdown("---")