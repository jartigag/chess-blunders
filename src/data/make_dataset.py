#!/usr/bin/env python3
#
#usage: ./make_dataset.py ../../data/raw/database.sqlite ../../data/processed/matches.csv

"""
original author: Antiochian, 2020-10-18

1408484768 lines in main file (140GB, yikes!)

Flow:
    - Step thru file line by line
    Check if first move of new game (if starts with "1. ")
    - Compare current eval to previous eval for both sides for all moves
    log eval change, if eval change exceeds a cutoff (-2?) then mark as a blunder
    and note down time at which move occurred
    - Graph data

Data structure:
    Each game should yield two 2XN arrays
    [time, evalchange] - white
    [time, evalchange] - black

Intermediate datafiles are exported and saved with the following filename structure:

 "data/1603074502 time180-180_rating2000-4000_raw.txt"
      timestamp     gametime    rating        filetype

Each run produces 4 similarly named files:
    ..._raw.txt - all raw blunder times as newline-delineated list
    ..._norm.txt - frequency dict of all move times (needed to normalize data) serialised as dictionary
    ..._info.txt - misc info about when the file was generated, how long it took, etc etc
    ..._graph.png - graph of data

Later new graphs/analysis can be built directly from these files without having to endure
the tedius process of stepping through the 140GB raw game datafile again.
"""

import click
import logging
from pathlib import Path
#from src.features.build_features import process
#from src.visualization.visualize import make_visualizations

import sys
import time


def preprocess_PGN(inp, output_filepath, maxlim, blunder_cutoff, min_elo, max_elo, min_time, max_time):

    id_string = f"time{min_time}-{max_time}_rating{min_elo}-{max_elo}"
    output_filepath = Path(output_filepath).resolve()

    start = int(time.time())
    logger = logging.getLogger(__name__)
    logger.info(f"Preprocessing {inp} to {output_filepath}/{start}_{id_string}..")

    if not maxlim:
        maxlim = float("Inf")
    linecount = 0
    validcount = 0
    curr_elo = -1
    normalization = {}
    finished = False

    out     = output_filepath / f"{start}_{id_string}_raw.txt"
    normout = output_filepath / f"{start}_{id_string}_norm.txt"
    infoout = output_filepath / f"{start}_{id_string}_info.txt"

    def time_to_int(timestring):
        """takes in timestamp of format "00:00:00" etc and converts to seconds int"""
        timeint = 0 #number of seconds
        t = timestring.split(":")
        t.reverse()
        mult = 1
        for i in t:
            timeint += mult*int(i)
            mult *= 60
        return timeint

    def strip_game(line, time_cutoff_min,time_cutoff_max):
        """
        This function removes all metadata and move information from game, leaving only something that looks like:
            [[eval, time], [eval, time], [eval,time],...]
        """
        if time_cutoff_max == None:
            time_cutoff_max = float("Inf")
        game = line.split("}")[:-1] #gets
        stripped = []
        if game and ("%eval" in game[0]) and ("%clk" in game[0]):
            #valid game
            for line in game:
                res = []
                curr = ""
                read = False
                for char in line:
                    if char == "[":
                        read = True
                    elif char == "]":
                        res.append(curr.split()[1])
                        curr = ""
                        read = False
                    elif read:
                        curr += char
                if len(res) == 2:
                    stripped.append(res)
            #final check in case of checkmate (no eval is given)
        if stripped:
            if (time_to_int(stripped[0][1]) >= time_cutoff_min) and (time_to_int(stripped[0][1]) <= time_cutoff_max):
                return stripped
        else:
            return False

    def extract_blunders(stripped,normalization, cutoff = -2, extremis = 100):
        #cutoff = change in eval to count as a blunder
        #extremis: point at which blunders are no longer recognised
        curr_eval = 0.0
        white = True
        blunder_times = []
        all_times = []
        for move in stripped:
            move[1] = time_to_int(move[1])
            all_times.append(move[1])
            prev_eval = curr_eval
            if move[0][0] == "#":
                if move[0][1] == "-":
                    curr_eval = -extremis
                else:
                    curr_eval = extremis
            else:
                curr_eval = float(move[0])
            if white:
                white = False
                eval_change = curr_eval - prev_eval
                if eval_change < cutoff and curr_eval < extremis:
                    blunder_times.append(move[1])
            else:
                white = True
                eval_change = prev_eval - curr_eval
                if eval_change < cutoff and curr_eval > -extremis:
                    blunder_times.append(move[1])
        for t in all_times:
            if t in normalization:
                normalization[t] += 1
            else:
                normalization[t] = 1
        return blunder_times, normalization

    with open(inp, "r") as infile:
        with open(out, "w") as outfile:
            for line in infile:
                if linecount > maxlim:
                    break
                    #return normalization
                if line[:9] == "[WhiteElo":
                    curr_elo = int(line.split()[1][1:-2])
                if (curr_elo < max_elo) and (curr_elo >= min_elo) and (line[:3] == "1. "):
                    #reset for new game!
                    stripped = strip_game(line, min_time, max_time)
                    if stripped:
                        validcount +=1
                        blunder_times, normalization = extract_blunders(stripped, normalization)
                        for t in blunder_times:
                            outfile.write(str(t)+"\n")
                linecount += 1
    time_taken = time.time() - start
    logger.info(f"Finished creating {out} after {linecount} lines processed. ({validcount} matching games found)")
    with open(normout, "w") as outfile:
        print(normalization, file=outfile)
    with open(infoout, "w") as outfile:
        print("Created", out, "\n", linecount, " lines processed. (", validcount, " matching games found)", file=outfile)
        print(f" {round(time_taken, 3)} seconds taken.", file=outfile)
        print("\nParameters used:", file=outfile)
        print("\n Blunder cutoff: ", blunder_cutoff, "\n Min Elo: ", min_elo, "\n Max Elo: ", max_elo, "\n Min time:", min_time, "\n Max time:", max_time, file=outfile)

    sys.exit()
    return normalization, out


def get_raw(blunderfile="blunders.txt"):
    raw = {}
    with open(blunderfile) as infile:
        for line in infile:
            key = line.replace("\n", "")
            if int(key) in raw:
                raw[int(key)] += 1
            else:
                raw[int(key)] = 1
        return raw


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=True))
def main(input_path, output_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Making final data set from raw data..')

    normalized_input_path = f"{Path(input_path).resolve()}/" if Path(input_path).is_dir() else f"{Path(input_path).resolve()}"
    logger.info(f"PGNs in input path {normalized_input_path} will be preprocessed")
    for f in Path(input_path).glob('*.pgn'):
        norm, outfile = preprocess_PGN(f, output_path, maxlim=2**20, blunder_cutoff=-2, min_elo=0, max_elo=5000, min_time=300, max_time=300)
        total = 0
        for k in norm:
            total += norm[k]
        print("Total blunders: ", total)
        # plot_histogram_from_blunderfile()
        print("Extracting and plotting data...")
        raw = get_raw(outfile)
        xdata, ydata = plot_histogram(raw, norm, max_time)
        print("Data processed.")

    #./src/features/build_features.py
    #logger = logging.getLogger(".".join([process.__module__, process.__name__]))
    logger.info('Building features..')
    #TODO

    #./src/visualization/visualize.py
    #logger = logging.getLogger(".".join([make_visualizations.__module__, make_visualizations.__name__]))
    logger.info('making visualizations..')
    #TODO

    logger.info('final data set done.')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()
