#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


import glob
df_data = pd.concat(map(pd.read_csv,
                        glob.glob('../data/interim/*lichess_db_standard_rated_2021-04.eval.blunders.csv')))
print(len(df_data),"rows")
df_data.head()


# # Explore by Elo

grouped_by_elo = df_data.groupby( pd.cut(df_data['Elo'], np.arange(600, 3000, 200)) )
grouped_by_elo.size()


for low_thr in range(600,2600,200):
    vc = grouped_by_elo.get_group(pd.Interval(low_thr, low_thr+200, closed='right')).value_counts(['Move', 'FEN'])
    #with pd.option_context('display.max_rows', 8):
    print(f"Elo: ({low_thr},{low_thr+200}]")
    print(vc[vc>1].head(10))
    print("---")

