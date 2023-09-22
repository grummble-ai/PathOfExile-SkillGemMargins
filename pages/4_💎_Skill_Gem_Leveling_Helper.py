import streamlit as st
import pandas as pd
import utility.app1.skillgems_data_handler as dh
import widgets.initializer as initializer
from utility.plot_utility import df_get_max_col

TITLE = "Skill Gem Leveling Helper"
VERSION = "v1.2.2"

# TODO: Finish settings and add button to site that can restore default settings // Could be done with sessionstate
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
    "default_min_roi": 0,
    "default_min_chaos": 0
}


# ToDo: going from 0 quality to 20 quality means flipping the gem, in practice, and should add xp needed equivalent to 1->20 the gem
# ToDo: Gems you buy at level 1-19 should be considered level 1. It changes almost nothing, but would cull potential duplicates. Also, would induce less confusion for all alt qual gems being level 16
# ToDo: Gems at 1-19 quality should be set at 0 quality, it doesn't matter if you'll flip the gem anyways
# ToDo: For exeptional and awakened gems, missing quality should add 1c/qual% to the gem cost, since you'll pay for gcps yourself later on


def create_top(df):
    # # add one to firebase db whenever the tables are refreshed
    # add_action_to_db(st.session_state.db_connection,
    #                  viewer_id=st.session_state.viewer_id,
    #                  document=u"actions_skillgemleveling")

    st.subheader("1️ Set your Preferences")

    # Settings
    colfirst, ph1, colsecond, ph2, colthird, ph3, colfourth = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])

    with colfirst:
        st.caption("Gems to hide:")
        hide_corrupted_gems = st.checkbox(label="Hide Corrupted Gems", value=DEFAULT_SETTINGS["hide_corrupted"])
        hide_quality_gems = st.checkbox(label="Hide Gems with Quality", value=DEFAULT_SETTINGS["hide_quality"])
        low_conf = st.checkbox(label="Hide Low Confidence", value=DEFAULT_SETTINGS["hide_low_confidence"])
        nr_conf = st.number_input('Low Confidence Threshold (Min. No. Listings):', min_value=0,
                                  value=DEFAULT_SETTINGS["low_confidence_threshold"])

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
        # st.caption("Miscellaneous:")
        min_roi = st.number_input('Return on Investment (Minimum):',
                                  value=DEFAULT_SETTINGS["default_min_roi"],
                                  min_value=0,
                                  max_value=st.session_state.roi_max-2,
                                  step=1)
        min_c = st.number_input(f'Buy Chaos (Minimum):',
                                min_value=DEFAULT_SETTINGS["default_min_chaos"],
                                value=0,
                                max_value=st.session_state.buy_chaos_max-2,
                                step=1)
        max_c = st.number_input('Buy Chaos (Maximum):',
                                min_value=0,
                                max_value=st.session_state.buy_chaos_max_limit,
                                key="buy_chaos_max",
                                step=1)

    st.write("_The table below updates automatically when you make changes to your preferences._\n")

    st.markdown("---")
    st.subheader("2️ Check the Best Results")

    tab1, tab2, tab3 = st.tabs(["💰 Results Sorted by Normalized Margin", "💎 Results Sorted by Margin",
                                "💸 Results Sorted by Return of Investment"])
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


def column_title_link_to_html(type: str, text: str):
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

    # filter: min buy chaos
    df_top10 = df_top10[df_top10["buy_c"] >= min_c]

    # filter: max buy chaos
    factor = st.session_state.buy_chaos_max
    df_top10 = df_top10[df_top10["buy_c"] <= st.session_state.buy_chaos_max]

    # filter: roi
    df_top10 = df_top10[df_top10["roi"] >= min_roi]

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
                              "skill", "gemQuality", "gem_type", "gemLevel", "levelRequired", "query_url",
                              "gem_level_base",
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
                                        "upgrade_path": "Upgrade Path [Lvl/Qual]",
                                        "buy_divine": column_title_link_to_html("divine", "Buy"),
                                        "sell_divine": column_title_link_to_html("divine", "Sell"),
                                        "margin_divine": column_title_link_to_html("divine", "Margin"),
                                        "margin_gem_specific": "Norm. " + column_title_link_to_html("divine", "Margin"),
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


@st.cache_data
def create_rawdata(df):
    # ui elements
    create_top_table_img(df, hide_conf=False, nr_conf=0, hide_corr=False,
                         hide_qual=False, mode="raw")


def create_FAQ():
    with st.expander("How does it work?"):
        st.markdown(
            '''<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/py69sI2ldxw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>''',
            unsafe_allow_html=True)
    with st.expander("FAQ"):
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
            **Norm_alized_ Margin?** Margin but normalized, i.e. taking into account different amounts of xp to 
            level certain gems to their maximum level. The highest amount is 1.920.762.677 for awakened gems. A regular 
            gem requires 684.009.294 xp to be leveled from 1/0 to 20/20. Therefore, the margin of the regular gem
            is divided by 684.009.294 / 1.920.762.677 = 0.3428 to account for faster leveling of the regular gem, i.e.,
            increasing the margin of the regular gem compared to an awakened gem. \n
            **RoI?** - Return on Investment; RoI = (Selling price - Buying Price) / Buying Price \n
            - **Ideas for potential improvements:**
            Gems you buy at level 1-19 should be considered level 1. \n
            Gems at 1-19 quality should be set at 0 quality, it doesn't matter if you'll flip the gem anyways\n
            For exeptional and awakened gems, missing quality should add 1c/qual% to the gem cost, since you'll pay for gcps yourself later on \n
            Consider the price of GCPs for the vendor recipe for regular gems \n
            Add a tab with historical data \n
            Possibility to enter your character's base attributes to filter out gems that your character cannot wear \n
        """)


def create_changelog():
    with st.expander("Changelog"):
        st.write("""
            **Version 1.2.2** (08th of February, 2023) \n
            - Improved caching to make the app less resource intensive globally
            **Version 1.2.1** (08th of February, 2023) \n
            - Fixed a bug regarding the preferences: buy chaos (maximum)
            **Version 1.2.0** (07th of February, 2023) \n
            - Minor changes to text
            - Added a YouTube video with explanations under "How does it work?"
            - Fixed a bug when setting the minimum roi
            - Added buy chaos (**maximum**) to the preference section
            **Version 1.1.0** (20th of December, 2022) \n
            - Added chaos orb and divine orb icons to some column titles 
            - Added trade links to the gems
            - Streamlit 1.16.0
            - Added Margin as an option to main window
            - Very basic analytics added: a counter goes up when anyone opens the app, and whenever the table is refreshed; no personal data is used at all
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


def session_state_variables(df):
    # max buy in chaos
    if 'buy_chaos_max' not in st.session_state:
        buy_chaos_max = df_get_max_col(df, "buy_c")
        st.session_state.buy_chaos_max = buy_chaos_max

    if 'buy_chaos_max_limit' not in st.session_state:
        st.session_state.buy_chaos_max_limit = buy_chaos_max

    if 'roi_max' not in st.session_state:
        roi_max = df_get_max_col(df, "roi")
        st.session_state.roi_max = roi_max


@st.cache_data
def load_data():
    dict_gem = dh.load_json()
    df_raw = pd.DataFrame.from_dict(dict_gem, orient="index")
    return df_raw


def raw_data():
    df_raw = load_data()
    session_state_variables(df_raw)
    return df_raw


SUBHEADER = '''
            Hey exile, this tool shows you the best skill gems to level for profit! The data from [poe.ninja](https://poe.ninja/)
            is updated automatically every day. Start by setting your preferences **(1️)** and then check the results **(2️)**! 
            '''

initializer.create_boilerplate(pagetitle=TITLE, version=VERSION, subheader=SUBHEADER)

df = raw_data()
create_top(df)
