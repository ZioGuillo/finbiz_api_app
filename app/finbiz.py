from finvizfinance.quote import finvizfinance

def process_stock_data(symbol):
    # Initialize the stock object
    stock = finvizfinance(symbol)

    # Fetch stock fundamentals
    try:
        stock_fundamentals = stock.ticker_fundament()
        # Fetch stock price (assuming 'Price' key holds the latest price)
        stock_price = stock_fundamentals.get('Price', 'N/A')
    except Exception as e:
        # Handle exceptions (e.g., if the symbol is not found or if there's a network issue)
        return {'error': str(e)}

    # Extract the required data
    per = stock_fundamentals.get('P/E', 'N/A')
    fper = stock_fundamentals.get('Forward P/E', 'N/A')
    beta = stock_fundamentals.get('Beta', 'N/A')
    target_price = stock_fundamentals.get('Target Price', 'N/A')

    # Additional data processing if needed

    processed_data = {
        'symbol': symbol,
        'Final Day Price': stock_price,
        'PER': per,
        'FPER': fper,
        'Beta': beta,
        'Target Price': target_price
    }

    return processed_data

def analyze_stock(stock_data):
    # Extract needed data
    per = float(stock_data.get('PER', 0)) if stock_data.get('PER', 0) != 'N/A' else 0
    fper = float(stock_data.get('FPER', 0)) if stock_data.get('FPER', 0) != 'N/A' else 0
    stock_price = float(stock_data.get('Final Day Price', 'N/A'))

    # Calculations
    percentage_var_month = 1 / per if per else 0
    var_puntual_month = stock_price * percentage_var_month

    percentage_var_3_month = 1 / fper if fper else 0
    var_puntual_3_month = stock_price * percentage_var_3_month

    # Further analysis based on the calculated values
    # Implement additional criteria based on your formulas

    results = {
        "percentage_var_month": percentage_var_month,
        "var_puntual_month": var_puntual_month,
        "percentage_var_3_month": percentage_var_3_month,
        "var_puntual_3_month": var_puntual_3_month,
        # Include results from further criteria here
    }

    return results
