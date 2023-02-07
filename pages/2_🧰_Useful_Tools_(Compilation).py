import streamlit as st
from utility.firebase_operations import add_action_to_db
import widgets.initializer as initializer

# add_action_to_db(st.session_state.db_connection,
#                  viewer_id=st.session_state.viewer_id,
#                  document=u"actions_toolbox")

TITLE = "Path of Exile Tools I use (and You Should Be Using)"
SUBHEADER = '''
            **Hey, exile!** Here's a compilation of tools you want to use to improve you experience with PoE. \n
            '''

initializer.create_boilerplate(pagetitle=TITLE, version="", subheader=SUBHEADER)

# st.markdown("<img src=\"https://media.tenor.com/gZ5zDNNSqhAAAAAC/do-it-yourself-tools.gif\" width=\"300\">", unsafe_allow_html=True)

st.subheader('Essential Tools:')
st.markdown('''
            - **[filterblade.xyz](https://www.filterblade.xyz/)** - decent loot filter presets with a nice interface for customization \n
            - **[PoE Wiki](https://www.poewiki.net/)** - extensive game knowledge with well-written articles\n
            - **[Path of Building Community Fork](https://pathofbuilding.community/)** - theorycraft, analyze, and track builds\n
            - **[pathofexile.com/trade](https://www.pathofexile.com/trade)** - trade website by GGG\n
            - **[Awakened PoE Trade](https://snosme.github.io/awakened-poe-trade/download)** - quickly check item prices in-game\n
            - **[poelab.com](https://www.poelab.com/)** - all 4 lab layouts updated every day \n
            ''')

st.subheader('Advanced Tools:')
with st.expander("Expand me."):
    st.markdown('''
                - **[poe.ninja](https://poe.ninja/)** - build searches and item prices\n
                - **[Better PathOfExile Trading](https://chrome.google.com/webstore/detail/better-pathofexile-tradin/fhlinfpmdlijegjlpgedcmglkakaghnk)** - Chrome extension to store trades on pathofexile.com/trade\n
                - **[craftofexile.com](https://www.craftofexile.com/en/)** - everything you need for crafting (likelihoods, simulation, emulation, ...)\n
                - **[Skill Gem Leveling Helper](https://poeacademy.streamlit.app/Skill_Gem_Leveling_Helper)** - tells you what gems to level for profit (always level gems for profit) \n
                ''')

st.subheader('Pro Tools:')
with st.expander("Expand me."):
    st.markdown('''
                - **AutoHotkey Macros** - basically what you want, e.g. logout macro or invite macro \n
                - **[Chaos Recipe Enhance](https://github.com/ChaosRecipeEnhancer/EnhancePoEApp/releases)** - automate chaos recipes at league start\n
                - **[Exilence Next](https://github.com/viktorgullmark/exilence-next/releases)** - track you wealth and find valuable stuff to sell\n
                - **[PoE Live Search Manager](https://github.com/5k-mirrors/poe-live-search-manager/releases)** - automatically whisper people, when live a search pops\n
                - **[Sextant Rolling Helper](https://poeacademy.streamlit.app/Sextant_Rolling_Helper)** - tells you if sextant rolling is profitable at the moment and what the most valuable sextants are \n
                - **[Elesshar's craft book](https://docs.google.com/spreadsheets/d/e/2PACX-1vSDpNvovNev6Ic-KPU1jKZ3waswImcoEwH3I5ziFhZ60nmD5U58Vr-kPIIgBdCxi_D30dPakMD_SqxF/pubhtml#)** - Loads slow af but shows you how to craft endgame stuff\n
                ''')