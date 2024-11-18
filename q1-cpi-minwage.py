# Takes the average Minimum wage using all provinces, for each year, in December
# Takes the average CPI on food using all provinces, for each year, in December


import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

file_path = 'cpi_wage_data_with_inflation.csv'
data = pd.read_csv(file_path)

# filter data for the "Food" product
food_data = data[data['product'] == 'Food 5'].copy()

# extract the year and month from the date column
food_data.loc[:, 'year'] = pd.to_datetime(food_data['date']).dt.year
food_data.loc[:, 'month'] = pd.to_datetime(food_data['date']).dt.month

# filter for December entries only
december_data = food_data[food_data['month'] == 12]

# annual averages for minimum wage and CPI
annual_summary = december_data.groupby('year').agg(
    average_minimum_wage=('minimum_wage', 'mean'),
    average_cpi_food=('cpi', 'mean')
).reset_index()

# data for Linear Regression
X = annual_summary['average_minimum_wage'].values.reshape(-1, 1)
y = annual_summary['average_cpi_food'].values

# linear Regression
model = LinearRegression()
model.fit(X, y)

# regression line
slope = model.coef_[0]
intercept = model.intercept_
regression_line = model.predict(X)

plt.figure(figsize=(10, 6))
plt.scatter(annual_summary['average_minimum_wage'], annual_summary['average_cpi_food'], color='blue', label='Data Points')
plt.plot(annual_summary['average_minimum_wage'], regression_line, color='red', label='Regression Line')
plt.title('Minimum Wage vs CPI for Food (Canada, Annual Averages)')
plt.xlabel('Average Minimum Wage (December)')
plt.ylabel('Average CPI for Food (December)')
plt.legend()
plt.grid()
plt.show()
