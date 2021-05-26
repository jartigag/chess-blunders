#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


df_data = pd.read_csv('../data/interim/first_500k_lichess_db_standard_rated_2021-04.pgn.eval.blunders.csv')
df_data.head()


grouped_by_elo = df_data.groupby( pd.cut(df_data['Elo'], np.arange(1400, 3000, 200)) )
grouped_by_elo.size()


vc = grouped_by_elo.get_group(pd.Interval(1400, 1600, closed='right')).value_counts(['Move', 'FEN'])
vc[vc>1]

