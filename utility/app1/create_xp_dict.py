import pandas as pd
from pandas import *
df = pd.read_excel('regular_gem_xp.xlsx', index_col=0)
df.to_pickle('regular_gem_xp_df')