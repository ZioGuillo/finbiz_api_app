from finvizfinance.quote import finvizfinance
import json
import time  # Import the time module

# Predefined stocks by sector
stocks_by_sector = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'INTC'],
    'Health Care': ['JNJ', 'PFE', 'MRK', 'ABBV', 'TMO'],
    'Financials': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
    'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
    'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
    'Industrials': ['GE', 'MMM', 'BA', 'HON', 'UNP'],
    'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'EXC'],
    'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'SPG'],
    'Materials': ['LIN', 'ECL', 'SHW', 'APD', 'DD'],
    'Telecommunication Services': ['T', 'VZ', 'TMUS', 'CHTR', 'SBAC']
}

def get_last_prices_by_sector(sector):
    """
    Fetches the last prices and company names of stocks for a given sector.

    :param sector: A string representing the sector from which to fetch stock symbols.
    :return: A JSON string containing the symbols, their last prices, and company names for the selected sector.
    """
    if sector not in stocks_by_sector:
        print(f"Error: Sector '{sector}' not found.")
        return None

    sector_symbols = stocks_by_sector[sector]
    stock_data = {}
    
    for symbol in sector_symbols:
        try:
            stock = finvizfinance(symbol)
            stock_fundamentals = stock.ticker_fundament()
            last_price = stock_fundamentals.get('Price', 'N/A')
            company_name = stock_fundamentals.get('Company', 'Unknown Company')
            stock_data[symbol] = {'Company Name': company_name, 'Last Price': last_price}
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            stock_data[symbol] = {'Company Name': 'Error fetching data', 'Last Price': 'Error fetching price'}

    return json.dumps(stock_data, indent=4)

def get_last_prices_by_all_sector():
    """
    Fetches the last prices and company names of stocks for all sectors,
    fetching 5 symbols at a time with a 5-second delay between each batch.
    
    :return: A dictionary containing the symbols, their last prices, and company names for all sectors.
    """
    stock_data_by_sector = {}
    batch_size = 4  # Number of symbols to fetch before delaying
    request_delay = 10  # Delay between batches in seconds

    for sector, symbols in stocks_by_sector.items():
        sector_data = []
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i+batch_size]
            for symbol in batch_symbols:
                try:
                    stock = finvizfinance(symbol)
                    stock_fundamentals = stock.ticker_fundament()
                    last_price = stock_fundamentals.get('Price', 'N/A')
                    company_name = stock_fundamentals.get('Company', 'Unknown Company')
                    sector_data.append({'symbol': symbol, 'price': last_price, 'company_name': company_name})
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    sector_data.append({'symbol': symbol, 'price': 'Error fetching price', 'company_name': 'Error fetching data'})

            # Delay after processing each batch, except for the last one
            if i + batch_size < len(symbols):
                print(f"Waiting for {request_delay} seconds...")
                time.sleep(request_delay)

        stock_data_by_sector[sector] = sector_data

    return stock_data_by_sector

# Example usage
stock_data_all_sector = get_last_prices_by_all_sector()
print(json.dumps(stock_data_all_sector, indent=4))

# Example usage:
# selected_sector = 'Telecommunication Services'
# json_result = get_last_prices_by_sector(selected_sector)
# print(json_result)
