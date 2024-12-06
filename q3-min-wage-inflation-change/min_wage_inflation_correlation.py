import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

filename1 = '../cpi_wage_data_with_inflation_country.csv'

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

# Remove null values since there are some years without inflation change data
data = data.dropna()

# Calculate the linear regression
fit = stats.linregress(data['minimum_wage'].values, data['inflation_change'].values)
print(f"Correlation coefficient: {fit.rvalue}")

# Display plot with linear regression
plt.figure(1)
plt.plot(data['minimum_wage'].values, data['inflation_change'].values, 'b.', alpha=0.5)
plt.plot(data['minimum_wage'].values, fit.slope * data['minimum_wage'] + fit.intercept, 'r-', linewidth=3)
plt.title('National Inflation Rate vs National Minimum Wage')
plt.xlabel('Minimum Wage')
plt.ylabel('Inflation Rate')
plt.grid(True)
# plt.show()
plt.savefig('../plots/national_inflation_vs_minimum_wage.png', dpi=300, bbox_inches='tight')