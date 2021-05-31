#!/bin/bash

# previously:
# for f in lichess_db_standard_rated_2020*.pgn.eval.pgn; do head -4000000 $f > first_4M_$(basename $f); done

for input in first_4M_lichess_db_standard_rated_2020*.pgn.eval.pgn
do
    #input="first_4M_lichess_db_standard_rated_2020-03.pgn.eval.pgn"
    output=${input##*first_4M_}

    split -n4 $input
    # manually, fix the end and beginning of each file, so the pgn keeps a correct format:
    vim -p xaa xab xac xad
    mv xaa 0-1M_$output
    mv xab 1-2M_$output
    mv xac 2-3M_$output
    mv xad 3-4M_$output
done
