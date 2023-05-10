# skill gems
import utility.app1.skillgems_data_handler as data_handler
import utility.app1.gem_margins as gem_margins

# sextants
# from utility.app2.sextant_data_handler import load_TFTdata_from_github, mix_sextant_info_and_tft_data
from utility.app2.sextant_data_handler import load_TFTdata_from_github, mix_sextant_info_and_tft_data, exclude_sextants

############################################################
# Skill gems
############################################################
# # get data from poe.ninja and save to db
# data_handler.load_all_categories()
# # create the df from poe.ninja data
# gem_margins.create_json_data()


############################################################
# sextants
############################################################
load_TFTdata_from_github()
mix_sextant_info_and_tft_data()
exclude_sextants()