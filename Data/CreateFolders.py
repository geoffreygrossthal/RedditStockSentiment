import os
from calendar import monthrange

# List of stock tickers
stock_tickers = [
    'MSFT', 'AMZN', 'GOOGL', 'FB', 
    'NFLX', 'NVDA', 'BRK.B', 'JPM', 
    'V', 'PG', 'DIS', 'PYPL', 'INTC'
]

# Loop through each stock ticker
for ticker in stock_tickers:
    # Set the base directory for the current ticker
    base_dir = ticker

    # Create the main directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # Loop through each year from 2024 to 2014
    for year in range(2024, 2013, -1):
        year_path = os.path.join(base_dir, str(year))
        os.makedirs(year_path, exist_ok=True)

        # Loop through each month from January (1) to December (12)
        for month in range(1, 13):
            month_path = os.path.join(year_path, f'{month:02d}')
            os.makedirs(month_path, exist_ok=True)

            # Get the number of days in the month
            num_days = monthrange(year, month)[1]

            # Loop through each day of the month
            for day in range(1, num_days + 1):
                day_path = os.path.join(month_path, f'{day:02d}')
                os.makedirs(day_path, exist_ok=True)

print("Folders created successfully.")
