import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

inflation_file_path = "../raw_data/inflation.csv"
wages_file_path = "../raw_data/wages.csv"
grocery_prices_24_file_path = "../raw_data/price-to-24.csv"
grocery_prices_17_file_path = "../raw_data/price-to-17.csv"

inflation_data = pd.read_csv(inflation_file_path)
wages_data = pd.read_csv(wages_file_path)
grocery_prices_24_data = pd.read_csv(grocery_prices_24_file_path)
grocery_prices_17_data = pd.read_csv(grocery_prices_17_file_path)

# preprocess wages data
wages_data["Effective Date"] = pd.to_datetime(
    wages_data["Effective Date"], format="%d-%b-%y", errors="coerce"
)
wages_data["Year"] = wages_data["Effective Date"].dt.year
wages_data["Minimum Wage"] = (
    wages_data["Minimum Wage"].str.replace(r"[^\d.]", "", regex=True).astype(float)
)

# filter wages data for 2000-2024
wages_data_filtered = wages_data[wages_data["Year"] >= 2000]
average_wages = wages_data_filtered.groupby("Year")["Minimum Wage"].mean().reset_index()

# preprocess inflation data
inflation_data["date"] = pd.to_datetime(inflation_data["date"])
inflation_data["Year"] = inflation_data["date"].dt.year
inflation_data_filtered = inflation_data[inflation_data["Year"] >= 2000]

# inflation-adjusted wages (real wages)
merged_wages_inflation = pd.merge(
    average_wages, inflation_data_filtered, on="Year", how="inner"
)
merged_wages_inflation["Real Minimum Wage"] = (
    merged_wages_inflation["Minimum Wage"]
    / (1 + merged_wages_inflation["annual_percent_change"] / 100)
)

# preprocess grocery prices data (2017-2024)
grocery_prices_24_data["REF_DATE"] = pd.to_datetime(grocery_prices_24_data["REF_DATE"])
grocery_prices_24_data["Year"] = grocery_prices_24_data["REF_DATE"].dt.year
grocery_prices_24_data_filtered = grocery_prices_24_data[
    (grocery_prices_24_data["Year"] >= 2017) & (grocery_prices_24_data["GEO"] == "Canada")
]
average_grocery_prices_24 = grocery_prices_24_data_filtered.groupby("Year")["VALUE"].mean().reset_index()

# preprocess grocery prices data (2000-2017)
grocery_prices_17_data["REF_DATE"] = pd.to_datetime(grocery_prices_17_data["REF_DATE"])
grocery_prices_17_data["Year"] = grocery_prices_17_data["REF_DATE"].dt.year
grocery_prices_17_data_filtered = grocery_prices_17_data[
    (grocery_prices_17_data["Year"] >= 2000) & (grocery_prices_17_data["GEO"] == "Canada")
]
average_grocery_prices_17 = grocery_prices_17_data_filtered.groupby("Year")["VALUE"].mean().reset_index()

# merge grocery prices from both datasets
combined_grocery_prices = pd.concat([average_grocery_prices_17, average_grocery_prices_24])

# adjust grocery prices for inflation (deduplicate for 2017 and onwards)
merged_groceries_inflation = pd.merge(
    combined_grocery_prices, inflation_data_filtered, on="Year", how="inner"
)

# deduplicate by aggregating (e.g., taking the mean for each year)
merged_groceries_inflation = (
    merged_groceries_inflation.groupby("Year", as_index=False)
    .agg({"VALUE": "mean", "annual_percent_change": "mean"})
)

# recalculate real grocery prices after deduplication
merged_groceries_inflation["Real Grocery Price"] = (
    merged_groceries_inflation["VALUE"]
    / (1 + merged_groceries_inflation["annual_percent_change"] / 100)
)

# merge datasets for analysis
final_data = pd.merge(
    merged_wages_inflation[["Year", "Real Minimum Wage"]],
    merged_groceries_inflation[["Year", "Real Grocery Price"]],
    on="Year",
    how="inner",
)

# Linear regression
X = final_data["Real Minimum Wage"].values.reshape(-1, 1)
y = final_data["Real Grocery Price"].values

model = LinearRegression()
model.fit(X, y)
slope = model.coef_[0]
intercept = model.intercept_

plt.figure(figsize=(10, 6))
plt.scatter(final_data["Real Minimum Wage"], final_data["Real Grocery Price"], color="blue", label="Data Points")
plt.plot(final_data["Real Minimum Wage"], model.predict(X), color="red", label="Regression Line")
plt.xlabel("Inflation-Adjusted Minimum Wage")
plt.ylabel("Inflation-Adjusted Grocery Price")
plt.title("Real Minimum Wage vs. Real Grocery Prices (2000-2024)")
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig('../plots/minimum_wage_vs_real_grocery_prices.png', dpi=300, bbox_inches='tight')

final_data.to_csv("./real_wage_grocery_comparison.csv", index=False)
print("Processed data saved to 'real_wage_grocery_comparison.csv'.")
