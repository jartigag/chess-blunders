#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import glob

df_data202104 = pd.concat(map(pd.read_csv,
                        glob.glob('../data/interim/*lichess_db_standard_rated_2021-04*eval.blunders.csv')))
print("2021-04:",len(df_data202104),"rows")
df_data202104['Date'] = pd.to_datetime('2021-04')

df_data202002 = pd.concat(map(pd.read_csv,
                        glob.glob('../data/interim/*lichess_db_standard_rated_2020-02*eval.blunders.csv')))
print("2020-02:",len(df_data202002),"rows")
df_data202002['Date'] = pd.to_datetime('2020-02')

df_data = pd.concat([df_data202104, df_data202002])

df_data.head()


# # Explore by Elo

grouped_by_elo = df_data.groupby( pd.cut(df_data['Elo'], np.arange(600, 3000, 200)) )
grouped_by_elo.size()


for low_thr in range(600,2600,200):
    vc = grouped_by_elo.get_group(pd.Interval(low_thr, low_thr+200, closed='right')).value_counts(['Move', 'FEN'])
    #with pd.option_context('display.max_rows', 8):
    print(f"Elo: ({low_thr},{low_thr+200}]")
    print(vc[vc>1].head(5))
    print("---")


# # Explore by Date

grouped_by_elo = df_data.groupby( [pd.cut(df_data['Elo'], np.arange(600, 3000, 200)),'Date'] )
grouped_by_elo.size()


for low_thr in range(600,2600,200):
    #for date in grouped_by_elo.Date.unique():
    #for date in set([tup[1] for tup in list(grouped_by_elo.groups.keys())]):
    for date in [pd.Timestamp('2020-02-01 00:00:00'),pd.Timestamp('2021-04-01 00:00:00')]:
        vc = grouped_by_elo.get_group((pd.Interval(low_thr, low_thr+200, closed='right'),date)).value_counts(['Move', 'FEN'])
        print(f"Date: {date}. Elo: ({low_thr},{low_thr+200}]")
        print(vc[vc>1].head(5))
    print("---")


# # Explore by plots

vc = df_data.Move.value_counts()
vc[vc>7000].plot(kind='bar')


s = df_data.groupby(['Date','Move']).size().sort_values(ascending=False).to_frame('size').reset_index().set_index('Date')

for move, group in s[s['size']>3000].groupby('Move'):
    x = [t.to_pydatetime() for t in group.index]
    y = group['size'].to_list()
    plt.plot(x,y, label=move)

#plt.legend(loc='right', bbox_to_anchor=(1.5,0.5))
plt.ylim()
plt.show()


s.query("size>3000 & Date==datetime(2021,4,1)").sort_values(by='size', ascending=False)

