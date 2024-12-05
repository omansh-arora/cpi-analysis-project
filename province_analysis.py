import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
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
data['cpi'] = data['cpi'].astype(np.float64)

print(data)
data = data.dropna()
data = data.reset_index()

data2 = pd.read_csv(filename2, parse_dates=['date'])
data2 = data2[data2['province'] != 'Canada']
print(data2)
# print(data2[(data2['date'] == '2017-01-01']) & (data['province'] == 'Newfoundland and Labrador')])
# print(data2[data2['date'] == '2017-01-01'] and data['province'] == 'British Columbia')
basket = pd.DataFrame([])
basket['province'] = data2['province']
basket['date'] = data2['date']
basket['price'] = data2['price'] * 8 # basket for 1 month
basket = basket.groupby(by=['date', 'province']).agg(sum=('price', 'sum')).reset_index()
print('basket', basket)
basket = basket.iloc[:-(len(basket) - len(data))]

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
plt.show()

joint = pd.merge(data, basket, how='right', on=['date', 'province'])
# joint = joint.dropna()
joint['percentage_salary'] = (joint['sum'])/(joint['minimum_wage'] * 160) * 100



joint = joint.drop(columns=['product', 'date', 'index', 'is_food', 'Effective Date'])
joint = joint[(joint['cpi'].notna())]
joint = joint.groupby(by=['minimum_wage', 'province']).agg(mean_inflation_change=('inflation_change', 'mean'), mean_percentage_salary=('percentage_salary', 'mean'), mean_basket_cost=('sum', 'mean'), mean_cpi=('cpi', 'mean')).reset_index()
print('joint')
# print(joint)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
    # print(joint)
X = joint.drop(columns=['province'])
y = joint['province'].values
print('X')
print(X)
print('y')
print(y)

X_train, X_valid, y_train, y_valid = train_test_split(X, y)

model = RandomForestClassifier(n_estimators=150)
model.fit(X_train, y_train)

print(model.score(X_valid, y_valid))