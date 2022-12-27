import streamlit as st
import streamlit.components.v1 as components


def create_sidebar():
    # side bar
    try:
        st.sidebar.write("This is a side-project made by **PoE Academy** which is not affiliated with GGG in any way. "
                         "You may already be familiar with my YT logo:")
        st.sidebar.image("logo_v2.0.png", width=100)
    except:
        st.sidebar.write("This is a project made by PoE Academy. You may already know me from my YT videos.")

    st.empty()
    st.sidebar.write("For feedback / questions feel free to use my [Discord Server]("
                     "https://discord.com/channels/827836172184584214/981558870507929648)")
    st.sidebar.write("If you are interested in PoE Tips, solid builds and step-by-step guides consider subscribing "
                     "to my [YT channel](https://www.youtube.com/c/PoEAcademy)")
    st.sidebar.write("And if you find this project useful, you might even consider supporting it:")
    with st.sidebar:
        components.html(
            '''
            <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="PoEAcademy" data-color="#FF5F5F" data-emoji="☕"  data-font="Inter" data-text="I find this useful" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" ></script>
            '''
        )