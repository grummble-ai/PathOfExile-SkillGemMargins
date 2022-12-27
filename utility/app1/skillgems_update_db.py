import skillgems_data_handler as data_handler
import gem_margins as gem_margins

# # get data from poe.ninja and save to db
data_handler.load_all_categories()

# create the df from poe.ninja data
gem_margins.create_json_data()
