import os

import pandas as pd
from utility.app1 import skillgems_data_handler as dh
from os import path

pd.options.mode.chained_assignment = None

GEM_EXPERIENCE_AWAKENED = 1920762677  # to level 5; #TODO: awakened gems seem to have different xp requirements?
GEM_EXPERIENCE_ENLEMPENH = 1666045137  # to level 3; for enhance, empower and enlighten
GEM_EXPERIENCE_BLOODANDSAND = 529166003  # to level 6;
GEM_EXPERIENCE_BRANDRECALL = 341913067  # to level 6
GEM_EXPERIENCE_REGULAR = 684009294  # to level 20/20;
MAX_EXP = max(GEM_EXPERIENCE_AWAKENED, GEM_EXPERIENCE_ENLEMPENH, GEM_EXPERIENCE_BLOODANDSAND,
              GEM_EXPERIENCE_BRANDRECALL, GEM_EXPERIENCE_REGULAR)

GEM_EXPERIENCE = {"awakened": GEM_EXPERIENCE_AWAKENED,
                  "enlempenh": GEM_EXPERIENCE_ENLEMPENH,
                  "bloodandsand": GEM_EXPERIENCE_BLOODANDSAND,
                  "brandrecall": GEM_EXPERIENCE_BRANDRECALL,
                  "regular": GEM_EXPERIENCE_REGULAR,
                  "awakened_norm": GEM_EXPERIENCE_AWAKENED / MAX_EXP,
                  "enlempenh_norm": GEM_EXPERIENCE_ENLEMPENH / MAX_EXP,
                  "bloodandsand_norm": GEM_EXPERIENCE_BLOODANDSAND / MAX_EXP,
                  "brandrecall_norm": GEM_EXPERIENCE_BRANDRECALL / MAX_EXP,
                  "regular_norm": GEM_EXPERIENCE_REGULAR / MAX_EXP,
                  }


def get_ex_value(df):
    divine_value = df.loc['Divine Orb'][0]
    df['value_divine'] = df['value'].div(divine_value)
    return df


def add_gem_colors(df):
    df_colors = pd.read_excel(path.join(os.getcwd(), "utility", "app1", "gem_colors.xlsx"))
    # drop zeros from excel
    df_colors[(df_colors != 0).all(1)]
    df_colors = df_colors[~(df_colors == 0).any(axis=1)]
    gem_colors = df_colors.values.tolist()
    for gem in gem_colors:
        df.loc[df['skill'] == gem[0], 'gem_color'] = gem[1]
    return df


def add_gem_types(df):
    df['gem_type'] = "regular"
    df.loc[df['name'].str.contains("Awakened"), 'gem_type'] = "awakened"
    df.loc[df['name'].str.contains("Enlighten"), 'gem_type'] = "exceptional"
    df.loc[df['name'].str.contains("Empower"), 'gem_type'] = "exceptional"
    df.loc[df['name'].str.contains("Enhance"), 'gem_type'] = "exceptional"
    df.loc[df['name'] == "Blood and Sand", 'gem_type'] = "special"
    df.loc[df['name'] == "Brand Recall", 'gem_type'] = "special"

    return df


def calculate_chaos_values(df):
    unique_names = df.drop_duplicates(subset="name")
    names = unique_names["name"].tolist()

    # create a new dataframe with all columns that will be filled using the loop below
    df_analyzed = df[0:0]

    for idx, gems in enumerate(names):
        # iterate trough every gem in the gem list (e.g. Lightning Strike, Hatred, ...)
        df_ = df[df['name'] == gems]

        # find the cheapest entry in the group and use it as a basis
        df_min = df_[df_.corrupted == df_.corrupted.min()]
        df_min = df_min[df_min.gemQuality == df_min.gemQuality.min()]
        df_min = df_min[df_min.gemLevel == df_min.gemLevel.min()]
        df_min = df_min[df_min.value_chaos == df_min.value_chaos.min()]
        # # For debugging
        # if df_min.corrupted[0] is True:
        #     print(f"no uncorrupted version found for gem: {gems}")

        # iterate through every single gem entry for a give gem (e.g. 8/0, 16/0 and 20/20 for Lightning Strike)
        for i in range(df_.shape[0]):
            df_gem = df_.iloc[[i]]
            # calculate the important metrics
            buy_c = df_min["value_chaos"].values[0]
            sell_c = df_gem["value_chaos"].values[0]
            margin_c = sell_c - buy_c
            roi_c = margin_c / buy_c

            # add them to the highest level / quality gem dataframe
            df_gem["buy_c"] = buy_c
            df_gem["sell_c"] = sell_c
            df_gem["margin_c"] = margin_c
            df_gem["roi"] = roi_c

            df_gem["gem_level_base"] = df_min['gemLevel'].values[0]
            df_gem["gem_quality_base"] = df_min['gemQuality'].values[0]

            # upgrade path
            if df_gem["corrupted"].values[0]:
                df_gem["upgrade_path"] = '[' + str(df_min['gemLevel'].values[0]) \
                                         + '/' + str(df_min['gemQuality'].values[0]) \
                                         + '] -> [' + str(df_gem['gemLevel'].values[0]) \
                                         + '/' + str(df_gem['gemQuality'].values[0]) + '] ©'
            else:
                df_gem["upgrade_path"] = '[' + str(df_min['gemLevel'].values[0]) \
                                         + '/' + str(df_min['gemQuality'].values[0]) \
                                         + '] -> [' + str(df_gem['gemLevel'].values[0]) \
                                         + '/' + str(df_gem['gemQuality'].values[0]) + ']'

            # append the resulting dataframe
            df_analyzed = pd.concat([df_analyzed, df_gem], ignore_index=True)

    return df_analyzed


def calculate_divine_values(df, C_TO_DIV):
    df['buy_divine'] = df['buy_c'].div(C_TO_DIV)
    df['sell_divine'] = df['sell_c'].div(C_TO_DIV)
    df['margin_divine'] = df['margin_c'].div(C_TO_DIV)

    return df


def xp_requirement_regular_gems(df):
    df_reg_gem_xp = pd.read_pickle(path.join(os.getcwd(), "utility", "app1", "regular_gem_xp_df"))

    # warnings.simplefilter('error')

    # iterate through all entries in gem list
    for i in df.index:
        gem_type = df.iloc[i]["gem_type"]
        if gem_type == "regular":
            gem_level_base = df.iloc[i]["gem_level_base"]
            gem_quali_base = df.iloc[i]["gem_quality_base"]
            gem_level = df.iloc[i]["gemLevel"]
            gem_quali = df.iloc[i]["gemQuality"]
            gem_name = df.iloc[i]["name"]

            # don't do anything if they have the same level / qual
            if not (gem_level_base == gem_level and gem_quali_base == gem_quali):
                # find the right number in the xp matrix
                if gem_quali_base > 0:
                    ind_x = gem_level_base - 1 + 20
                else:
                    ind_x = gem_level_base - 1

                if gem_quali > 0 and 1 <= gem_level <= 20:
                    ind_y = gem_level - 1 + 20
                elif gem_quali > 0 and gem_level == 21:
                    ind_y = gem_level - 2 + 20
                else:
                    ind_y = gem_level - 1

                xp_required_raw = df_reg_gem_xp.iloc[ind_y]
                xp_required = xp_required_raw.iloc[ind_x]
                margin_divine_norm = df.iloc[i]['margin_divine'] / (xp_required / MAX_EXP)

                df.loc[i, 'margin_gem_specific'] = margin_divine_norm

            else:
                # mainly used for the same gems: [16/0] -> [16/0] no xp so margin_gem_specific == margin_divine
                df.loc[i, 'margin_gem_specific'] = df.iloc[i]["margin_divine"]

    return df


def calculate_margin_per_xp_and_ranking(df):
    # --- normalize margin depending on xp required ---
    # df['margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE['regular_norm']
    df.loc[df['name'].str.contains("Awakened"), 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE[
        'awakened_norm']
    df.loc[df['name'].str.contains("Enlighten"), 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE[
        'enlempenh_norm']
    df.loc[df['name'].str.contains("Empower"), 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE[
        'enlempenh_norm']
    df.loc[df['name'].str.contains("Enhance"), 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE[
        'enlempenh_norm']
    df.loc[df['name'] == "Blood and Sand", 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE[
        'bloodandsand_norm']
    df.loc[df['name'] == "Brand Recall", 'margin_gem_specific'] = df['margin_divine'] / GEM_EXPERIENCE['brandrecall_norm']

    # calculate margins for regular gems
    df = xp_requirement_regular_gems(df)

    # rank entries after roi
    df["ranking_from_margin_gem_specific"] = df['margin_gem_specific'].rank(ascending=False)
    df["ranking_from_roi"] = df['roi'].rank(ascending=False)

    # sort out all rows with no return of investment (margin 0 or even negative)
    df = df[df["roi"] > 0]

    return df


def remove_low_confidence(df, list_cnt):
    unique_gems = list(df['name'].unique())
    skills_to_keep, skills_to_delete = [], []

    for name in unique_gems:
        df_ = df[(df['name'] == name)]
        cnt = list(df_["listingcount"])
        if cnt[0] > list_cnt:
            skills_to_keep.append(name)

    df_conf = df[df['name'].isin(skills_to_keep)]

    return df_conf


def create_query_url(LEAGUE:str, name:str, skill:str, type_qual:str, corr:str):
    # create the name string, format: %22Awakened%20Multistrike%20Support%22 (does not add %20 if only single word!
    if type_qual == "Anomalous" or "Divergent" or "Phantasmal":
        skill_name = skill
        # anomalous: %22gem_alternate_quality%22:{%22option%22:%221%22},
        # phantasmal: %22gem_alternate_quality%22:{%22option%22:%223%22},
        # divergent: %22gem_alternate_quality%22:{%22option%22:%222%22},
        if type_qual == "Anomalous":
            alternate_qual = "%22gem_alternate_quality%22:{%22option%22:%221%22},"
        elif type_qual == "Phantasmal":
            alternate_qual = "%22gem_alternate_quality%22:{%22option%22:%223%22},"
        elif type_qual == "Divergent":
            alternate_qual = "%22gem_alternate_quality%22:{%22option%22:%222%22},"
        else:
            alternate_qual = ""

    else:
        alternate_qual = ""
        skill_name = name

    name_str = "%22" + skill_name.replace(" ", "%20") + "%22"

    query_url = (
        f"https://www.pathofexile.com/trade/search/{LEAGUE}?q={{"
        "%22query%22:{%22filters%22:{%22misc_filters%22:{%22filters%22:{"
        f"%22gem_level%22:{{%22min%22:1}},{alternate_qual}%22corrupted%22:{{%22option%22:{corr}}},%22quality%22:{{%22min%22:0}}"
        f"}}}}}},%22type%22:{name_str}}}}}"
    )
    return query_url


def create_query_html(query_url:str):
    # query_html = fr"<a href={query_url} Buy</a>"
    query_html = f"""<a class="button" target="_blank" title="Buy on pathofexile.com/trade" href={query_url} role="button" data-variant="round" data-size="small" style="font-family: "Source Sans Pro", sans-serif; color: rgb(255, 75, 75);">Trade <svg aria-hidden="true" data-prefix="fas" data-icon="exchange-alt" class="icon-exchange-alt-solid_svg__svg-inline--fa icon-exchange-alt-solid_svg__fa-exchange-alt icon-exchange-alt-solid_svg__fa-w-16" viewBox="0 0 512 512" width="1em" height="1em"><path fill="currentColor" d="M0 168v-16c0-13.255 10.745-24 24-24h360V80c0-21.367 25.899-32.042 40.971-16.971l80 80c9.372 9.373 9.372 24.569 0 33.941l-80 80C409.956 271.982 384 261.456 384 240v-48H24c-13.255 0-24-10.745-24-24zm488 152H128v-48c0-21.314-25.862-32.08-40.971-16.971l-80 80c-9.372 9.373-9.372 24.569 0 33.941l80 80C102.057 463.997 128 453.437 128 432v-48h360c13.255 0 24-10.745 24-24v-16c0-13.255-10.745-24-24-24z"></path></svg></a>"""
    return query_html


def add_search_url(df):
    LEAGUE = dh.load_league()

    unique_names = df.drop_duplicates(subset="name")
    names = unique_names["name"].tolist()

    # create a new dataframe with all columns that will be filled using the loop below
    df_urls_added = df[0:0]

    for idx, gems in enumerate(names):
        # iterate trough every gem in the gem list (e.g. Lightning Strike, Hatred, ...)
        df_ = df[df['name'] == gems]

        # iterate through every single gem entry for a give gem (e.g. 8/0, 16/0 and 20/20 for Lightning Strike)
        for i in range(df_.shape[0]):
            df_gem = df_.iloc[[i]]

            # get the gem quality, gemlevel name and quality type
            name = df_gem["name"].values[0]
            skill = df_gem["skill"].values[0]
            type_qual = df_gem["qualityType"].values[0]

            # create the query url from gem info
            url = create_query_url(LEAGUE, name, skill, type_qual, corr="false")
            df_gem["query_url"] = url

            # create the query html from query url
            html = create_query_html(url)
            df_gem["query_html"] = html

            # append the resulting dataframe
            df_urls_added = pd.concat([df_urls_added, df_gem], ignore_index=True)

    return df_urls_added


def create_json_data():
    dict_cur = dh.load_raw_dict(type="Currency")
    data_cur = pd.DataFrame.from_dict(dict_cur, orient="index")
    dict_gem = dh.load_raw_dict(type="Gems")
    data_gem = pd.DataFrame.from_dict(dict_gem, orient="index")
    df_raw = data_gem

    # --- currency ---
    C_TO_DIV = data_cur[data_cur['name'] == "Divine Orb"]['value_chaos'].values[0]

    # --- gems ---
    # sort gems
    df = data_gem.sort_values(['skill', 'qualityType', 'gemLevel'], ascending=[True, True, False])

    # add gem type, i.e. Enlighten -> Exceptional; types: regular, awakened, exceptional, special (blood and sand & brand recall)
    df["gem_type"] = ""
    df = add_gem_types(df)

    # remove vaal skill gems
    df = df[~df.name.str.contains("Vaal")]

    # df["gem_info"] = ""

    df["gem_level_base"] = ""
    df["gem_quality_base"] = ""
    df["upgrade_path"] = ""
    df["buy_c"] = ""
    df["sell_c"] = ""
    df["margin_c"] = ""
    df["buy_divine"] = ""
    df["sell_divine"] = ""
    df["margin_divine"] = ""
    df["margin_gem_specific"] = ""
    df["roi"] = ""
    df["ranking_from_roi"] = ""
    df["gem_color"] = ""
    df["query_url"] = ""
    df["query_html"] = ""


    df = calculate_chaos_values(df)

    df = calculate_divine_values(df, C_TO_DIV)

    df = calculate_margin_per_xp_and_ranking(df)

    df = add_gem_colors(df)

    df = add_search_url(df)

    gems_analyzed = df.to_dict(orient="index")
    dh.save_json(gems_analyzed)
