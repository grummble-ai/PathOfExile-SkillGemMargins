import streamlit as st


def create_welcomepage():
    st.write('''
    Welcome fellow Exile, glad to have you here! This is my 'website' where you can find all sorts of 
    useful tools for [Path of Exile](https://www.pathofexile.com/)! \n
    Some of them are created by myself, others are gathered for your convenience. All of them are, to my 
    knowledge, free to use. \n ''')

    st.markdown("<img src=\"https://i.gifer.com/4j.gif\" width=\"200\">", unsafe_allow_html=True)

    st.markdown("-----")

    st.write('''
    Here's what you can find on this website: \n 
    - [Tool Compilation](https://poeacademy.streamlit.app/Useful_Tools_(Compilation)): These are the tools that make PoE much more enjoyable to play
    - [Sextant Rolling Helper](https://poeacademy.streamlit.app/Sextant_Rolling_Helper): Shows how profitable Sextant Rolling is with current prices
    - [Skill Gem Leveling Helper](https://poeacademy.streamlit.app/Skill_Gem_Leveling_Helper): Shows what the most profitable gems to level are currently
    - [Build Guides Buttler](https://poeacademy.streamlit.app/Build_Guides): potential new tool (visit for more info)
    You can also just navigate by using the menu on the top of the sidebar. Sounds great? Great. ''')

    st.write('''
            Enjoy this project and **please provide feedback** on .. really anything: things you like, things you dislike,
            and things you want to see in the future. You best contact me on my **[Discord](https://discord.com/channels/827836172184584214/981558870507929648)** or **[GitHub](https://github.com/grummble-ai/PathOfExile-SkillGemMargins/issues)**.  \n
            ''')