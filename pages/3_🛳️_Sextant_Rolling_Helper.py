import streamlit as st
from utility.firebase_operations import add_action_to_db
import widgets.initializer as initializer
from PIL import Image
from utility.data_handler import get_currency_value_in_c
from utility.plot_utility import convert_df, df_drop_column, load_mixed_data, df_rename_columns, default_img_url, \
    column_title_link_to_html, sort_df_keep_X_best_results, total_count_sextant_mods, \
    keep_rows_depending_on_conent_of_column, calc_exp_val_sextants, timestamp_to_date, \
    block_sextants, convert_df_with_icon, swap_df_columns

SUBHEADER = '''This tool is still being tested. 
            Please [report any bugs / feedback to me](https://discord.gg/KHakZVKPRu).'''
VERSION = "0.9.3"


def create_table():
    #TODO: it seems that all additional monster sextants are missing although I'm just blocking 3 of them?
    #############
    # preparation
    #############
    df = st.session_state.df_raw

    # filter sextants to block
    st.session_state.df_blocked, st.session_state.sextant_to_block = block_sextants(df)
    df = st.session_state.df_blocked

    # hide low confidence
    if st.session_state.hide_low_confidence:
        df = keep_rows_depending_on_conent_of_column(df, column_name="lowConfidence", column_value=False)

    # sort df from most valuable to least valuable and filter for x best results
    df = sort_df_keep_X_best_results(df, "chaos", st.session_state.nr_results)

    #############
    # clean-up
    #############
    # calculate the expected value with filters
    st.session_state.df_sliced = df

    # remove unwanted columns
    df = df_drop_column(df, ["Level", "Line0", "Line1", "Line2", "Line3", "Spalte1", "lowConfidence",
                             "w_has_atlas_mission", "w_hall_of_grandmasters", "ratio", "w_no_strongboxes",
                             "w_unique_map", "w_no_monster_packs", "w_no_boss", "w_map_has_blight",
                             "w_vault_of_atziri", "w_elder_occupied", "timestamp", "Item"])

    df = swap_df_columns(df, "name", "icon")

    # rename df columns
    df = df_rename_columns(df, {"name": "Short Name",
                                "icon": "Icon",
                                "full_text": "Description",
                                "w_default": "Weighting",
                                "divine": "TFT Bulk Price in " + st.session_state.html_divine,
                                "chaos": "TFT Bulk Price in " + st.session_state.html_chaos,
                                "lowConfidenceHTML": "Low Confidence"})

    st.session_state.html_table = convert_df_with_icon(df)


def create_part1():
    image = Image.open("img/Under-Construction.png")
    st.image(image, width=300)

    st.markdown("-----")
    # Settings
    colfirst, ph1, colsecond, ph2, colthird, ph3, colfourth = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])

    with colfirst:
        st.subheader("1️  Settings")
        st.markdown("Low Confidence:")
        st.checkbox(label="Exclude Low Confidence Sextants",
                    # value=st.session_state.hide_low_confidence,
                    key="hide_low_confidence")

        st.slider(label="I am confident this many rolls will sell:",
                  max_value=st.session_state.cnt_sextants,
                  key="nr_results")
        st.caption(
            "70/70 would mean that you are confident that all rolls sell; 17/68 means that the best 25% would sell.")

    with colsecond:
        exp_val_sliced, total_weights_sliced = calc_exp_val_sextants(st.session_state.df_sliced,
                                                                     st.session_state.df_blocked)

        st.subheader("2️ Check If Worth It")

        if round(exp_val_sliced, 2):
            gross_color = ":green["
        else:
            gross_color = ":red["

        st.markdown("Avg. __Gross__ Profit = " + gross_color + str(round(exp_val_sliced, 2)) + "] " + str(
            st.session_state.html_chaos), unsafe_allow_html=True)
        st.caption(
            f"Assuming that only {st.session_state.nr_results} out of {st.session_state.cnt_sextants} sextant rolls "
            f"(depending on your settings) will sell __AND__ you block the 3 sextant rolls in the list on the "
            f"right for rolling sextants; It would be " +
            str(round(st.session_state.exp_val_raw, 2)) + f" Chaos without any filters, i.e. rolling without blocking "
                                                          f"and all {st.session_state.cnt_sextants} sextant rolls "
                                                          f"would sell.")

        if round(exp_val_sliced - st.session_state.price_awk - 1, 2) > 0:
            net_color = ":green["
            # - 1 considers 1 chaos orb for the Surveyor's Compass
        else:
            net_color = ":red["

        st.markdown(
            "Avg. __Net__ Profit = **" + net_color + str(round(exp_val_sliced - st.session_state.price_awk - 1, 2))
            + "]** " + str(st.session_state.html_chaos),
            unsafe_allow_html=True)
        st.caption(f"Your true average profit as it considers expenditures: Net = Gross - Awk. Sextant Price - "
                   f"Surveyor's Compass Price = " +
                   str(round(exp_val_sliced, 2)) + "C - " +
                   str(st.session_state.price_awk) + "C - 1C ")

        # sextant_per_div = round(st.session_state.price_div / st.session_state.price_awk, 2)
        # st.markdown(
        #     str(st.session_state.html_awk_sextant) + " / " + str(st.session_state.html_divine) + " = " + str(
        #         sextant_per_div),
        #     unsafe_allow_html=True
        # )

    with colthird:
        st.subheader("3️ How to roll Sextants?")
        st.markdown("""
                            1. You need :red[4] voidstones
                            2. Allocate the Atlas passive :red[Enduring Influence] for 4 instead of 3 uses:
                            """)
        image = Image.open("img/enduring_influence.png")
        st.image(image)

    with colfourth:
        st.markdown(f"""
                    3. Block these 3 Sextants mods on 3 of your voidstones: 
                    - *{st.session_state.sextant_to_block[0]}*
                    - *{st.session_state.sextant_to_block[1]}*
                    - *{st.session_state.sextant_to_block[2]}*
                    4. Roll sextant mods on the last Voidstone :red[ON YOUR ATLAS]
                    5. Itemize each worthy sextant rolls with :red[Surveyor's Compass] for 1c @ Kirac
                    6. Sell on [trade](https://www.pathofexile.com/trade) or in bulk on [TFT Discord](https://discord.com/invite/tftrove)
                    """)
        st.caption("The best sextants to block are updated automatically.")
    st.markdown("---")


def create_part2():
    st.subheader("3: Itemize Roll Whenever You Hit Something Good:")
    st.caption("_The table below updates automatically after changes._\n")

    st.markdown(
        st.session_state.html_table,
        unsafe_allow_html=True
    )

    st.caption(
        f"PoE Ninja and TFT fetched on {timestamp_to_date(st.session_state.timestamp)} GMT+2.")


def create_FAQ():
    with st.expander("FAQ (click me)"):
        st.write("""
                **How does it work?** \n
                The tool grabs data from poe ninja (currency prices) and TFT bulk selling data. It then calculates 
                the expected value depending on value and weight of possible rolls. Remember that this represents the 
                value you'd get if you'd roll a really large number of sextants ("infinite" rolls). 
                
                **Gross Profit vs. Net Profit** \n
                _Gross Profit_ is your turnover, if you'd sell everything but don't consider how much you've payed for it. 
                The number can be useful if you have farmed the sextants yourself for example and don't have to pay for
                them but usually you will just buy awakened sextants in bulk. \n
                _Net Profit_ is your turnover minus cost. Costs are awakened sextants (depending on the market) and 
                suveyor's compasses (always 1c each @ Kirac)
                
                **What is low confidence?**\n
                You can exclude low confidence values which are tagged as such by TFT. I don't know how they define this
                but it's the best we got.   
                
                **What is "I am confident this many rolls will sell"?**\n
                You can reduce the number of entries shown in the table. This will always drop the least profitable rolls
                (I suspect that you can't sell these) which reduces the average net profit (less chance of hitting 
                something worthwhile. 
                
                **Potential improvements**\n
                - Currently the tool only picks the least favorable sextant mod from the added minion mods (usually 
                cheap and high weighting), however, an optimization would be suited better IMO and I will think about
                adding something like this if the tool gets some traction.
                - Add elevated sextants to the party if there's is any data on them available in the future (TFT, poe.ninja?)
                """)


def create_changelog():
    with st.expander("Changelog"):
        st.write("""
            **Version 0.9.3** (31th of January, 2023) \n
            - Reworked Section 2 "Check If Worth It" for more clarity
            - Minor improvements to the UI
            **Version 0.9.2** (7th of January, 2023) \n
            - Added line breaks to mod description
            - Improvements to visual clarity in the table
            **Version 0.9.1** (7th of January, 2023) \n
            - Fixed timestamp bug
            **Version 0.9.0** (7th of January, 2023) \n
            - Added the basic functionalities
        """)


def create_site():
    create_part1()
    create_part2()
    create_FAQ()
    create_changelog()


def sessionstate_init():
    # set default values
    df_raw = load_mixed_data()
    if 'df_raw' not in st.session_state:
        st.session_state.df_raw = df_raw

    if 'df_sliced' not in st.session_state:
        st.session_state.df_sliced = df_raw

    if 'df_blocked' not in st.session_state:
        st.session_state.df_blocked = df_raw

    if 'exp_val_raw' not in st.session_state:
        st.session_state.exp_val_raw, tot_weights_raw = calc_exp_val_sextants(st.session_state.df_raw,
                                                                              st.session_state.df_raw)

    if 'hide_low_confidence' not in st.session_state:
        st.session_state.hide_low_confidence = True

    if 'cnt_sextants' not in st.session_state:
        st.session_state.cnt_sextants = total_count_sextant_mods(st.session_state.df_raw)

    if 'nr_results' not in st.session_state:
        st.session_state.nr_results = st.session_state.cnt_sextants

    if 'html_divine' not in st.session_state:
        url = default_img_url(type="divine")
        st.session_state.html_divine = column_title_link_to_html(url, text="Divine")

    if 'html_chaos' not in st.session_state:
        url = default_img_url(type="chaos")
        st.session_state.html_chaos = column_title_link_to_html(url, text="Chaos")

    if 'html_awk_sextant' not in st.session_state:
        url = default_img_url(type="awksextant")
        st.session_state.html_awk_sextant = column_title_link_to_html(url, text="Awk. Sextant")

    if 'price_div' not in st.session_state:
        price, time = get_currency_value_in_c("Divine Orb")
        st.session_state.price_div = price
        st.session_state.timestamp = time

    if 'price_awk' not in st.session_state:
        price, time = get_currency_value_in_c("Awakened Sextant")
        st.session_state.price_awk = price

    if 'sextant_to_block' not in st.session_state:
        st.session_state.sextant_to_block = []

    if 'html_table' not in st.session_state:
        st.session_state.html_table = ""


#
initializer.create_boilerplate(pagetitle="Sextant Rolling Helper", version=VERSION, subheader=SUBHEADER)

# initialize session state
sessionstate_init()

create_table()
# create website
create_site()
