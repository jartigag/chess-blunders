chess blunders
==============================

analyzing the most common chess blunders

## - Download and filter only evaluated games

[![asciicast](https://asciinema.org/a/421249.svg)](https://asciinema.org/a/421249)

#### All data (only the first 4M evaluated games for each month in 2020 and 2021 has been processed, but that's enough):

[![](https://files.mastodon.social/media_attachments/files/106/364/592/647/904/077/original/409a5f27f47aa91b.png)](https://mastodon.social/@jartigag/106364603081282594)

## - Preprocess: get blunders (parallelizing 1M per core)

[![](https://files.mastodon.social/media_attachments/files/106/325/214/686/169/487/original/c5d7d06fd10299a1.png)](https://mastodon.social/@jartigag/106325214993618150)

#### Resulting interim data

[![asciicast](https://asciinema.org/a/414643.svg)](https://asciinema.org/a/414643)

## - Aggregate and visualize most common blunders

![](reports/figures/blunders_by_total_size_2020.png)

| ![](reports/figures/blunders_2020_in_board/1-g6.png) | ![](reports/figures/blunders_2020_in_board/2-Ng5.png) | ![](reports/figures/blunders_2020_in_board/3-Bc4.png) |
|------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| ![](reports/figures/blunders_2020_in_board/4-Nd4.png) | ![](reports/figures/blunders_2020_in_board/5-fxe5.png) | ![](reports/figures/blunders_2020_in_board/6-fxe5.png) |
| ![](reports/figures/blunders_2020_in_board/7-Nh3.png) | ![](reports/figures/blunders_2020_in_board/8-Nxe5.png) | ![](reports/figures/blunders_2020_in_board/9-Bf4.png) |

![](reports/figures/blunders_evolution_2020.png)

Project Organization
------------

Derived from the [Cookiecutter Data Science project](https://github.com/jartigag/cookiecutter-data-science)

```
├── Makefile           <- Makefile with commands like `make data` or `make create_environment`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default MkDocs project; see mkdocs.org for details
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.py           <- Make this project pip installable with `pip install -e`
└── src                <- Source code for use in this project.
    ├── data           <- Scripts to download or generate data
    │   └── make_dataset.py
    │
    └── visualization  <- Scripts to create exploratory and results oriented visualizations
        └── visualize.py
```
