import streamlit as st
from PIL import Image
import pandas as pd
import data_handler as dh
import streamlit.components.v1 as components

VERSION = "v1.0.0"

#TODO: Finish settings and add button to site that can restore default settings // Could be done with sessionstate
DEFAULT_SETTINGS = {
    "hide_corrupted": True,
    "hide_quality": False,
    "hide_low_confidence": True,
    "low_confidence_threshold": 30,
    "show_gem_color_green": True,
    "show_gem_color_red": True,
    "show_gem_color_blue": True,
    "show_gem_type_alt": True,
    "show_gem_type_awk": True,
    "show_gem_type_exc": True,
    "default_min_roi": 10,
    "default_min_chaos": 0,
}

# ToDo: going from 0 quality to 20 quality means flipping the gem, in practice, and should add xp needed equivalent to 1->20 the gem
# ToDo: Gems you buy at level 1-19 should be considered level 1. It changes almost nothing, but would cull potential duplicates. Also, would induce less confusion for all alt qual gems being level 16
# ToDo: Gems at 1-19 quality should be set at 0 quality, it doesn't matter if you'll flip the gem anyways
# ToDo: For exeptional and awakened gems, missing quality should add 1c/qual% to the gem cost, since you'll pay for gcps yourself later on


def create_top(df):
    st.title(f"PoE Academy's Skill Gem Leveling Helper {VERSION}")
    st.write('''
            **Hey, exile!** Welcome to this tool. I have hated the process of going through poe.ninja manually to
            find suitable skill gems, which is why I've decided to create a small tool that does this automatically.
            Since the tool accesses both poe.ninja's and GGG's API, it should continue to work unless there are
            some game-breaking changes.
            ''')

    st.markdown("---")
    st.subheader("1: Set your Preferences:")

    # Settings
    colfirst, ph1, colsecond, ph2, colthird, ph3, colfourth = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])

    with colfirst:
        st.caption("Gems to hide:")
        hide_corrupted_gems = st.checkbox(label="Hide Corrupted Gems", value=DEFAULT_SETTINGS["hide_corrupted"])
        hide_quality_gems = st.checkbox(label="Hide Gems with Quality", value=DEFAULT_SETTINGS["hide_quality"])
        low_conf = st.checkbox(label="Hide Low Confidence", value=DEFAULT_SETTINGS["hide_low_confidence"])
        nr_conf = st.number_input('Low Confidence Threshold (No. of Listings):', min_value=0, value=DEFAULT_SETTINGS["low_confidence_threshold"])

    with colsecond:
        st.caption("Gem colors to show:")
        green = st.checkbox('Green Gems (Dexterity)', value=DEFAULT_SETTINGS["show_gem_color_green"])
        red = st.checkbox('Red Gems (Strength)', value=DEFAULT_SETTINGS["show_gem_color_red"])
        blue = st.checkbox('Blue Gems (Intelligence)', value=DEFAULT_SETTINGS["show_gem_color_blue"])
        gem_colors = [green, red, blue]

    with colthird:
        st.caption("Gem types to show:")
        alt_gems = st.checkbox('Alt. Gems (Phantasmal etc.)', value=DEFAULT_SETTINGS["show_gem_type_alt"])
        awakened = st.checkbox('Awakened Gems', value=DEFAULT_SETTINGS["show_gem_type_awk"])
        exceptional = st.checkbox('Exceptional Gems (Enlighten etc.)', value=DEFAULT_SETTINGS["show_gem_type_exc"])
        gem_types = [alt_gems, awakened, exceptional]

    with colfourth:
        st.caption("Minimum values:")
        min_roi = st.slider('Minimum Return on Investment (RoI):',
                            value=DEFAULT_SETTINGS["default_min_roi"],
                            min_value=0,
                            max_value=100,
                            step=1)
        min_c = st.slider('Minimum Buy-In (Chaos Orbs):',
                          min_value=DEFAULT_SETTINGS["default_min_chaos"],
                          value=0,
                          max_value=100,
                          step=1)

    st.write("_The tables updates automatically after changes._\n")

    st.markdown("---")
    st.subheader("2: Check the Results:")

    tab1, tab2 = st.tabs(["💰 Results Sorted by Margin / Rel. XP", "💸 Results Sorted by Return of Investment"])
    with tab1:
        create_top_table_img(df, hide_conf=low_conf, nr_conf=nr_conf, hide_corr=hide_corrupted_gems,
                             hide_qual=hide_quality_gems, gem_colors=gem_colors, gem_types=gem_types, min_c=min_c,
                             min_roi=min_roi, mode="margin_rel")
    with tab2:
        create_top_table_img(df, hide_conf=low_conf, nr_conf=nr_conf, hide_corr=hide_corrupted_gems,
                             hide_qual=hide_quality_gems, gem_colors=gem_colors, gem_types=gem_types, min_c=min_c,
                             min_roi=min_roi, mode="roi")

    LEAGUE = dh.load_league()
    LAST_UPDATE = dh.last_update()
    DIV_PRICE = dh.load_divine_price()

    league_info = f"Data from poe.ninja for league \'{LEAGUE}\' from {LAST_UPDATE} GMT+2. Current divine price is {DIV_PRICE} C."
    st.caption(league_info)

    create_FAQ()

    create_changelog()


# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="40" >'


def convert_df(input_df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    html = input_df.to_html(escape=False, formatters=dict(Icon=path_to_image_html), index=False)
    html_title_centered = html.replace('<th>', '<th align="center">')
    return html_title_centered


def swap_df_columns(df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df


def create_top_table_img(df, hide_conf, nr_conf, hide_corr, hide_qual, gem_colors, gem_types, min_roi, min_c, mode):
    # various filters
    # filter: low confidence
    if hide_conf:
        df_top10 = df[df["listing_count"] >= nr_conf]
    else:
        df_top10 = df

    # filter: corrupted gems
    if hide_corr:
        df_top10 = df_top10[df_top10["corrupted"] == 0]

    # filter: gem quality =! 0
    if hide_qual:
        df_top10 = df_top10[df_top10["gemQuality"] == 0]

    # filter: gem colors
    # gem_colors = [green, red, blue]
    df_top10 = drop_gem_colors(df_top10, green=gem_colors[0], red=gem_colors[1], blue=gem_colors[2])

    # filter: gem type
    # gem_types = [alt_gems, awakened, exceptional]
    df_top10 = drop_gem_types(df_top10, alt_gem=gem_types[0], awaken=gem_types[1], exception=gem_types[2])

    # filter: buy-in c
    df_top10 = df_top10[df_top10["buy_c"] >= min_c]

    # filter: roi
    df_top10 = df_top10[df_top10["listing_count"] >= min_roi]

    # show only the 10 best results
    if mode == "margin":
        df_top10 = df_top10.nlargest(10, "margin_divine", keep="first")
    elif mode == "margin_rel":
        # grab the 10 best gems to level by margin
        df_top10 = df_top10.nsmallest(10, "ranking_from_margin_gem_specific", keep="first")
    elif mode == "roi":
        # grab the 10 best gems to level by roi
        df_top10 = df_top10.nsmallest(10, "ranking_from_roi", keep="first")

    # drop unnecessary columns
    df_top10 = df_top10.drop(["value_chaos", "value_divine", "created", "datetime", "corrupted", "qualityType",
                              "skill", "gemQuality", "gem_type", "gemLevel", "levelRequired", "gem_level_base",
                              "gem_quality_base", "sell_c", "margin_c", "gem_color", "ranking_from_roi",
                              "ranking_from_margin_gem_specific"], axis=1)

    truncate_list = ["buy_divine", "sell_divine", "margin_divine", "margin_gem_specific", "roi"]
    for col in truncate_list:
        df_top10[col] = df_top10[col].map('{:,.3f}'.format)

    # reindex icon url and name to show the icon first
    df_top10 = swap_df_columns(df_top10, "name", "icon_url")

    df_top10 = df_top10.rename(columns={"name": "Skill Gem",
                                        "icon_url": "Icon",
                                        "buy_c": "Buy (Chaos)",
                                        "upgrade_path": "Upgrade Path",
                                        "buy_divine": "Buy (Divine)",
                                        "sell_divine": "Sell (Divine)",
                                        "margin_divine": "Margin (Divine)",
                                        "margin_gem_specific": "Margin / Rel. XP",
                                        # "average_returns_ex": "Average Returns (Ex)",
                                        "roi": "RoI",
                                        "listing_count": "No. Trade Listings"
                                        })

    if mode == "margin":
        df_top10 = df_top10.rename(columns={"Margin (Divine)": "Margin (Divine) ▼"})
    elif mode == "margin_rel":
        df_top10 = df_top10.rename(columns={"Margin / Rel. XP": "Margin / Rel. XP ▼"})
    elif mode == "roi":
        df_top10 = df_top10.rename(columns={"RoI": "RoI ▼"})

    html = convert_df(df_top10)
    st.markdown(
        html,
        unsafe_allow_html=True
    )


# def create_top_table(df, hide_conf, nr_conf, hide_corr, hide_qual, mode):
#     if mode == "margin":
#         st.subheader("... by Margin")
#     elif mode == "roi":
#         st.subheader("... by Return of Investment")
#     else:
#         ValueError("Choose appropriate Top 10 table settings.")
#
#     if hide_conf:
#         df_top10 = df[df["listing_count"] >= nr_conf]
#     else:
#         df_top10 = df
#
#     if hide_corr:
#         df_top10 = df_top10[df_top10["corrupted"] == 0]
#
#     if hide_qual:
#         df_top10 = df_top10[df_top10["gemQuality"] == 0]
#
#     if mode == "margin":
#         # grab the 10 best gems to level by margin
#         df_top10 = df_top10.nsmallest(10, "ranking_from_margin_gem_specific", keep="first")
#     elif mode == "roi":
#         # grab the 10 best gems to level by roi
#         df_top10 = df_top10.nsmallest(10, "ranking_from_roi", keep="first")
#
#     # drop unnecessary columns
#     df_top10 = df_top10.drop(["value_chaos", "value_divine", "created", "datetime", "corrupted", "qualityType",
#                               "skill", "gemQuality", "gem_type", "gemLevel", "levelRequired", "gem_level_base",
#                               "gem_quality_base",
#                               "icon_url", "buy_c", "sell_c", "margin_c", "gem_color", "ranking_from_roi",
#                               "ranking_from_margin_gem_specific"], axis=1)
#
#     df_top10 = df_top10.rename(columns={"name": "Skill Gem",
#                                         "upgrade_path": "Upgrade Path",
#                                         "buy_divine": "Buy (Divine)",
#                                         "sell_divine": "Sell (Divine)",
#                                         "margin_divine": "Margin (Divine)",
#                                         "margin_gem_specific": "Margin / Rel. Exp.",
#                                         # "average_returns_ex": "Average Returns (Ex)",
#                                         "roi": "RoI",
#                                         "listing_count": "No. Trade Listings"
#                                         })
#
#     if mode == "margin":
#         df_top10 = df_top10.rename(columns={"Margin / Rel. Exp.": "Margin / Rel. Exp. ▼"})
#     elif mode == "roi":
#         df_top10 = df_top10.rename(columns={"RoI": "RoI ▼"})
#
#     st.table(df_top10)


def drop_gem_colors(df, green, red, blue):
    """
    This function drops all gem colors that are not ticket in the settings section.
    """
    if not green:
        df = df[df["gem_color"] != "green"]
    if not red:
        df = df[df["gem_color"] != "red"]
    if not blue:
        df = df[df["gem_color"] != "blue"]
    return df


def drop_gem_types(df, alt_gem, awaken, exception):
    if not alt_gem:
        df = df[df["name"].str.contains("Phantasmal") == False]
        df = df[df["name"].str.contains("Divergent") == False]
        df = df[df["name"].str.contains("Anomalous") == False]

    if not awaken:
        df = df[df["name"].str.contains("Awakened") == False]

    if not exception:
        df = df[df["name"].str.contains("Enlighten") == False]
        df = df[df["name"].str.contains("Empower") == False]
        df = df[df["name"].str.contains("Enhance") == False]

    return df


# def create_plot(df):
#     # ui elements
#     st.header('Want to dig into the data yourself?')
#
#     # input elements
#     col3, colx, col4 = st.columns([3, 1, 5])
#
#     with col3:
#         st.subheader("Settings")
#         input_min_roi = st.slider('Minimum Return on Investment:',
#                                   value=10,
#                                   min_value=0,
#                                   max_value=100,
#                                   step=1)
#         input_buyin = st.slider('Minimum Buy-In (Chaos Orbs):',
#                                 min_value=0,
#                                 value=0,
#                                 max_value=100,
#                                 step=1)
#         input_min_listings = st.number_input('Minimum No. of Listing on Trade:',
#                                              min_value=0,
#                                              value=10,
#                                              step=1,
#                                              format="%d")
#         st.caption("What gem colors to show:")
#         green = st.checkbox('Green Gems (Dexterity)', value=True)
#         red = st.checkbox('Red Gems (Strength)', value=True)
#         blue = st.checkbox('Blue Gems (Intelligence)', value=True)
#
#         st.caption("What special gems to show:")
#         alt_gems = st.checkbox('Alt. Gems (Phantasmal etc.)', value=True)
#         awakened = st.checkbox('Awakened Gems', value=True)
#         exceptional = st.checkbox('Exceptional Gems (Enlighten etc.)', value=True)
#
#     with col4:
#         st.subheader("Hover the graph for more info")
#         # filter as specified in the input
#         df_ = df[df["roi"] >= input_min_roi]
#         df_ = df_[df_["buy_c"] >= input_buyin]
#         df_ = df_[df_["listing_count"] >= input_min_listings]
#         if not green:
#             df_ = df_[df_["gem_color"] != "green"]
#         if not red:
#             df_ = df_[df_["gem_color"] != "red"]
#         if not blue:
#             df_ = df_[df_["gem_color"] != "blue"]
#
#         df_ = drop_special_gems(df_, alt_gem=alt_gems, awaken=awakened, exception=exceptional)
#
#         # workaround to make roi_gem_norm numeric (bug with plotly)
#         size = pd.to_numeric(df_.roi)
#
#         if df_.shape[0] < 15:
#             fig = px.scatter(df_,
#                              x="buy_c",
#                              y="margin_c",
#                              size=size,
#                              text="name",
#                              color="gem_color",
#                              color_discrete_map={"blue": "rgba(112, 112, 255, 0.8)",
#                                                  "green": "rgba(112, 255, 112, 0.8)",
#                                                  "red": "rgba(224, 80, 48, 0.8)",
#                                                  "white": "rgba(255, 255, 255, 0.8)"},
#                              labels={
#                                  "margin_c": "Margin (Chaos Orbs)",
#                                  "buy_c": "Buying Price (Chaos Orbs)",
#                                  "gem_color": "Gem Color"
#                              },
#                              hover_data=["name",
#                                          "margin_divine",
#                                          "margin_gem_specific",
#                                          "roi"
#                                          ],
#                              log_x=True,
#                              log_y=True,
#                              )
#             fig.update_traces(textposition='middle right')
#             fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#
#         else:
#             fig = px.scatter(df_,
#                              x="buy_c",
#                              y="margin_c",
#                              size=size,
#                              # text="name",
#                              color="gem_color",
#                              color_discrete_map={"blue": "rgba(112, 112, 255, 0.8)",
#                                                  "green": "rgba(112, 255, 112, 0.8)",
#                                                  "red": "rgba(224, 80, 48, 0.8)",
#                                                  "white": "rgba(255, 255, 255, 0.8)"},
#                              labels={
#                                  "margin_c": "Margin (Chaos Orbs)",
#                                  "buy_c": "Buying Price (Chaos Orbs)",
#                                  "gem_color": "Gem Color"
#                              },
#                              hover_data=["name",
#                                          "margin_divine",
#                                          "margin_gem_specific",
#                                          "roi"
#                                          ],
#                              log_x=True,
#                              log_y=True,
#                              )
#
#         st.caption("Margin vs. Buying Price plot. Marker size indicates the RoI. Logarithmic scale.")
#         st.plotly_chart(fig, use_container_width=True)
#
#     st.empty()
#     st.markdown("---")


@st.cache
def create_rawdata(df):
    # ui elements
    create_top_table_img(df, hide_conf=False, nr_conf=0, hide_corr=False,
                         hide_qual=False, mode="raw")


def create_FAQ():
    with st.expander("FAQ (click me)"):
        st.write("""
            - **General**
            **Why are there so many gems that start from level 16?** This is because poe.ninja's API returns many gems
            as such. 
            - **Setup** \n
            **Why hide low confidence?** Because PoE.ninja considers a count smaller than 10 to be "low evidence" 
            which you should do as well. \n
            **Why is the default value for the low confidence threshold 50 not 10?** There are two reasons: First,
            it seems that sometimes poe.ninja does have additional criterion for determining whether or not a gem is
            tagged with low confidence, but its API doesn't contain this information. Second, you want to look for 
            liquid markets. If there are many listings for a certain gem you can be sure that there is a market for it
            and that you will be able to trade your gems quickly. \n
            **Why hide corrupted gems?** Because, by using a Vaal Orb, you have a 1 in 8 chance to get those which
            is simply not reliant. \n
            **Why hide gems with quality?** Because there are some cases (e.g. auras), where you don't need to level 
            them twice (1/0 to 20/0; and 1/20 to 20/20) to get the full return \n   
            - **Tables**\n
            **No. of Trade Listing?** Indicated the number of listings available on trade. \n
            **Buy (Divine)** The buying price of the gem in Divine Orbs. Why do most orbs that can be bought from Lilly
            Roth cost 1c? Well, because no one lists them for their vendor price. I think this is negligible for your 
            decision on which gem to level so I have no plans on implementing a double check for this. \n
            **Sell (Divine)** The selling price of the gem in Divine Orbs. \n
            **Margin?** Selling price - Buying Price \n
            **Margin / Rel. Exp.?** Margin but normalized, i.e. taking into account different amounts of xp to 
            level certain gems to their maximum level. The highest amount is 1.920.762.677 for awakened gems. A regular 
            gem requires 684.009.294 xp to be leveled from 1/0 to 20/20. Therefore, the margin of the regular gem
            is divided by 684.009.294 / 1.920.762.677 = 0.3428 to account for faster leveling of the regular gem, i.e.,
            increasing the margin of the regular gem compared to an awakened gem. \n
            **RoI?** - Return on Investment; RoI = (Selling price - Buying Price) / Buying Price \n
        """)


def create_changelog():
    with st.expander("Changelog"):
        st.write("""
            **Version 1.0.0** (7th of September, 2022) \n
            - Fixed a bug where gems weren't flagged with their actual gem color
            - Added a lot more settings to the settings part (gem colors/types, min values) 
            - Included both tables into tabs for better navigation
            - Added skill gem icons and buy (chaos) to the tables for better orientation 
            - Reworked the FAQ and added a lot more information to it
            - Added minor improvements to the layout
            - Changed the refernce currency from Exalted Orbs (good by my old friend) to Divine Orbs
            - Removed a long standing bug where the Exalted (now Divine) Orb to Chaos Orb ratio was not calculated correctly
            - The "play with the data yourself" area has vanished as it was only really useful for creating this tool
            - Update to Streamlit 1.12.2
            **Version 0.9.3** \n
            - The default value for the low confidence filter is now set to 30 the remove most unwanted results. 
              (It seems that poe.ninja has a more sophisticated approach than this, but, unfortunately, its API response
              does not provide the low confidence information.)
            **Version 0.9.2** \n
            - Fixed a bug when calculating Margin / Rel. Exp. (again)
            - Added the possibility to set a custom low confidence threshold 
            **Version 0.9.1** \n
            - Fixed a bug when calculating Margin / Rel. Exp.
            **Version 0.9.0** \n
            - Improved gem xp calculation. Required gem experience is now calculated precisely for regular gems. 
            - Added more settings for the main tables (especially gems with quality)
            - Slight improvements to the UI. \n
            **Version 0.8.0** \n
            - Fixed a bug where some corrupted versions of gems were used as a starting point of the analysis
            - Rewrote some info in the expanders
        """)


def create_sidebar():
    # side bar
    try:
        st.sidebar.write("This is a project made by **PoE Academy**. You may already be familiar with my YT logo:")
        st.sidebar.image("logo_with_bg_transparent.png", width=150)
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
            <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="PoEAcademy" data-color="#FF5F5F" data-emoji="☕"  data-font="Inter" data-text="Great Tool!" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" ></script>
            '''
        )


def load_data():
    dict_gem = dh.load_json()
    df = pd.DataFrame.from_dict(dict_gem, orient="index")
    return df


def settings():
    img = Image.open("utility/favicon.ico")
    st.set_page_config(
        page_title="Skill Gem Leveling Helper by PoE Academy",
        page_icon=img,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://discord.com/channels/827836172184584214/981558870507929648',
            'Report a bug': "https://discord.com/channels/827836172184584214/981558870507929648",
            'About': "This app was made to help choosing the right gems to level for profit in Path of Exile."
        }
    )


# @st.cache
def create_site():
    settings()

    df = load_data()

    create_top(df)

    # create_plot(df)

    create_sidebar()

    # st.header('C) Raw results')
    # create_rawdata(df)
    st.write(f"You are working with {VERSION}; This site is not affiliated with, funded, or in any way associated "
             f"with Grinding Gear Games.")
