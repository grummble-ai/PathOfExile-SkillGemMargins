from skillgems_data_handler import load_all_categories
from gem_margins import create_json_data

# # get data from poe.ninja and save to db
load_all_categories()

# create the df from poe.ninja data
create_json_data()