from utility.data_handler import get_data_path
import pandas as pd


# load raw data and make it a json
path_to_data = get_data_path("raw_sextant_info", subf="app2")
path_to_excel = path_to_data + ".xlsx"
df = pd.read_excel(path_to_excel, sheet_name="awksextants", header=0, index_col=0)
df.to_json(path_to_data + ".json", indent=4, orient="index")
