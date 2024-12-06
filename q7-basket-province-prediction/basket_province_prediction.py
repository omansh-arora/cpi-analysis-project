import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

filename1 = '../cpi_wage_data_with_inflation_province.csv'
filename2 = '../price_wage_data_province.csv'

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
data = data.reset_index()

data2 = pd.read_csv(filename2, parse_dates=['date'])
data2 = data2[data2['province'] != 'Canada']

# Get data for basket of goods
basket = pd.DataFrame([])
basket['province'] = data2['province']
basket['date'] = data2['date']
basket['price'] = data2['price'] * 8 # basket for 1 month
basket = basket.groupby(by=['date', 'province']).agg(sum=('price', 'sum')).reset_index()
basket = basket.iloc[:-(len(basket) - len(data))]

# Join tables
joint = pd.merge(data, basket, how='right', on=['date', 'province'])
joint['percentage_salary'] = (joint['sum'])/(joint['minimum_wage'] * 160) * 100

# Prepare data
joint = joint.drop(columns=['product', 'date', 'index', 'is_food', 'Effective Date'])
joint = joint[(joint['cpi'].notna())]
joint = joint.groupby(by=['minimum_wage', 'province']).agg(mean_inflation_change=('inflation_change', 'mean'), mean_percentage_salary=('percentage_salary', 'mean'), mean_basket_cost=('sum', 'mean'), mean_cpi=('cpi', 'mean')).reset_index()

# Split data
X = joint.drop(columns=['province'])
y = joint['province'].values

# Get training/validation data
X_train, X_valid, y_train, y_valid = train_test_split(X, y)

# Model for predicting which province
model = RandomForestClassifier(n_estimators=150)
model.fit(X_train, y_train)
print('Province prediction model score: ', model.score(X_valid, y_valid))

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

for province, group in basket.groupby('province'):
    ax.plot(group['date'], group['sum'], marker='o', label=province)

ax.set_title("Basket cost by date for each province", fontsize=16)
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Basket cost", fontsize=14)
ax.legend(title="Province", fontsize=12)
ax.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
# plt.show()
plt.savefig('../plots/basket_cost_by_province.png', dpi=300, bbox_inches='tight')