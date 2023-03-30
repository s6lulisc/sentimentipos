# EPP Final Project: Sentiment Analysis Scores and IPO First Day Returns

## Authors

- Luke Liscio (University of Bonn, s6lulisc@uni-bonn.de)
- Leonardo Rota Sperti (University of Bonn, s6lerota@uni-bonn.de)

## About this project

The purpose of this repository is to conduct an empirical study using sentiment
analysis. The analysis is performed on US financial news articles related to companies
that had Initial Public Offerings in the year 2018. We investigate the relationship
between the polarity score of chosen companies and their first day returns. Polarity
score measures the sentiment of a text by assigning positive or negative values to words
and averaging those values to get an overall score. In this analysis, first day returns
is measured as the percentage change from opening price to closing price on the first
day of trading. This repo contains python scripts that handle the data management,
analsis, and production of a paper with the findings from this analysis.

The main objective of this project is to demonstrate and apply the skills learned in
"Effective Programming Practices for Economists".

## Requirements to run this project

In order to run this project on your local computer you need to have installed Python,
an Anaconda distribution, and a LaTex distribution in order to compile the documents.

The project was created on MacOS Ventura version 13.1. Here are the following programs
that were used during this project:

- Anaconda 23.1.0
- Python 3.11
- MacTeX-2023

Once the above programs are installed, you will need to download git-lfs. Follow
these[instructions to install git-lfs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).
I.e., for macOS users, type the following command in the terminal:

```console
$ brew install git-lfs
```

and then run this command:

```console
$ git install git-lfs
```

1. First clone this repository to your local machine by typing this command into your
   terminal

   ```console
   $ git clone https://github.com/s6lulisc/sentimentipos.git
   ```

1. All of the necessary python dependencies are located in environment.yml . To install
   the virtual environment in a terminal, navigate to the root folder of the repository
   and type

   ```console
   $ conda env create -f environment.yml
   ```

   And then activate it with

   ```console
   $ conda activate sentimentipos
   ```

1. To build the project, type

   ```console
   $ pytask
   ```

1. To run tests, type

   ```console
   $ pytest
   ```

## How to understand this repository

This repository was built using the
[Templates for Reproducible Research Projects in Economics](https://econ-project-templates.readthedocs.io/en/latest/index.html).

The `src` folder contains all the python scripts related to the execution of the
project.

- `data` contains the two original data sets used in this project.
- `data_management` contains 3 python scripts: `clean_data`, `data_processing`, and
  `task_data_management`. These scripts run the data processing and cleaning.
- `analysis` contains the python scripts `model.py` and `task_analysis` that run the
  sentiment analysis and regression.
- `final` contains python scripts related to plotting and creatinng the summary
  statistics table.

The `bld` folder contains all the outputs of the project.

- `data` contains 2 folders and 2 files: the `unzipped` folder of all the json files of
  financial news articles, the cleaned excel data called `ipo_data_clean.xlsx`, the
  folder `tokenized_texts` which contains csv files of all the text content from the
  json files matching for each IPO respectively, and `ipo_info.csv` which lists company
  name, date and returns for the IPOs that are chosen from the function `ipo_tickers` in
  the script `data_processing`.
- `figures` contains the plot from the regression.
- `models` contains the sentiment scroes of each IPO based on the textual analysis
  conducted on related financial news articles for each IPO.
- `tables` contains the summary statistics of the regression and stores it as a table.

In the root folder of the repository, there is also `sentimentipos.pdf` that is the
paper of the project that is compiled.

## Distribution of project responsibility

The responsibilities were split into two catorgories.

1. Collaborative effort:

- All code in `data_processing.py`, `clean_data.p`, `task_data_management.py`,
  `model.py`, `task_analysis.py`, `plot.py`

2. Individual:

**Author: Luke Liscio**

- the tests in `test_data_management.py` up until `test_filter_df_by_ipo_date`
- the tests in `test_model.py`
- `task_final.py`
- `sentimentipos.tex`
- `task_paper.py`
- `README.md`

**Author: Leonardo Rota Sperti**

- Tests in `test_data_management.py` from `test_filter_df_by_ipo_date`
- All docstrings

## Credits

This project was created with [cookiecutter](https://github.com/audreyr/cookiecutter)
and the
[econ-project-templates](https://github.com/OpenSourceEconomics/econ-project-templates).
