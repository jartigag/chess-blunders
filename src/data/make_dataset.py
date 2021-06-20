#!/usr/bin/env python3
#
#usage: ./make_dataset.py ../../data/raw/ ../../data/interim/

import click
import logging
from pathlib import Path

import chess.pgn
import pandas as pd
import os, subprocess
import bz2
#from src.features.build_features import process

def preprocess_pgn(pgn_file):
    """Extract blunders (identified by Move-FEN), each one with player's Elo, game's time control and seconds spent in that move"""

    data = pd.DataFrame(columns=['Move', 'FEN', 'Turn', 'Elo', 'TimeControl', 'ElapsedSeconds'])
    data.set_index(['Move', 'FEN'], inplace=True)

    def convert_bytes(num):
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    size = convert_bytes(pgn_file.stat().st_size)
    if str(pgn_file).endswith("bz2"):
        try:
            ps = subprocess.Popen(('bzcat', pgn_file), stdout=subprocess.PIPE)
            output = subprocess.check_output(('wc','-l'), stdin=ps.stdout, timeout=5)
            ps.wait()
            numlines = int(output)
        except subprocess.TimeoutExpired:
            numlines = float('Inf')
    else:
        numlines = int(os.popen(f"wc -l {pgn_file}").read().split(  )[0])
    readlines = 0

    logger = logging.getLogger()
    logger.warning(f"Preprocessing {pgn_file} ({numlines} lines, {size})")

    actual_progress_bucket = 0
    progress_buckets = [x for x in range(0,100)]

    def print_progress(a):
        if a<len(progress_buckets):
            if readlines/numlines*100 >= progress_buckets[a]:
                logger.info(f"{readlines/numlines*100:.2f} % completed ({readlines} lines read, {len(data)} blunders extracted)")
                a+=1
        return a

    pgn = bz2.open(pgn_file, 'rt') if str(pgn_file).endswith("bz2") else open(pgn_file)
    current_match = chess.pgn.read_game(pgn)

    while current_match:
        current_node = current_match
        if not current_node.variations: # eg: [Termination "Abandoned"], [Termination "Time forfeit"]
            readlines += len(current_match.headers) + 3 # headers + movetext + 2 blank lines
            current_match = chess.pgn.read_game(pgn)
            continue

        if '%eval' not in current_node.variations[0].comment:
            # There is no eval for this game, skip to next
            readlines += len(current_match.headers) + 3 # headers + movetext + 2 blank lines
            current_match = chess.pgn.read_game(pgn)
            continue

        # Game has an eval, loop through moves
        while not current_node.is_end():
            next_node = current_node.variations[0] # next move
            turn = current_node.board().fullmove_number
            if turn>15: break
            if 4 in next_node.nags: #  Annotation Glyphs or NAGs are used to annotate chess games when using a computer
                #                      NAG_BLUNDER = 4 """A blunder. Can also be indicated by ``??`` in PGN notation."""
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
                    {'Elo': elo, 'TimeControl': timecontrol, 'ElapsedSeconds': secs, 'Turn': turn},
                        name=(move, fen)
                    ))

            current_node = next_node

        readlines += len(current_match.headers) + 3 # headers + movetext + 2 blank lines
        try:
            current_match = chess.pgn.read_game(pgn)
        except Exception as e:
            print(e)
            readlines += len(current_match.headers) + 3 # headers + movetext + 2 blank lines
            continue
        actual_progress_bucket = print_progress(actual_progress_bucket)

    print_progress(-1)
    return data


def aggregate_data(blunders_df):
    """Get the final processed dataframes, aggregated by several variables of interest, to be visualized"""
    vc = blunders_df.value_counts(['Move', 'FEN'])
    return vc[vc>10] #TODO: reconsider this


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=True))
@click.option('--from_interim_files', is_flag=True)
def main(input_path, output_path, from_interim_files):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger()

    if Path(input_path).is_dir():
        normalized_input_path = f"{Path(input_path).resolve()}/"
        if not from_interim_files:
            files = [f for f in Path(input_path).iterdir() if '.pgn' in f.name and f.suffix in ['.pgn','.bz2']]
        else:
            files = [f for f in Path(input_path).iterdir() if f.suffix=='.csv']
    else:
        normalized_input_path = f"{Path(input_path).resolve()}"
        if not from_interim_files:
            files = [Path(input_path) if Path(input_path).suffix in ['.pgn','.pgn.bz2'] else input_path]
        else:
            files = [f for f in Path(input_path).iterdir() if f.suffix=='.csv']

    if not from_interim_files:
        logger.warning('Making interim data set from raw data..')
        logger.warning(f"PGNs in input path {normalized_input_path} will be preprocessed")
    else:
        logger.warning('Making final data set from interim data..')
        logger.warning(f"PGNs in input path {normalized_input_path} will be processed")

    for f in files:
        if isinstance(f,Path):

            if not from_interim_files:
                preprocessed_data = preprocess_pgn(f)
                preprocessed_output = f"{Path(output_path)/f.stem}.blunders.csv" # f.stem is f.name without suffix
                preprocessed_data.to_csv(preprocessed_output)
                logger.warning(f"{len(preprocessed_data)} blunders extracted. Output in {preprocessed_output}")
            else:
                preprocessed_data = pd.read_csv(f)
                processed_data = aggregate_data(preprocessed_data)
                processed_output = f"{Path(output_path)/f.stem}.aggregated.csv"
                processed_data.to_csv(processed_output)
                logger.warning(f"Aggregated in {len(processed_data)} rows. Output in {processed_output}")

        else:
            logger.warning(f"{f} suffix is invalid (must be .pgn or .pgn.bz2). Skipping to next file..")

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

# $ for f in data/interim; do echo $f; awk -F, '{print $1","$2","$3}' $f | sort -rn | uniq -c | sort -rnt"," | head | column -nts","; echo; done
# 0-1M_lichess_db_standard_rated_2021-04.eval.blunders.csv
#      31 Nd4   r1bqkbnr/pppp1ppp/2n5/3Pp3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3        3
#      27 g6    rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2         2
#      22 Bc4   rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2          2
#      19 Ng5   r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4   4
#      16 Nd4   rnbqkbnr/ppp1pppp/8/8/4p3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3          3
#      15 dxe7  rnbqk2r/ppp1nppp/3P4/2b5/8/5N2/PPP1PPPP/RNBQKB1R w KQkq - 1 5         5
#      15 Bg4   rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2            2
#      15 Bf4   rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2          2
#      13 fxe5  rnbqkbnr/pppp2pp/5p2/4P3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3          3
#      12 Nh3   r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4  4
#
# 1-2M_lichess_db_standard_rated_2021-04.eval.blunders.csv
#      27 g6    rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2        2
#      26 Nd4   r1bqkbnr/pppp1ppp/2n5/3Pp3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3       3
#      22 Ng5   r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4  4
#      16 Bc4   rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2         2
#      15 dxe7  rnbqk2r/ppp1nppp/3P4/2b5/8/5N2/PPP1PPPP/RNBQKB1R w KQkq - 1 5        5
#      14 Nxf7  r1b1kbnr/pppp1ppp/8/4N1q1/2BnP3/8/PPPP1PPP/RNBQK2R w KQkq - 1 5      5
#      13 O-O   r1bqk2r/ppp2ppp/2p5/2b5/2B1P1n1/2N5/PPPP1PPP/R1BQK2R w KQkq - 4 7    7
#      13 Nxe5  r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3     3
#      13 Nd4   rnbqkbnr/ppp1pppp/8/8/4p3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3         3
#      12 fxe5  rnbqkbnr/pppp2pp/5p2/4P3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3         3
#
# 2-3M_lichess_db_standard_rated_2021-04.eval.blunders.csv
#      30 Nd4   r1bqkbnr/pppp1ppp/2n5/3Pp3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3        3
#      24 Ng5   r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4   4
#      24 g6    rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2         2
#      18 Bc4   rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2          2
#      14 O-O   r1bqk2r/ppp2ppp/2p5/2b5/2B1P1n1/2N5/PPPP1PPP/R1BQK2R w KQkq - 4 7     7
#      14 g4    r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4  4
#      13 Nxf7  r1b1kbnr/pppp1ppp/8/4N1q1/2BnP3/8/PPPP1PPP/RNBQK2R w KQkq - 1 5       5
#      12 fxe5  rnbqkbnr/ppp2ppp/3p4/4p3/4PP2/8/PPPP2PP/RNBQKBNR w KQkq - 0 3         3
#      12 fxe5  r1bqkbnr/pppp1ppp/2n5/4p3/4PP2/8/PPPP2PP/RNBQKBNR w KQkq - 1 3        3
#      11 Nxe5  r1bqkbnr/pppp1ppp/2n5/4P3/4P3/8/PPPP2PP/RNBQKBNR b KQkq - 0 3         3
#
# 3-4M_lichess_db_standard_rated_2021-04.eval.blunders.csv
#      28 g6     rnbqkbnr/pppp1ppp/8/4p2Q/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2         2
#      23 Nd4    r1bqkbnr/pppp1ppp/2n5/3Pp3/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3        3
#      21 Ng5    r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4   4
#      16 Bc4    rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2          2
#      13 O-O    r1bqk2r/ppp2ppp/2p5/2b5/2B1P1n1/2N5/PPPP1PPP/R1BQK2R w KQkq - 4 7     7
#      13 Nd4    rnbqkbnr/ppp1pppp/8/8/4p3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3          3
#      11 g4     r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4  4
#      11 dxe7   rnbqk2r/ppp1nppp/3P4/2b5/8/5N2/PPP1PPPP/RNBQKB1R w KQkq - 1 5         5
#      10 cxb5   rnbqkbnr/p3pppp/2p5/1P6/2pP4/4P3/1P3PPP/RNBQKBNR b KQkq - 0 5         5
#      10 Bxf7+  r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4     4
