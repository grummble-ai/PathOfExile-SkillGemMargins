from datetime import datetime as dt
import streamlit as st
import plotly.express as px
import pandas as pd
import data_handler as dh
from PIL import Image


def create_top(df):
    st.title("PoE Skill Gem Profit Margin Calculator (v0.6.1 - Work in Progress)")
    # create content
    st.header("TOP 10 Gems to Level...")
    # st.write("Choose wisely:")
    low_conf = st.checkbox(label="Hide Low Confidence", value=True)
    hide_corrupted_gems = st.checkbox(label="Hide Corrupted Gems", value=True)
    create_top_table(df, hide_conf=low_conf, hide_corr=hide_corrupted_gems, mode="margin")
    create_top_table(df, hide_conf=low_conf, hide_corr=hide_corrupted_gems, mode="roi")

    with st.expander("Read me"):
        st.write("""
            **What am I looking at?** The tables show the top 10 results by margin and RoI in Exalted Orbs.\n
            **Margin?** Selling price - Buying Price \n
            **RoI?** - Return on Investment; RoI = (Selling price - Buying Price) / Buying Price \n
            **Margin / Req. Exp.?** Margin but normalized, i.e. taking into account different amounts of xp to 
            level certain gems to their maximum level. AT THE MOMENT IT IS ASSUMED THAT EVERY GEM IS LEVELED FROM 0 
            TO MAX. LVL AND NOT, E.G., STARTING FROM 16/0. \n
            **No. of Trade Listing?** Indicated the number of listings available on trade. PoE.ninja considers a 
            number smaller than 10 to be "low evidence" which you should do as well. 
            **Why hide corrupted gems?** Because, by using a Vaal Orb, you have a 1 in 8 chance to get those which
            is simply not reliant. 
        """)
    st.markdown("---")
    st.empty()


def create_top_table(df, hide_conf, hide_corr, mode):
    if mode == "margin":
        st.subheader("...by Margin")
    elif mode == "roi":
        st.subheader("...by RoI / Req. Exp.")
    else:
        ValueError("Choose appropriate Top 10 table settings.")

    LEAGUE = dh.load_league()
    LAST_UPDATE = dh.last_update()
    comment = f"PoE.ninja data for league \'{LEAGUE}\' from {LAST_UPDATE}"
    st.caption(comment)

    if hide_conf:
        df_top10 = df[df["listing_count"] >= 10]
    else:
        df_top10 = df

    if hide_corr:
        df_top10 = df_top10[df_top10["corrupted"] == 0]

    if mode == "margin":
        # grab the 10 best gems to level by margin
        df_top10 = df_top10.nsmallest(10, "ranking_from_margin_gem_specific", keep="first")
    elif mode == "roi":
        # grab the 10 best gems to level by roi
        df_top10 = df_top10.nsmallest(10, "ranking_from_roi", keep="first")

    # drop unnecessary columns
    df_top10 = df_top10.drop(["value_chaos", "value_exalted", "created", "datetime", "corrupted", "qualityType",
                              "skill", "gemQuality", "gemLevel", "levelRequired", "icon_url", "buy_c", "sell_c",
                              "margin_c", "gem_color", "ranking_from_roi", "ranking_from_margin_gem_specific"], axis=1)

    df_top10 = df_top10.rename(columns={"name": "Skill Gem",
                                        "upgrade_path": "Upgrade Path",
                                        "buy_ex": "Buy (Ex)",
                                        "sell_ex": "Sell (Ex)",
                                        "margin_ex": "Margin (Ex)",
                                        "margin_gem_specific": "Margin / Req. Exp.",
                                        # "average_returns_ex": "Average Returns (Ex)",
                                        "roi": "RoI",
                                        "listing_count": "No. Trade Listings"
                                        })

    if mode == "margin":
        df_top10 = df_top10.rename(columns={"Margin / Req. Exp.": "Margin / Req. Exp. ▼"})
    elif mode == "roi":
        df_top10 = df_top10.rename(columns={"RoI": "RoI ▼"})

    st.table(df_top10)


def drop_special_gems(df, alt_gem, awaken, exception):
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


def create_plot(df):
    # ui elements
    st.header('Want to dig deeper?')

    # input elements
    col3, colx, col4 = st.columns([3, 1, 5])

    with col3:
        st.subheader("Choose your settings:")
        input_min_roi = st.slider('Minimum Return on Investment:',
                                  value=10,
                                  min_value=0,
                                  max_value=100,
                                  step=1)
        input_buyin = st.slider('Minimum Buy-In (Chaos Orbs):',
                                min_value=0,
                                value=0,
                                max_value=100,
                                step=1)
        input_min_listings = st.number_input('Minimum No. of Listing on Trade:',
                                             min_value=0,
                                             value=10,
                                             step=1,
                                             format="%d")
        st.caption("What gem colors to show:")
        green = st.checkbox('Green Gems (Dexterity)', value=True)
        red = st.checkbox('Red Gems (Strength)', value=True)
        blue = st.checkbox('Blue Gems (Intelligence)', value=True)

        st.caption("What special gems to show:")
        alt_gems = st.checkbox('Alt. Gems (Phantasmal etc.)', value=True)
        awakened = st.checkbox('Awakened Gems', value=True)
        exceptional = st.checkbox('Exceptional Gems (Enlighten etc.)', value=True)

    with col4:
        st.subheader("Hover to see more info:")
        # filter as specified in the input
        df_ = df[df["roi"] >= input_min_roi]
        df_ = df_[df_["buy_c"] >= input_buyin]
        df_ = df_[df_["listing_count"] >= input_min_listings]
        if not green:
            df_ = df_[df_["gem_color"] != "green"]
        if not red:
            df_ = df_[df_["gem_color"] != "red"]
        if not blue:
            df_ = df_[df_["gem_color"] != "blue"]

        df_ = drop_special_gems(df_, alt_gem=alt_gems, awaken=awakened, exception=exceptional)

        # workaround to make roi_gem_norm numeric (bug with plotly)
        size = pd.to_numeric(df_.roi)

        if df_.shape[0] < 15:
            fig = px.scatter(df_,
                             x="buy_c",
                             y="margin_c",
                             size=size,
                             text="name",
                             color="gem_color",
                             color_discrete_map={"blue": "rgba(112, 112, 255, 0.8)",
                                                 "green": "rgba(112, 255, 112, 0.8)",
                                                 "red": "rgba(224, 80, 48, 0.8)",
                                                 "white": "rgba(255, 255, 255, 0.8)"},
                             labels={
                                 "margin_c": "Margin (Chaos Orbs)",
                                 "buy_c": "Buying Price (Chaos Orbs)",
                                 "gem_color": "Gem Color"
                             },
                             hover_data=["name",
                                         "margin_ex",
                                         "margin_gem_specific",
                                         "roi"
                                         ],
                             log_x=True,
                             log_y=True,
                             )
            fig.update_traces(textposition='middle right')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        else:
            fig = px.scatter(df_,
                             x="buy_c",
                             y="margin_c",
                             size=size,
                             # text="name",
                             color="gem_color",
                             color_discrete_map={"blue": "rgba(112, 112, 255, 0.8)",
                                                 "green": "rgba(112, 255, 112, 0.8)",
                                                 "red": "rgba(224, 80, 48, 0.8)",
                                                 "white": "rgba(255, 255, 255, 0.8)"},
                             labels={
                                 "margin_c": "Margin (Chaos Orbs)",
                                 "buy_c": "Buying Price (Chaos Orbs)",
                                 "gem_color": "Gem Color"
                             },
                             hover_data=["name",
                                         "margin_ex",
                                         "margin_gem_specific",
                                         "roi"
                                         ],
                             log_x=True,
                             log_y=True,
                             )

        st.caption("Margin vs. Buying Price plot. Marker size indicates the RoI.")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.empty()


def create_FAQ():
    # ------------------------------------------------------------------------------------------------------------------
    st.header("Thoughts")
    with st.expander("Expand me"):  # TODO: write explanation
        st.write("""
            **How is the margin calculated?** \n
            Ideally you want to know what the best average outcome for any given 
            gem is. There are 4 corruption outcomes: \n
                - No effect (other than adding the corrupted property) \n
                - Add or subtract one level. Max level gems can exceed their normal maximum this way. A corrupted 
                gem at the normal maximum will not continue to gain experience. \n
                - Add or subtract 1-20 quality. Gems can have up to 23% quality this way. \n
                - Change the gem to its corresponding Vaal Gem. \n
            
            Sometimes 23% quality gems are worth a bit. Sometimes even a corrupted lvl 20 (no change) outcome yields 
            some money. Sometimes they aren't worth anything. \n
            
            So to correctly estimate the potential earnings, it would be better to average over all 4 outcomes and 
            not just to look at what the "big bang" (adding one level) would yield. And, in fact, the big bang is 
            not even a 25% chance but rather a 1 in 8 chance if you're just using a Vaal Orb instead of the temple 
            corruption.  \n
            
            However, this is a difficult task since the poe.ninja API does not provide all outcomes for all gems 
            and when it does, the listing count often is too small to have any significance. Please stick to 
            uncorrupted gems (typically [20/20]) if you want to aim for the guaranteed margin.  
            \n
            **Why do some gems that can be bought from Lily Roth have a selling price > 1c?** \n
            Good catch! The problem is that no one lists 
        """)

    st.empty()
    st.markdown("---")
    st.markdown("This site is not affiliated with, funded, or in any way associated with Grinding Gear Games.")


def create_sidebar():
    # side bar
    try:
        st.sidebar.image("logo_with_bg_transparent.png", use_column_width=True)
    except:
        st.sidebar.header("PoE Academy")

    st.empty()
    st.sidebar.write("For feedback / questions feel free to use my [Discord Server]("
                     "https://discord.com/channels/827836172184584214/981558870507929648)")
    st.sidebar.write("If you are interested in PoE Tips, solid builds and step-by-step guides consider subscribing "
                     "to my [YT channel](https://www.youtube.com/c/PoEAcademy)")


def load_data():
    dict_gem = dh.load_json()
    df = pd.DataFrame.from_dict(dict_gem, orient="index")
    return df


# @st.cache
def create_site():
    df = load_data()

    # settings
    st.set_page_config(layout="wide")

    create_top(df)

    create_plot(df)

    create_FAQ()

    create_sidebar()
