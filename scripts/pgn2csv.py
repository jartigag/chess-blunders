#!/usr/bin/env python3
#
# recommended usage:
# ./pgn2csv.py input.pgn | wc -l
# or
# ./pgn2csv.py input.pgn >/dev/null

import csv
import sys
import signal


def print_status_info():
    global written_lines
    print(file=sys.stderr)
    print("last read date-time:",dic['UTCDate'],dic['UTCTime'],file=sys.stderr)
    print("last read players:  ",dic['White'],dic['Black']    ,file=sys.stderr)
    print("last read line:     ",line                         ,file=sys.stderr)
    print(f"read lines:    {numline:,}"                       ,file=sys.stderr)
    print(f"written lines: {written_lines:,}"                 ,file=sys.stderr)
    sys.exit(-1)


def sigint_handler(signal, frame):
    print_status_info()


if __name__ == '__main__':
    written_lines = 0

    signal.signal(signal.SIGINT, sigint_handler)

    dic_keys = ["Event"   , "Site"           , "Date"           , "Round"      , "White",
                "Black"   , "Result"         , "UTCDate"        , "UTCTime"    , "WhiteElo",
                "BlackElo", "WhiteRatingDiff", "BlackRatingDiff", "WhiteTitle" , "BlackTitle",
                 "ECO"    , "Opening"        , "TimeControl"    , "Termination", "Game"]

    dic = {k: None for k in dic_keys}

    with open(sys.argv[1]) as f, open(f"{sys.argv[1]}.csv", 'w') as wf:
        writer = csv.DictWriter(wf, fieldnames=dic_keys)
        writer.writeheader()
        for numline,line in enumerate(f):
            try:
                if line[0] == "[":
                    keyvalue = line[1:-1]
                    key = keyvalue.split()[0]
                    dic[key] = keyvalue[len(key):-2].strip().strip('"')
                if line[0] == "1":
                    dic["Game"] = line.rstrip('\n')
                    if dic['UTCDate']==None:
                        print("\033[0;31m[-]\033[0m game without header (no metadata), so it will be discarded:", line, file=sys.stdout) # to count them, ./pgn2csv.py input.pgn | wc -l
                        continue
                    dic['Date'] = dic['UTCDate']+" "+dic['UTCTime']
                    writer.writerow(dic)
                    written_lines += 1
                    dic = {k: None for k in dic_keys}
                else:
                    pass
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                print(f'File "{fname}", line {exc_tb.tb_lineno}\n{type(e).__name__}: {e}', file=sys.stderr)
                print_status_info()
