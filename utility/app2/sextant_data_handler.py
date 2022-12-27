import requests
from utility.data_handler import get_data_path, write_json


def load_data_from_github():
    URL_DATA = "https://raw.githubusercontent.com/The-Forbidden-Trove/tft-data-prices/master/lsc/bulk-compasses.json"
    req = requests.get(URL_DATA)
    # print(req.text)
    data = req.json()
    storage_path = get_data_path(filename="sextant_data_tft.json", subf="app2")
    write_json(data=data, file_path=storage_path)


def load_weightings_data():
    URL_DATA = "https://poedb.tw/us/Sextant#Sextant"
    req = requests.get(URL_DATA)
    # print(req.text)
    # data = req.json()
    a = 1
