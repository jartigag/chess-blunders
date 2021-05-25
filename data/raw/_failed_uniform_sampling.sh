#!/bin/bash

filename="${1%.*}"
workdir="splitted_by_games-$filename"
mkdir -p $workdir

split -l 20 $1 $workdir/chunk

echo "$1 splitted into $(ls $workdir | wc -l) files in $workdir/"

cat $(ls $workdir/chunk* | shuf -n 5000000) > $filename.sampled.pgn

echo "$filename.sampled.pgn has $($filename.sampled.pgn | wc -l) lines"
