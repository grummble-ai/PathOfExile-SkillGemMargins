from utility.data_handler import get_data_path, write_txt
import pandas as pd


# load raw data and make it a json
path_to_data = get_data_path("raw_sextant_info", subf="app2")
path_to_excel = path_to_data + ".xlsx"
df = pd.read_excel(path_to_excel, sheet_name="awksextants", header=0, index_col=0)
df.to_json(path_to_data + ".json", indent=4, orient="index")

# find the weightings total for future calculations
path_to_weights = get_data_path("sextants_weights_total.txt", subf="app2")
df_sum = df.sum(axis=0)
weights_total = df_sum["w_default"]
write_txt(path_to_weights, 'w', str(weights_total))
