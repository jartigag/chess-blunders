#!/usr/bin/env python3
#
#usage: ./make_dataset.py ../../data/raw/ ../../data/interim/

import click
import logging
from pathlib import Path

import chess.pgn
import pandas as pd
import os
#from src.features.build_features import process

def preprocess_pgn(pgn_file):
    logger = logging.getLogger()
    logger.warning(f"Preprocessing {pgn_file}")

    data = pd.DataFrame(columns=['Move', 'FEN', 'Elo', 'TimeControl', 'SecondsInThisMove'])
    data.set_index(['Move', 'FEN'], inplace=True)

    numlines = int(os.popen(f"wc -l {pgn_file}").read().split(  )[0])
    readlines = 0

    def print_progress():
        readlines += len(current_match.headers) + 3 # headers + movetext + 2 blank lines
        if float(f"{readlines/numlines*100:.2f}")%5==0: # 5%, 10%, 15%..
            logger.info(f"{readlines/numlines*100:.2f} % completed ({readlines} lines read, {len(data)} blunders extracted)")

    pgn = open(pgn_file)
    current_match = chess.pgn.read_game(pgn)

    while current_match:
        current_node = current_match
        if not current_node.variations: # eg: [Termination "Abandoned"], [Termination "Time forfeit"]
            print_progress()
            current_match = chess.pgn.read_game(pgn)
            continue

        if '%eval' not in current_node.variations[0].comment:
            # There is no eval for this game, skip to next
            print_progress()
            current_match = chess.pgn.read_game(pgn)
            continue

        # Game has an eval, loop through moves
        while not current_node.is_end():
            next_node = current_node.variations[0] # next movement
            if 4 in next_node.nags:
                # Check the nag set for each node for 4: the indicator for blunder
                match_identif = "({} vs. {}, {})".format(current_match.headers['White'],
                                                         current_match.headers['Black'],
                                                         current_match.headers['Date'])
                logger.debug(f"blunder in {match_identif}: {next_node.move}")
                fen = current_node.board().fen()
                move = current_node.board().san(next_node.move)
                if current_node.board().turn==chess.WHITE:
                    elo = current_match.headers['WhiteElo']
                else:
                    elo = current_match.headers['BlackElo']
                timecontrol = current_match.headers['TimeControl']
                secs = current_node.clock()
                data = data.append(pd.Series(
                        {'Elo': elo, 'TimeControl': timecontrol, 'SecondsInThisMove': secs},
                        name=(move, fen)
                    ))

            current_node = next_node

        current_match = chess.pgn.read_game(pgn)
        print_progress()

    print_progress()
    return data


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=True))
def main(input_path, output_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger()
    logger.warning('Making final data set from raw data..')

    normalized_input_path = f"{Path(input_path).resolve()}/" if Path(input_path).is_dir() else f"{Path(input_path).resolve()}"
    logger.warning(f"PGNs in input path {normalized_input_path} will be preprocessed")
    #TODO: make possible to iterate over input_path='a_file.pgn'
    for f in Path(input_path).glob('*.pgn'):
        data = preprocess_pgn(f)
        preprocess_output = f"{Path(output_path)/f.stem}.blunders.csv" # f.stem is f.name without suffix
        data.to_csv(preprocess_output)
        logger.warning(f"Preprocess output in {preprocess_output}")


    #./src/features/build_features.py
    #logger = logging.getLogger(".".join([process.__module__, process.__name__]))
    logger.warning('Building features..')
    #TODO

    #./src/visualization/visualize.py
    #logger = logging.getLogger(".".join([make_visualizations.__module__, make_visualizations.__name__]))
    logger.warning('making visualizations..')
    #TODO

    logger.warning('final data set done.')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()

# $ tail +2 data/interim/lichess_db_standard_rated_2021-04.1Mlines.blunders.csv | sort -nk1,2 -t, | awk '{print $1,$2}' | uniq -c | sort -nr | column -ts, | head
#       5 Nd4     r1bqkbnr/pppp1ppp/2n5/3Pp3/4P3/8/PPP2PPP/RNBQKBNR b
#       5 Bc4     rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w
#       3 Rb3+    5b2/4ppp1/1k6/p4q2/3r1Br1/P1R5/1PP5/1K3R2 w
#       3 Nf6     rnb1k2r/pp1pq1pp/3b4/2pnN3/4QB2/8/PPP2PPP/RN2KB1R b
#       3 Kb6     5b2/4ppp1/2k5/p4q2/3r1Br1/P1R5/1PP5/1K3R2 b
#       2 Rh7     8/4R3/p2p1k2/2p1bNp1/2P3P1/1P3p1P/r7/6K1 w
#       2 Rh2+    4k3/4B1PK/4pP2/3p4/8/4PP2/2p3r1/8 b
#       2 Rfe2+   4n1k1/5pp1/1P5p/N7/1R6/5P1P/2r2r2/R3K3 b
#       2 Re2+    4n1k1/5pp1/1P5p/N7/1R6/5P1P/2rr4/R3K3 b
#       2 Qh4+    rnb4r/pp6/7p/7Q/1k6/2q5/P2R1PPP/4K2R w
#
# $ grep " 3... Nd4??" lichess_db_standard_rated_2021-04.1Mlines.pgn --color | wc -l
# 5
