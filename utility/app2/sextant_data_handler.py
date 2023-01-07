import json
import random

import requests
import pandas as pd
from utility.data_handler import get_data_path, write_json, read_json

SAVE_FILE_NAME = "sextant_info_and_data.json"
URL_TFT_DATA = "https://raw.githubusercontent.com/The-Forbidden-Trove/tft-data-prices/master/lsc/bulk-compasses.json"


def load_TFTdata_from_github():
    req = requests.get(URL_TFT_DATA)
    data = req.json()
    storage_path = get_data_path(filename="sextant_data_tft.json", subf="app2")
    write_json(data=data, file_path=storage_path)


def add_html_colors_to_confidence_val(df):
    green = "#008000"
    red = "#ff0000"
    df = df.assign(lowConfidenceHTML=
                   [f"<span style=\"color: {red}\">True</span>"
                    if x else f"<span style=\"color: {green}\">False</span>"
                    for x in df['lowConfidence']])
    return df


def save_mixed_data(df):
    storage_path = get_data_path(filename=SAVE_FILE_NAME, subf="app2")
    df.to_json(path_or_buf=storage_path)


def mix_sextant_info_and_tft_data():
    path_info = get_data_path(filename="raw_sextant_info.xlsx", subf="app2")
    df_raw = pd.read_excel(path_info, index_col="Nr")

    path_data = get_data_path(filename="sextant_data_tft.json", subf="app2")
    with open(path_data) as f:
        data_json = json.load(f)
    df_tft = pd.json_normalize(data_json, record_path=['data'], meta=['timestamp'])
    # merge both dataframes (raw data and TFT info together)
    df = df_raw.merge(df_tft, on="name")
    # exchange False and True with html spans including colors
    df = add_html_colors_to_confidence_val(df)
    save_mixed_data(df)


def exclude_minion_sextants():
    minion_sextants = ["Additional Monsters deal Fire",
                       "Additional Monsters deal Cold",
                       "Additional Monsters deal Lightning",
                       "Additional Monsters deal Physical",
                       "Additional Monsters deal Chaos"]
    path_data = get_data_path(filename="sextant_data_tft.json", subf="app2")
    data = read_json(path_data)
    sextant_data = data["data"]

    info = []
    exclude = []
    for minion_type in minion_sextants:
        sextant_dict = next(item for item in sextant_data if item["name"] == minion_type)
        info.append([sextant_dict["chaos"], minion_type])

    info_sorted = sorted(info, key=lambda x: int(x[0]))

    # take worst 3 entries and only save their names
    for slices in info_sorted[:3]:
        exclude.append(slices[1])

    write_json(exclude, get_data_path(filename="sextants_to_block.json", subf="app2"))


def objective_function():
    pass


def optimize_dataset():
    pass
