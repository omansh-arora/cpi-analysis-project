import subprocess
import os

files = [
    'preprocessing_country_data.py',
    'preprocessing_province_data.py',
    'q3-min-wage-inflation-change/min_wage_inflation_correlation.py',
    'q5-basket-cost-inflation-change/basket_cost_inflation_correlation.py',
    'q6-num-min-wage-hours-basket-cost/num_hours_worked_for_basket.py',
    'q7-basket-province-prediction/basket_province_prediction.py'
]

current_dir = os.getcwd()
root_dir = os.path.abspath(os.path.join(current_dir, '../../'))
cpi_wage_data_with_inflation_country = os.path.join(root_dir, 'cpi_wage_data_with_inflation_country.csv')
price_wage_data_country = os.path.join(root_dir, 'price_wage_data_country.csv')
cpi_wage_data_with_inflation_province = os.path.join(root_dir, 'cpi_wage_data_with_inflation_province.csv')
price_wage_data_province = os.path.join(root_dir, 'price_wage_data_province.csv')

env = os.environ.copy()
env['root_dir'] = root_dir
env['cpi_wage_data_with_inflation_country'] = cpi_wage_data_with_inflation_country
env['price_wage_data_country'] = price_wage_data_country
env['cpi_wage_data_with_inflation_province'] = cpi_wage_data_with_inflation_province
env['price_wage_data_province'] = price_wage_data_province

for file in files:
    file_path = os.path.join(current_dir, file)
    
    if os.path.exists(file_path):
        print(f"Running {file}")
        try:
            file_dir = os.path.dirname(file_path)
            result = subprocess.run(['python3', file_path], capture_output=True, text=True, check=True, cwd=file_dir, env=env)
            print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"Error with {file}: {e.stderr.strip()}")
    else:
        print(f"{file} does not exist")
