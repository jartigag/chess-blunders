#!/bin/sh

# time ./load_table.sql
# real    0m41,901s
#
# chess=> select count(*) from blunders;
#   count
# ---------
#  9661219
# (1 fila)


postgres_db="chess"
interim_data_path="$PWD/data/interim/"

psql $postgres_db -c "create table if not exists blunders (Id serial,Month date,Move text,FEN text,Turn integer,Elo integer,TimeControl text,ElapsedSeconds float);"

for month in $(seq -f "%02g" 12)
do
    psql $postgres_db -c "alter table blunders alter column month set default '2020-"$month"-01';"
    psql $postgres_db -c "copy blunders(Move,FEN,Turn,Elo,TimeControl,ElapsedSeconds) from program 'grep -hv Turn "$interim_data_path"*lichess_db_standard_rated_2020-"$month".pgn.eval.blunders.csv' csv;"
done
psql $postgres_db -c "alter table blunders alter column month drop default;"
