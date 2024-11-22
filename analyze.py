import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import sys

filename1 = sys.argv[1]
filename2 = sys.argv[2]

def contains(string, target):
    if target not in string:
        return False
    return True

data = pd.read_csv(filename1, parse_dates=['date'])
data['is_food'] = data['product'].map(lambda x: contains(x, 'Food'))
data = data[data['is_food'] == True]
data['inflation_change'] = data['inflation_change'].astype(np.float64)
data['minimum_wage'] = data['minimum_wage'].astype(np.float64)
data = data.dropna()

fit = stats.linregress(data['minimum_wage'].values, data['inflation_change'].values)
print(f"Correlation coefficient: {fit.rvalue}")

data['residual'] = data['inflation_change'] - (data['minimum_wage'] * fit.slope + fit.intercept)
data = data.reset_index()
print(data)

plt.figure(1)
plt.plot(data['minimum_wage'].values, data['inflation_change'].values, 'b.', alpha=0.5)
plt.plot(data['minimum_wage'].values, fit.slope * data['minimum_wage'] + fit.intercept, 'r-', linewidth=3)
plt.title('National Inflation Rate vs National Minimum Wage')
plt.xlabel('Minimum Wage')
plt.ylabel('Inflation Rate')

data.plot.hist(column=['residual'])
print(f"Residual normality test: {stats.normaltest(data['residual'].values).pvalue}")
# plt.show()

data2 = pd.read_csv(filename2, parse_dates=['date'])
basket = pd.DataFrame([])
basket['date'] = data2['date']
basket['price'] = data2['price'] * 8 # basket for 1 month
basket = basket.groupby(by=['date']).agg(sum=('price', 'sum'))
basket = basket.iloc[:-(len(basket) - len(data))]



joint = pd.merge(data, basket, how='right', on='date')
joint = joint.dropna()
joint['percentage_salary'] = (joint['sum'])/(joint['minimum_wage'] * 160) * 100

high_percentage_of_salary_neg_inflation = joint[(joint['percentage_salary'] > 18.5) & (joint['inflation_change'] < 0)]
low_percentage_of_salary_neg_inflation = joint[(joint['percentage_salary'] <= 18.5) & (joint['inflation_change'] < 0)]
high_percentage_of_salary_pos_inflation = joint[(joint['percentage_salary'] > 18.5) & (joint['inflation_change'] >= 0)]
low_percentage_of_salary_pos_inflation = joint[(joint['percentage_salary'] <= 18.5) & (joint['inflation_change'] >= 0)]

print(stats.chi2_contingency([[len(high_percentage_of_salary_pos_inflation), len(low_percentage_of_salary_pos_inflation)], [len(low_percentage_of_salary_pos_inflation), len(low_percentage_of_salary_neg_inflation)]]).pvalue)

