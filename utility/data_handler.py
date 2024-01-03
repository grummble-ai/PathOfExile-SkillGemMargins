import os
import json

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)


def get_data_path(filename: str, **kwargs):
    subfolder = kwargs.get('subf', None)
    if subfolder:
        path = os.path.join(ROOT_DIR, "data", subfolder, filename)
    else:
        path = os.path.join(ROOT_DIR, "data", filename)
    return path


def write_json(data, file_path: str):
    with open(file_path, 'wt') as outfile:
        json.dump(data, outfile)


def read_json(file_path: str):
    with open(file_path, 'r') as infile:
        data = json.load(infile)
    return data


def write_txt(file_path: str, mode: str, content: str):
    if mode != 'a' or mode != 'w' or mode != '+':
        ValueError("Provide appropriate writing mode: 'a', 'w', or '+'")
    with open(file_path, mode) as record:
        record.write(content)


def read_txt_lastentry(file_path):
    with open(file_path, "r") as f:
        content = f.readlines()[-1]
    return content


def get_currency_value_in_c(currency_name: str):
    path = get_data_path("currency_prices.json")
    json_data = read_json(path)
    curr_dict = next(item for item in json_data["lines"] if item["currencyTypeName"] == currency_name)
    # price: always chaos equivalent
    price = curr_dict["chaosEquivalent"]
    # time: represents when the poe.ninja fetched the data
    time = curr_dict["pay"]["sample_time_utc"]
    return price, time
