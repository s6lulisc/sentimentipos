# EPP Final Project: Sentiment Analysis Scores and IPO First Day Returns

## Authors

- Luke Liscio (University of Bonn, s6lulisc@uni-bonn.de)
- Leonardo Rota Sperti (University of Bonn, s6lerota@uni-bonn.de)

## About this project

The purpose of this repository is to conduct an empirical study of sentiment analysis on
US financial news articles related to IPOs in the year 2018. We then look at the
relationship between the polarity score of each of the IPOs under investigation and
their first day returns respectively. In this analysis, first day returns is measured as
the percentage change from opening price to closing price on the first day of trading.
This repo contains python scripts that handle the data management, analsis, and
production of a paper with the findings from this analysis.

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

1. Once the above programs are installed, first clone this repository to your local
   machine.

1. In order to run this project you will need to download this
   [zipped data set file from Kaggle](https://www.kaggle.com/datasets/jeet2016/us-financial-news-articles).
   When saving the file to your local machine, make sure to save it to the correct path.
   The zipped file needs to be saved in src/sentimentipos/data.

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
project, such as the data management, analysis, plotting, and the tasks.

- `data` contains the two data sets used in this project
- `data_management` contains python scripts that run data processing/cleaning
- `analysis` contains the python script model.py that runs the sentiment analysis and
  regression
- `final` contains python scripts related to plotting and creatinng the summary
  statistics table

The `bld` folder contains all the outputs of the project

- `data` contains the folder of the unzipped json files, matching json files related to
  the IPOs in the analysis, and the tokenized texts which contain the content from the
  json files relevant to each IPO.
- `figures` contains the plot from the regression
- `models` contains the sentiment scroes of each IPO based on the textual analysis
  conducted on related financial news articles to each IPO
- `tables` contains the output of the regression and stores it as a table

## Distribution of project responsibility

The breakdown of responibilites were split into two catorgories.

1. Joint effert

- All code in `clean_data`, `task_data_management`, `model`, `task_analysis`, `plot`

2. Individual

**Author: Luke Liscio**

- the tests for functions in `clean_data` up until `transpose_all_dataframes`
- the tests in `test_model`
- `task_final`
- `paper/sentimentipos.tex` and `paper/task_paper`
- `ReadMe`

**Author: Leonardo Rota Sperti**

- Tests in `clean_data` from `transpose_all_dataframes`
- All docstrings

## Credits

This project was created with [cookiecutter](https://github.com/audreyr/cookiecutter)
and the
[econ-project-templates](https://github.com/OpenSourceEconomics/econ-project-templates).
