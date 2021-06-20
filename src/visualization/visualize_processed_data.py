#!/usr/bin/env python3
#
#usage: ./visualize_processed_data.py ../../data/processed/ ../../reports/figures/

import click
import logging
from pathlib import Path

import pandas as pd
import chess


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=True))
def main(input_path, output_path):
    """
    """
    logger = logging.getLogger()

    if Path(input_path).is_dir():
        normalized_input_path = f"{Path(input_path).resolve()}/"
        files = [f for f in Path(input_path).iterdir() if f.suffix=='.csv']
    else:
        normalized_input_path = f"{Path(input_path).resolve()}"
        files = [f for f in Path(input_path).iterdir() if f.suffix=='.csv']

    logger.warning('Making visualizations..')
    logger.warning(f"Graphs will be generated from CSVs in input path {normalized_input_path}")

    for f in files:
        print_boards()

    logger.warning('Visualizations done.')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()
