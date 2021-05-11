#!/bin/bash

extension="${1##*.}"
filename="${1%.*}"

if [ $extension == "bz2" ]
then
    #bunzip2 --keep $1
    bzcat $1 | grep -B18 "%eval" > "$filename.eval.pgn"
else
    grep -B18 "%eval" $filename.pgn > "$filename.eval.pgn"
fi
