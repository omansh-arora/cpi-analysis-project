import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import sys

filename1 = sys.argv[1]

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

plt.figure(1)
plt.plot(data['minimum_wage'].values, data['inflation_change'].values, 'b.', alpha=0.5)
plt.plot(data['minimum_wage'].values, fit.slope * data['minimum_wage'] + fit.intercept, 'r-', linewidth=3)
plt.title('National Inflation Rate vs National Minimum Wage')
plt.xlabel('Minimum Wage')
plt.ylabel('Inflation Rate')

data.plot.hist(column=['residual'])
print(f"Residual normality test: {stats.normaltest(data['residual'].values).pvalue}")
plt.show()