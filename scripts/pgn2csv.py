#!/usr/bin/env python3

import csv
import sys

dic_keys = ["Event"   , "Site"           , "Date"           , "Round"      , "White",
            "Black"   , "Result"         , "UTCDate"        , "UTCTime"    , "WhiteElo",
            "BlackElo", "WhiteRatingDiff", "BlackRatingDiff", "WhiteTitle" , "BlackTitle",
             "ECO"    , "Opening"        , "TimeControl"    , "Termination", "Game"]

dic = {k: None for k in dic_keys}

with open(sys.argv[1]) as f, open(f"{sys.argv[1]}.csv", 'w') as wf:
    writer = csv.DictWriter(wf, fieldnames=dic_keys)
    writer.writeheader()
    for l in f:
        if l[0] == "[":
            keyvalue = l[1:-1]
            key = keyvalue.split()[0]
            dic[key] = keyvalue[len(key):-2].strip().strip('"')
        if l[0] == "1":
            dic["Game"] = l.rstrip('\n')
            if dic['UTCDate']==None:
                #print(dic, file=sys.stderr) # to count games without header (using ./pgn2csv.py | wc -l)
                continue
            dic['Date'] = dic['UTCDate']+" "+dic['UTCTime']
            writer.writerow(dic)
            dic = {k: None for k in dic_keys}
        else:
            pass
