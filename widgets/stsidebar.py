import streamlit as st
import streamlit.components.v1 as components
from utility.plot_utility import get_img_with_href as get_img_with_href


def create_sidebar():
    # side bar
    try:
        st.sidebar.write("This is a side-project by me:"
                         " **[PoE Academy](https://www.youtube.com/c/PoEAcademy)**. You may be familiar with my YT logo: ")
        st.sidebar.image("logo_v2.0.png", width=80)
    except:
        st.sidebar.write("This is a project made by me [PoE Academy](https://www.youtube.com/c/PoEAcademy). You may already know me from my YT videos.")

    st.sidebar.write(
        "If not consider subscribing to my channel for PoE Tips, solid builds, and more.")
    st.sidebar.write("For feedback / questions regarding this tool contact it's best to contact on [Discord]("
                     "https://discord.com/channels/827836172184584214/981558870507929648).")
    st.sidebar.write(
        "You want **regular updates or the creation of new tools**? Support this project directly by becoming a member of my")
    with st.sidebar:
        png_html = get_img_with_href('img/Digital-Patreon-Wordmark_FieryCoral.png',
                                     'https://www.patreon.com/user/membership?u=86747551',
                                     50)
        st.markdown(png_html, unsafe_allow_html=True)
