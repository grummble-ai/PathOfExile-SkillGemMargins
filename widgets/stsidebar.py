import streamlit as st
import streamlit.components.v1 as components
from utility.plot_utility import get_img_with_href as get_img_with_href


def create_sidebar():
    # side bar
    st.sidebar.write("🔼 **Navigation** 🔼")
    try:
        st.sidebar.write("This is a project maintained and developed by "
                         " **[PoE Academy](https://www.youtube.com/c/PoEAcademy)**:")
        with st.sidebar:
            logo_html = get_img_with_href('img/logo_v2.0.png',
                                         'https://www.youtube.com/c/PoEAcademy',
                                         30)
            st.markdown(logo_html, unsafe_allow_html=True)

        # st.sidebar.image("logo_v2.0.png", width=80)
    except:
        st.sidebar.write("This is a project made by me [PoE Academy](https://www.youtube.com/c/PoEAcademy). You may already know me from my YT videos.")

    st.sidebar.write("For **bugs / feedback / feature requests** contact me on **[Discord]("
                     "https://discord.com/channels/827836172184584214/981558870507929648)** or **[GitHub](https://github.com/grummble-ai/PathOfExile-SkillGemMargins/issues)**.")
    st.sidebar.write(
        "If this project creates a lot of value for you, consider supporting it directly via")
    with st.sidebar:
        png_html = get_img_with_href('img/Digital-Patreon-Wordmark_FieryCoral.png',
                                     'https://www.patreon.com/user/membership?u=86747551',
                                     50)
        st.markdown(png_html, unsafe_allow_html=True)
