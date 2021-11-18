#!/usr/bin/env python3

import pandas as pd
import sys

dic_keys = ["Event"   , "Site"           , "Date"           , "Round"      , "White",
            "Black"   , "Result"         , "UTCDate"        , "UTCTime"    , "WhiteElo",
            "BlackElo", "WhiteRatingDiff", "BlackRatingDiff", "WhiteTitle" , "BlackTitle",
             "ECO"    , "Opening"        , "TimeControl"    , "Termination", "Game"]

with open(f"{sys.argv[1]}.csv", 'w') as wf:
    print(",".join(dic_keys), file=wf)

dic = {k: None for k in dic_keys}

with open(sys.argv[1]) as f:
    for l in f:
        if l[0] == "[":
            keyvalue = l[1:-1]
            key = keyvalue.split()[0]
            dic[key] = keyvalue[len(key):-2].strip().strip('"')
        if l[0] == "1":
            dic["Game"] = l.rstrip('\n')
            df = pd.DataFrame([dic])
            try:
                df['Date'] = pd.to_datetime(df['UTCDate']+" "+df['UTCTime'])
                df.to_csv(f"{sys.argv[1]}.csv", mode='a', index=False, header=False)
            except KeyError:
                pass
            dic = {k: None for k in dic_keys}
        else:
            pass
