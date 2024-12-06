# CMPT 353: Final Project

## Description
Relationship between minimum wage trends and the cost of food in Canada

## Table of Contents
- [Libraries](#libraries)

- [Installation](#installation)

- [Usage](#usage)

## Libraries

A list of the libraries that were used for this project includes:

- subprocess
- os
- numpy
- pandas
- matplotlib
- sklearn
- scipy 
- statsmodels

Note: Python3 is used for this

## Installation

### 1. Clone the repository

git clone

### 2. Install require libraries

pip install numpy pandas matplotlib scikit-learn scipy statsmodels

## Usage

### Running the code

#### 1. Navigate to project directory

cd cpi-analysis-project

#### 2. Execute Python script

python3 main.py

### Order of Execution

1. Preprocesing script to generate data for Canada
2. Preprocessing script to generate data for Provinces
3. Script to generate analysis of CPI vs minimum wage
4. Script to generate analysis of CPI and minimum wage gap
5. Script to generate analysis of minimum wage vs rate of inflation change
6. Script to generate analysis of inflation adjust cost of groceries
7. Script to generate analysis of thecost of a basket of goods as rate of inflation changes
8. Script to generate analysis of number of minimum wage hours to purchase a basket of goods
9. Script to generate analysis of future prices of a basket of goods

### Files produced

- cpi_wage_data_with_inflation_country.csv
- price_wage_data_country.csv
- price_wage_data_province.csv
- cpi_wage_data_with_inflation_province.csv
- plots/basket_cost_by_province.png
- plots/minimum_wage_vs_cpi.png
- plots/minimum_wage_vs_mean_basket_cost.png
- plots/minimum_wage_vs_real_grocery_prices.png
- plots/national_inflation_vs_minimum_wage.png
- plots/tukey.png