#!/bin/sh

total_num_lines=$(wc -l $2 | awk '{print $1}')
last_read_line=$1

pending_num_lines="$((total_num_lines-last_read_line))"

echo $(date)" - tail -n $pending_num_lines $2 | ./pgn2csv.py >/dev/null"
tail -n $pending_num_lines $2 | ./pgn2csv.py >/dev/null

echo $(date)" - cat output.csv >> $2"
cat output.csv >> $2
rm output.csv

echo $(date)" - done."
ls -lh $2.csv
