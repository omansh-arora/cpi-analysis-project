import pandas as pd
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt

cpi_file_path = "../raw_data/cpi.csv"
wages_file_path = "../raw_data/wages.csv"

cpi_data = pd.read_csv(cpi_file_path)
wages_data = pd.read_csv(wages_file_path)

# wages data
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

# CPI data
cpi_long = cpi_data.melt(
    id_vars=["Products"], var_name="Month-Year", value_name="CPI"
)
cpi_long["Year"] = cpi_long["Month-Year"].str.extract(r"(\d{4})").astype(int)
cpi_long["Month"] = cpi_long["Month-Year"].str.extract(r"([a-zA-Z]+)")
cpi_long_filtered = cpi_long[cpi_long["Year"] >= 2000]

# exclude specified products
excluded_products = [
    "All-items", 
    "All-items excluding energy 7", 
    "All-items excluding food and energy 7"
]
cpi_long_filtered = cpi_long_filtered[~cpi_long_filtered["Products"].isin(excluded_products)]

# calculate annual averages for each product
average_cpi_by_product = cpi_long_filtered.groupby(["Year", "Products"])["CPI"].mean().reset_index()

# merge with wages data to calculate the gap
merged_data = pd.merge(
    average_cpi_by_product,
    average_wages_all_months.reset_index(),
    on="Year",
    how="inner"
)
merged_data["CPI-Wage Gap"] = merged_data["CPI"] - merged_data["Minimum Wage"]

# ANOVA
anova_results = f_oneway(
    *[
        merged_data[merged_data["Products"] == product]["CPI-Wage Gap"]
        for product in merged_data["Products"].unique()
    ]
)
print(f"ANOVA results: p-value = {anova_results.pvalue}")

# Tukey's HSD
tukey = pairwise_tukeyhsd(
    endog=merged_data["CPI-Wage Gap"],
    groups=merged_data["Products"],  
    alpha=0.05                        
)

# Tukey's HSD results
print("\nTukey's HSD Test Results:")
print(tukey)

# Plot
plt.figure(figsize=(12, 8))
tukey.plot_simultaneous()
plt.title("Tukey's HSD Test Results")
plt.xlabel("CPI-Wage Gap")
plt.show()

output_csv_path = "./cpi_wage_gap_analysis.csv"
merged_data.to_csv(output_csv_path, index=False)
print(f"Merged data saved to {output_csv_path}")
