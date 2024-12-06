import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

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

# Prepare data to split
joint = joint.drop(columns=['product', 'date', 'is_food'])
joint = joint.groupby('minimum_wage').agg(mean_inflation_change=('inflation_change', 'mean'), mean_percentage_salary=('percentage_salary', 'mean'), mean_basket_cost=('sum', 'mean'), mean_cpi=('cpi', 'mean')).reset_index()

# Prepare to get training/validation data
X = joint.drop(columns=['mean_basket_cost'])
y = joint['mean_basket_cost'].values

# Get training data and validation data
X_train, X_valid, y_train, y_valid = train_test_split(X, y)

# Model to predict basket cost
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
print('Basket cost model score: ', model.score(X_valid, y_valid))
input = pd.DataFrame([[15.204667, -2.92, 16.268689, 184.890000]], columns=X.columns)
print('Predicted basket cost: ', model.predict(input))

# Prepare to get training/validation data
X = joint.drop(columns=['minimum_wage'])
y = joint['minimum_wage'].values

# Get training data and validation data
X_train, X_valid, y_train, y_valid = train_test_split(X, y)

# Model to predict minimum wage
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
print('Minimum wage model score: ', model.score(X_valid, y_valid))
input = pd.DataFrame([[-2.92, 16.268689, 395.776000, 184.890000]], columns=X.columns)
print('Predicted minimum wage: ', model.predict(input))

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(joint['minimum_wage'], joint['mean_basket_cost'], color='purple', alpha=0.7)
plt.title('Minimum Wage vs Mean Basket Cost')
plt.xlabel('Minimum Wage')
plt.ylabel('Mean Basket Cost')
plt.grid(True)
# plt.show()
plt.savefig('../plots/minimum_wage_vs_mean_basket_cost.png', dpi=300, bbox_inches='tight')
