import pandas as pd
from utility.data_handler import get_data_path, read_json
from datetime import datetime
import streamlit as st
import os
import base64


def default_img_url(type: str):
    if type == "chaos":
        URL = "https://web.poecdn.com/image/Art/2DItems/Currency/CurrencyRerollRare.png?scale=1&w=1&h=1"
    elif type == "divine":
        URL = "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lNb2RWYWx1ZXMiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MX1d/e1a54ff97d/CurrencyModValues.png"
    elif type == "awksextant":
        URL = "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQXRsYXNSYWRpdXNUaWVyMyIsInciOjEsImgiOjEsInNjYWxlIjoxfV0/07377648d7/AtlasRadiusTier3.png"
    else:
        ValueError("Function default_img_url does not include the corresponding url. Please provide a different type.")
    return URL


def convert_df(input_df):
    html = input_df.to_html(escape=False, index=False)
    html_title_centered = html.replace('<th>', '<th align="center">')
    return html_title_centered


def load_mixed_data():
    storage_path = get_data_path(filename="sextant_info_and_data.json", subf="app2")
    df = pd.read_json(path_or_buf=storage_path)
    return df


# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="40" >'


def df_drop_column(df, columns_to_drop: list):
    df = df.drop(columns_to_drop, axis=1)
    return df


def df_rename_columns(df, column_names: dict):
    df = df.rename(columns=column_names)
    return df


def column_title_link_to_html(img_link: str, **kwargs):
    text = kwargs.get('text', None)
    str_left = '<img src="'
    str_right = '" width="25" >'
    if text:
        html = text + " " + str_left + img_link + str_right
    else:
        html = str_left + img_link + str_right
    return html


def sort_df_keep_X_best_results(df, column_name: str, count_results: int):
    df = df.nlargest(count_results, column_name, keep="first")
    return df


def total_count_sextant_mods(df):
    length = len(df.index)
    return length


def keep_rows_depending_on_conent_of_column(df, column_name: str, column_value):
    df = df[df[column_name] == column_value]
    return df


def calc_exp_val_sextants(df, df_basis):
    total_weights = df_basis["w_default"].sum()
    df_multiplied = df["w_default"] * df["chaos"]
    sum = df_multiplied.sum()
    exp_val = sum / int(total_weights)
    return exp_val, total_weights


def timestamp_to_date(timestamp):
    date_obj = datetime.strptime((timestamp[:19]).strip(), '%Y-%m-%dT%H:%M:%S')
    date = date_obj.strftime("%d.%m.%Y, %H:%M")
    return date


def block_sextants(df):
    sextants_to_block = read_json(get_data_path("sextants_to_block.json", subf="app2"))
    for sextant in sextants_to_block[1]:
        df = df[df["name"] != sextant]

    return df, sextants_to_block[1]


# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="40" >'


def convert_df_with_icon(input_df):
    html = input_df.to_html(escape=False, formatters=dict(Icon=path_to_image_html), index=False)
    html_title_centered = html.replace('<th>', '<th align="center">')
    return html_title_centered


def swap_df_columns(df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df

    # # TODO: THIS FUNCTION DOES NOT FIND THE GLOBAL OPTIMUM! REMOVING 3x ADDITIONAL MONSTERS YIELDS 9.14 WHILE
    # df_raw = df
    # exp_val_raw = calculate_expected_value_sextants(df_raw)
    #
    # rows_removed_ind = []
    # rows_removed_names = []
    #
    # for x in range(0, 3):
    #     exp_val = []
    #     df_reset = df_raw.reset_index()
    #     # drop all removed rows from raw dataframe
    #     if rows_removed_ind:
    #         for row in rows_removed_ind:# drop least desired rows from df
    #             df_reset = df_reset[df_reset.index != row]
    #
    #     df_sliced = df_reset
    #
    #     # iterate through every single row and check the contribution level of it
    #     for idx, row in df_sliced.iterrows():
    #         name = row["name"]
    #         index_sextant = row["index"]
    #         df_check = df_sliced.drop(idx)
    #         val, tot_weight = calculate_expected_value_sextants(df_check)
    #         exp_val.append(val)
    #
    #     ind_removal = exp_val.index(max(exp_val))
    #     rows_removed_ind.append(ind_removal)
    #
    # df_clensed = df_raw.reset_index()
    # for row in rows_removed_ind:
    #     row_series = df_raw[df_raw.index == row]
    #     rows_removed_names.append(row_series["name"].values[0])
    #     df_clensed = df_clensed[df_clensed.index != row]
    #
    # # calculate results with clensed dataframe
    # final_val, final_weight = calculate_expected_value_sextants(df_clensed)
    #
    # # calculate the resulting improvements for gross profits
    # final_improvement = final_val - exp_val_raw[0]
    # return df_clensed, rows_removed_ind, rows_removed_names, final_val, final_weight, final_improvement


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url, max_width_percent: int):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''<div width=\"200px\">
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" style="max-width: {max_width_percent}%"/>
        </a>
        </div>'''
    return html_code


def df_get_max_col(df, col_name: str):
    series_max_val = df.loc[df[col_name].idxmax()]
    max_val_raw = series_max_val[col_name]
    max_val = round(float(max_val_raw), 0) + 1
    return int(max_val)


def get_low_confidence_count(df):
    result_df = df[df['lowConfidence'] == True]
    count = len(result_df.index)
    return count
