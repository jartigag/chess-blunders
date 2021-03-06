#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df_list = []
for m in range(1,13):
    df = pd.read_csv(f'../data/interim/lichess_db_standard_rated_2020-{m:02d}.eval.blunders.csv')
    print(f"2020-{m:02d}:",len(df),"rows")
    df['Date'] = pd.to_datetime(f'2020-{m:02d}')
    df_list.append(df)

df_data = pd.concat([d for d in df_list])
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


for low_thr in [1600]:#range(600,2600,200):
    for date in pd.date_range(start='2020-01', periods=12, freq=pd.offsets.MonthBegin()):
        vc = grouped_by_elo.get_group((pd.Interval(low_thr, low_thr+200, closed='right'),date)).value_counts(['Move', 'FEN'])
        print(f"Date: {date}. Elo: ({low_thr},{low_thr+200}]")
        print(vc[vc>1].head(5))
    print("---")


# # Explore by plots

vc = df_data.value_counts(['Move', 'FEN'])
vc_gt400 = vc[vc>400]


vc_gt400.reset_index().plot(kind='bar',x='Move',legend=None) #.get_figure(); x.savefig('png', dpi=200)


#s = df_data.groupby(['Date','Move','FEN']).size().sort_values(ascending=False).to_frame('size')
s = df_data.value_counts(['Date', 'Move', 'FEN']).sort_values(ascending=False).to_frame('size')
s = s.reset_index().set_index('Date').sort_index()

data_dict = {}
for move, group in s[s['size']>400].groupby('Move'):
    data_dict[move] = {'date': [], 'size': []}
    data_dict[move]['date'] = [t.to_pydatetime() for t in group.index]
    data_dict[move]['size'] = group['size'].to_list()
    #plt.plot(x,y, label=move)

sorted_data = sorted(data_dict.items(), key = lambda kv:data_dict[kv[0]]['size'][-1], reverse=True)

'''
for row in sorted_data:
    move = row[0]
    x = row[1]['date']
    y = row[1]['size']
    plt.plot(x,y, label=move)

plt.legend(loc='right', bbox_to_anchor=(1.5,0.5))
plt.show()
'''

