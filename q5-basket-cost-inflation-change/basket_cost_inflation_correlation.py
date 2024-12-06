import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

filename1 = '../cpi_wage_data_with_inflation_country.csv'
filename2 = '../price_wage_data_country.csv'

def contains(string, target):
    if target not in string:
        return False
    return True

data = pd.read_csv(filename1, parse_dates=['date'])

# Adding a column to filter between food products
data['is_food'] = data['product'].map(lambda x: contains(x, 'Food'))
data = data[data['is_food'] == True]

# Adding a column for rate of inflation change
data['inflation_change'] = data['inflation_change'].astype(np.float64)

# Adding converting columns to floats
data['minimum_wage'] = data['minimum_wage'].astype(np.float64)
data['cpi'] = data['cpi'].astype(np.float64)

# Remove null values since there are some years without inflation change
data = data.dropna()

data2 = pd.read_csv(filename2, parse_dates=['date'])

# Get data for basket of goods
basket = pd.DataFrame([])
basket['date'] = data2['date']
basket['price'] = data2['price'] * 8 # basket for 1 month
basket = basket.groupby(by=['date']).agg(sum=('price', 'sum'))
basket = basket.iloc[:-(len(basket) - len(data))]

# Join tables
joint = pd.merge(data, basket, how='right', on='date')
joint = joint.dropna()
joint['percentage_salary'] = (joint['sum'])/(joint['minimum_wage'] * 160) * 100

# Divide into 4 categories to use chi2
high_percentage_of_salary_neg_inflation = joint[(joint['percentage_salary'] > 18.5) & (joint['inflation_change'] < 0)]
low_percentage_of_salary_neg_inflation = joint[(joint['percentage_salary'] <= 18.5) & (joint['inflation_change'] < 0)]
high_percentage_of_salary_pos_inflation = joint[(joint['percentage_salary'] > 18.5) & (joint['inflation_change'] >= 0)]
low_percentage_of_salary_pos_inflation = joint[(joint['percentage_salary'] <= 18.5) & (joint['inflation_change'] >= 0)]

# Print p-value
print('Chi2 p-value: ', stats.chi2_contingency([[len(high_percentage_of_salary_pos_inflation), len(low_percentage_of_salary_pos_inflation)], [len(low_percentage_of_salary_pos_inflation), len(low_percentage_of_salary_neg_inflation)]]).pvalue)
