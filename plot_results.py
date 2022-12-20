import streamlit as st
from PIL import Image
import pandas as pd
import data_handler as dh
import streamlit.components.v1 as components

VERSION = "v1.1.0"

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

    # with st.form("my_form"):
    #     title = st.text_input('Your feedback:')
    #
    #     # Every form must have a submit button.
    #     submitted = st.form_submit_button("Submit")
    #     if submitted:
    #         st.write("slider", title)

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

    st.write("_The table below updates automatically after changes._\n")

    st.markdown("---")
    st.subheader("2: Check the Best Results:")

    tab1, tab2, tab3 = st.tabs(["💰 Results Sorted by Margin / Rel. XP", "💎 Results Sorted by Margin", "💸 Results Sorted by Return of Investment"])
    with tab1:
        create_top_table_img(df, hide_conf=low_conf, nr_conf=nr_conf, hide_corr=hide_corrupted_gems,
                             hide_qual=hide_quality_gems, gem_colors=gem_colors, gem_types=gem_types, min_c=min_c,
                             min_roi=min_roi, mode="margin_rel")
    with tab2:
        create_top_table_img(df, hide_conf=low_conf, nr_conf=nr_conf, hide_corr=hide_corrupted_gems,
                             hide_qual=hide_quality_gems, gem_colors=gem_colors, gem_types=gem_types, min_c=min_c,
                             min_roi=min_roi, mode="margin")
    with tab3:
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
    html = input_df.to_html(escape=False, formatters=dict(Icon=path_to_image_html), index=False)
    html_title_centered = html.replace('<th>', '<th align="center">')
    return html_title_centered


def swap_df_columns(df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df


def column_title_link_to_html(type:str, text:str):
    img_left = '<img src="'
    img_right = '" width="25" >'
    img_chaos = "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyRerollRare.png?scale=1&w=1&h=1"
    img_divine = "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lNb2RWYWx1ZXMiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/e1a54ff97d/CurrencyModValues.png"
    if type == "chaos":
        html = text + " " + img_left + img_chaos + img_right
    elif type == "divine":
        html = text + " " + img_left + img_divine + img_right
    else:
        Exception(ValueError(f"Type {type} not recognized. Please use chaos or divine."))

    return html


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
                              "skill", "gemQuality", "gem_type", "gemLevel", "levelRequired", "query_url", "gem_level_base",
                              "gem_quality_base", "margin_c", "gem_color", "ranking_from_roi",
                              "ranking_from_margin_gem_specific"], axis=1)

    truncate_list = ["buy_divine", "sell_divine", "margin_divine", "margin_gem_specific", "roi"]
    for col in truncate_list:
        df_top10[col] = df_top10[col].map('{:,.3f}'.format)

    # reindex icon url and name to show the icon first
    df_top10 = swap_df_columns(df_top10, "name", "icon_url")

    chaos_test = 'Buy <img src="' + "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyRerollRare.png?scale=1&w=1&h=1" + '" width="25" >'

    df_top10 = df_top10.rename(columns={"name": "Skill Gem",
                                        "icon_url": "Icon",
                                        "buy_c": column_title_link_to_html("chaos", "Buy"),
                                        "sell_c": column_title_link_to_html("chaos", "Sell"),
                                        "upgrade_path": "Upgrade Path",
                                        "buy_divine": column_title_link_to_html("divine", "Buy"),
                                        "sell_divine": column_title_link_to_html("divine", "Sell"),
                                        "margin_divine": column_title_link_to_html("divine", "Margin"),
                                        "margin_gem_specific": "Margin / Rel. XP",
                                        # "average_returns_ex": "Average Returns (Ex)",
                                        "roi": "RoI",
                                        "listing_count": "No. Listings",
                                        "query_html": "Link"
                                        })

    html = convert_df(df_top10)
    st.markdown(
        html,
        unsafe_allow_html=True
    )


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
            - **Ideas for potential improvements:**
            - Gems you buy at level 1-19 should be considered level 1.
            - Gems at 1-19 quality should be set at 0 quality, it doesn't matter if you'll flip the gem anyways
            - For exeptional and awakened gems, missing quality should add 1c/qual% to the gem cost, since you'll pay for gcps yourself later on
            - Consider the price of GCPs for the vendor recipe for regular gems
            - Add a tab with historical data 
        """)


def create_changelog():
    with st.expander("Changelog"):
        st.write("""
            **Version 1.1.0** (20th of December, 2022) \n
            - Added chaos orb and divine orb icons to some column titles 
            - Added trade links to the gems
            - Streamlit 1.16.0
            - Added Margin as an option to main window
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
        st.sidebar.image("logo_v2.0.png", width=150)
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
