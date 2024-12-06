import pandas as pd
import numpy as np

def load_data(price_path_22, price_path_24, wage_path):
    """Load price and wage datasets."""
    df_22 = pd.read_csv(price_path_22)
    df_24 = pd.read_csv(price_path_24)
    wage_df = pd.read_csv(wage_path)
    return df_22, df_24, wage_df

def filter_and_format_dates(df_22, df_24):
    """Filter and format date columns in both price datasets."""
    df_22['REF_DATE'] = pd.to_datetime(df_22['REF_DATE'])
    df_24['REF_DATE'] = pd.to_datetime(df_24['REF_DATE'])
    df_22 = df_22[df_22['GEO'] == 'Canada']
    df_24 = df_24[df_24['GEO'] == 'Canada']
    df_22 = df_22[df_22['REF_DATE'].dt.year > 1999]
    df_24 = df_24[(df_24['REF_DATE'].dt.year >= 2022) & (df_24['REF_DATE'].dt.month >= 3)]
    return df_22, df_24

def filter_items(df_22, df_24, items_22, items_24):
    """Filter items in both datasets based on specific lists."""
    df_22 = df_22[df_22['Products'].isin(items_22)]
    df_24 = df_24[df_24['Products'].isin(items_24)]
    return df_22, df_24

def clean_combined_data(df_22, df_24, items_22, items_24):
    """Combine datasets, drop unnecessary columns, and adjust item names."""
    combined_df = pd.concat([df_22, df_24], ignore_index=True)
    combined_df.drop(['GEO', 'DGUID', 'UOM', 'UOM_ID', 'SCALAR_FACTOR', 'SCALAR_ID', 'VECTOR', 'COORDINATE', 'STATUS', 'SYMBOL', 'TERMINATED', 'DECIMALS'], axis=1, inplace=True)
    combined_df.rename(columns={'REF_DATE': 'date', 'Products': 'item', 'VALUE': 'price'}, inplace=True)
    combined_df.loc[combined_df['item'] == 'Carrots, 1 kilogram', 'price'] *= 1.36
    replacement_dict = dict(zip(items_22, items_24))
    combined_df['item'] = combined_df['item'].replace(replacement_dict)
    return combined_df

def remove_dollar_sign(st):
    """Remove dollar sign from strings and convert to float."""
    st = str(st).replace('$', '')
    return float(st)

def process_wage_data(wage_df):
    """Process wage data to calculate average annual minimum wage."""

    wage_df['Effective Date'] = pd.to_datetime(wage_df['Effective Date'], format="%d-%b-%y")
    wage_df['Minimum Wage'] = wage_df['Minimum Wage'].apply(remove_dollar_sign)
    wage_df['year'] = wage_df['Effective Date'].dt.year
    avg_wage_df = wage_df.groupby('year')['Minimum Wage'].mean().reset_index()
    return avg_wage_df

def load_and_reformat_cpi(cpi_path):
    """Load the CPI data and reformat it to long format with each month as a row."""
    cpi_df = pd.read_csv(cpi_path)
    
    # Melt the DataFrame to make each month a row, with 'Products' as the identifier
    cpi_df = cpi_df.melt(id_vars=['Products'], var_name='Month_Year', value_name='CPI')
    
    # Convert the 'Month_Year' column to a datetime format
    cpi_df['date'] = pd.to_datetime(cpi_df['Month_Year'], format='%B %Y')
    
    # Drop the original 'Month_Year' column
    cpi_df.drop(columns=['Month_Year'], inplace=True)
    
    return cpi_df

def create_cpi_wage_dataset(cpi_df, avg_wage_df):
    """Combine CPI data with average wage data on year to create a standalone dataset."""
    cpi_df['year'] = cpi_df['date'].dt.year
    cpi_wage_df = cpi_df.merge(avg_wage_df, on='year', how='left')
    cpi_wage_df.drop(columns=['year'], inplace=True)
    cpi_wage_df.rename(columns={'Products':'product','CPI':'cpi', 'Minimum Wage':'minimum_wage'}, inplace = True)
    return cpi_wage_df


def merge_wages_with_prices(combined_df, avg_wage_df):
    """Merge the average wage data with the price data on the year."""
    combined_df['year'] = combined_df['date'].dt.year
    combined_df = combined_df.merge(avg_wage_df, on='year', how='left')
    combined_df.rename(columns={'Minimum Wage': 'min_wage'}, inplace=True)
    combined_df.drop(columns=['year'], inplace=True)
    return combined_df

def save_cleaned_data(df, output_path):
    """Save the cleaned DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)

def load_inflation_data(inflation_path):
    """Load and format inflation data."""
    inflation_df = pd.read_csv(inflation_path)
    inflation_df['date'] = pd.to_datetime(inflation_df['date'])
    inflation_df['year'] = inflation_df['date'].dt.year
    inflation_df = inflation_df[['year', 'annual_percent_change']]
    inflation_df.rename(columns={'annual_percent_change': 'inflation_change'}, inplace=True)
    return inflation_df

def add_inflation_change(cpi_wage_df, inflation_df):
    """Add the inflation change column to the CPI-wage dataset."""
    cpi_wage_df['year'] = cpi_wage_df['date'].dt.year
    cpi_wage_df = cpi_wage_df.merge(inflation_df, on='year', how='left')
    cpi_wage_df.drop(columns=['year'], inplace=True)
    return cpi_wage_df

if __name__ == "__main__":
    # Define paths and items to process
    items_22 = ['Baked beans, canned, 398 millilitres', 'Ground beef, 1 kilogram', 'Eggs, 1 dozen', 'Apples, 1 kilogram', 'Bananas, 1 kilogram', 'Carrots, 1 kilogram', 'Chicken, 1 kilogram', 'Bread, 675 grams', 'Potatoes, 4.54 kilograms', 'Onions, 1 kilogram']
    items_24 = ['Canned baked beans, 398 millilitres', 'Ground beef, per kilogram', 'Eggs, 1 dozen', 'Apples, per kilogram', 'Bananas, per kilogram', 'Carrots, 1.36 kilograms', 'Whole chicken, per kilogram', 'White bread, 675 grams', 'Potatoes, 4.54 kilograms', 'Onions, per kilogram']

    # Load and process data
    df_22, df_24, wage_df = load_data('raw_data/price-to-17.csv', 'raw_data/price-to-24.csv', 'raw_data/wages.csv')
    df_22, df_24 = filter_and_format_dates(df_22, df_24)
    df_22, df_24 = filter_items(df_22, df_24, items_22, items_24)
    combined_df = clean_combined_data(df_22, df_24, items_22, items_24)

    avg_wage_df = process_wage_data(wage_df)
    combined_df = merge_wages_with_prices(combined_df, avg_wage_df)
    save_cleaned_data(combined_df, 'price_wage_data_country.csv')

    # Load and process CPI data
    cpi_df = load_and_reformat_cpi('raw_data/cpi.csv')
    
    
    # Process wage data and create a separate CPI-wage dataset
    avg_wage_df = process_wage_data(wage_df)
    cpi_wage_df = create_cpi_wage_dataset(cpi_df, avg_wage_df)
    inflation_df = load_inflation_data('raw_data/inflation.csv')

    cpi_wage_df = add_inflation_change(cpi_wage_df, inflation_df)
    save_cleaned_data(cpi_wage_df, 'cpi_wage_data_with_inflation_country.csv')