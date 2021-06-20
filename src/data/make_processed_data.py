#!/usr/bin/env python3
#
#usage: ./make_processed_data.py ../../data/interim/ ../../data/processed/

import click
import logging
from pathlib import Path

import pandas as pd

from src.visualization.visualize_processed_data import *


def aggregate_data(blunders_df):
    """Get the final processed dataframes, aggregated by several variables of interest, to be visualized"""
    vc = blunders_df.value_counts(['Move', 'FEN'])
    return vc[vc>10] #TODO: reconsider this


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=True))
def main(input_path, output_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger()

    if Path(input_path).is_dir():
        normalized_input_path = f"{Path(input_path).resolve()}/"
        files = [f for f in Path(input_path).iterdir() if f.suffix=='.csv']
    else:
        normalized_input_path = f"{Path(input_path).resolve()}"
        files = [Path(input_path).iterdir()] if Path(input_path).suffix=='.csv' else None

    logger.warning('Making processed data set from interim data..')
    logger.warning(f"CSVs in input path {normalized_input_path} will be processed")

    for f in files:
        preprocessed_data = pd.read_csv(f)
        processed_data = aggregate_data(preprocessed_data)
        processed_output = f"{Path(output_path)/f.stem}.aggregated.csv"
        processed_data.to_csv(processed_output)
        logger.warning(f"Aggregated in {len(processed_data)} rows. Output in {processed_output}")

    logger.warning('Processed data set done.')

    #./src/visualization/visualize_processed_data.py
    #logger = logging.getLogger(".".join([make_visualizations.__module__, make_visualizations.__name__]))
    logger.warning('Making visualizations..')
    #TODO


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()
