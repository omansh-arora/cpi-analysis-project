# Takes the average Minimum wage using all provinces, for each year
# Takes the average CPI on food using all provinces, for each year


import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

cpi_file_path = "../raw_data/cpi.csv"
wages_file_path = "../raw_data/wages.csv"
cpi_data = pd.read_csv(cpi_file_path)
wages_data = pd.read_csv(wages_file_path)

# process wages data
wages_data["Effective Date"] = pd.to_datetime(
    wages_data["Effective Date"], format="%d-%b-%y", errors="coerce"
)
wages_data["Year"] = wages_data["Effective Date"].dt.year
wages_data["Minimum Wage"] = (
    wages_data["Minimum Wage"].str.replace(r"[^\d.]", "", regex=True).astype(float)
)

# wages data from 2000 onwards and calculate average minimum wage for each year
wages_data_cleaned = wages_data.dropna(subset=["Effective Date"])
wages_data_cleaned = wages_data_cleaned[wages_data_cleaned["Year"] >= 2000]
average_wages_all_months = wages_data_cleaned.groupby("Year")["Minimum Wage"].mean()

# process CPI data
cpi_food_long = cpi_data[cpi_data["Products"] == "Food 5"].melt(
    id_vars=["Products"], var_name="Month-Year", value_name="CPI Food"
)
cpi_food_long["Year"] = cpi_food_long["Month-Year"].str.extract(r"(\d{4})").astype(int)
cpi_food_long["Month"] = cpi_food_long["Month-Year"].str.extract(r"([a-zA-Z]+)")
cpi_food_long_filtered = cpi_food_long[cpi_food_long["Year"] >= 2000]
average_cpi_food_by_year = (
    cpi_food_long_filtered.groupby("Year")["CPI Food"].mean().reset_index()
)

# merge average wages and CPI data
merged_data_all_months = pd.merge(
    average_wages_all_months, average_cpi_food_by_year, on="Year", how="inner"
)
merged_data_all_months.columns = ["Year", "Average Minimum Wage", "Average CPI Food"]
output_csv_path = "./merged_minimum_wage_cpi_data.csv"
merged_data_all_months.to_csv(output_csv_path, index=False)

# Linear Regression
X = merged_data_all_months["Average Minimum Wage"].values.reshape(-1, 1)
y = merged_data_all_months["Average CPI Food"].values

model_all_months = LinearRegression()
model_all_months.fit(X, y)

# regression line
slope_all_months = model_all_months.coef_[0]
intercept_all_months = model_all_months.intercept_

plt.figure(figsize=(10, 6))
plt.scatter(
    merged_data_all_months["Average Minimum Wage"],
    merged_data_all_months["Average CPI Food"],
    color="blue",
    label="Data Points",
)
plt.plot(
    X,
    model_all_months.predict(X),
    color="red",
    label="Regression Line",
)
plt.xlabel("Average Minimum Wage")
plt.ylabel("Average CPI for Food")
plt.title("Minimum Wage vs CPI for Food (Canada, Annual Averages)")
plt.legend()
plt.grid(True)
plt.show()
