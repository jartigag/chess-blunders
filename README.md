chess blunders
==============================

analyzing the most common chess blunders

## 2020

![](reports/figures/blunders_by_total_size_2020.png)

| ![](reports/figures/blunders_2020_in_board/1-g6.png) | ![](reports/figures/blunders_2020_in_board/2-Ng5.png) | ![](reports/figures/blunders_2020_in_board/3-Bc4.png) |
|------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| ![](reports/figures/blunders_2020_in_board/4-Nd4.png) | ![](reports/figures/blunders_2020_in_board/5-fxe5.png) | ![](reports/figures/blunders_2020_in_board/6-fxe5.png) |
| ![](reports/figures/blunders_2020_in_board/7-Nh3.png) | ![](reports/figures/blunders_2020_in_board/8-Nxe5.png) | ![](reports/figures/blunders_2020_in_board/9-Bf4.png) |

![](reports/figures/blunders_evolution_2020.png)

Project Organization
------------

```
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default MkDocs project; see mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
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
    ├── features       <- Scripts to turn raw data into features for modeling
    │   └── build_features.py
    │
    ├── models         <- Scripts to train models and then use trained models to make predictions
    │   ├── predict_model.py
    │   └── train_model.py
    │
    └── visualization  <- Scripts to create exploratory and results oriented visualizations
        └── visualize.py
```

### Installing development requirements
------------

    pip install -r requirements.txt

### Running the tests
------------

    py.test tests
