#!/usr/bin/env python3
#
#usage: ./make_dataset.py ../../data/raw/ ../../data/interim/

import click
import logging
from pathlib import Path

import chess.pgn
#from src.features.build_features import process

def process_pgn(pgn_file):
    logger = logging.getLogger(__name__)
    logger.info(f"Preprocessing {pgn_file}")

    pgn = open(pgn_file)
    current_match = chess.pgn.read_game(pgn)

    while current_match:
        current_node = current_match
        if not current_node.variations: # eg: [Termination "Abandoned"], [Termination "Time forfeit"]
            current_match = chess.pgn.read_game(pgn)
            continue

        if '%eval' not in current_node.variations[0].comment:
            # There is no eval for this game, skip to next
            current_match = chess.pgn.read_game(pgn)
            continue

        # Game has an eval, loop through moves
        while not current_node.is_end():
            next_node = current_node.variations[0]
            if 4 in next_node.nags:
                # Check the nag set for each node for 4: the indicator for blunder
                match_identif = "({} vs. {}, {})".format(current_match.headers['White'],
                                                         current_match.headers['Black'],
                                                         current_match.headers['Date'])
                logger.debug(f"blunder in {match_identif}: {next_node.move}")
                fen = current_node.board().fen()
                move = current_node.board().san(next_node.move)
                #data[f'{fen},{move}'] = 1 if f'{fen},{move}' not in data else data[f'{fen},{move}']+1

            current_node = next_node

        current_match = chess.pgn.read_game(pgn)

    return None


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
    #TODO: make possible to iterate over input_path='a_file.pgn'
    for f in Path(input_path).glob('*.pgn'):
        result = process_pgn(f)

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
