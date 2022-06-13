import data_handler
import gem_margins

# # get data from poe.ninja and save to db
data_handler.load_all_categories()

# create the df from poe.ninja data
gem_margins.calculate_margins()
