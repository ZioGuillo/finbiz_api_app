from finvizfinance.quote import finvizfinance

def safe_float_convert(value, default=0.0):
    """Attempts to convert a value to float, returns default if conversion fails or value is None."""
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def process_stock_data(symbol):
    try:
        # Initialize the stock object
        stock = finvizfinance(symbol)
        stock_fundamentals = stock.ticker_fundament()

        # Get the name of the company
        company_name = stock_fundamentals.get('Company', 'N/A')

        # Extract the required data
        # check if it is a numeric value first, otherwise, use a default value such as 0.0
        stock_price = float(stock_fundamentals.get('Price', 'N/A'))
        per = stock_fundamentals.get('P/E', 'N/A')
        fper = stock_fundamentals.get('Forward P/E', 'N/A')
        beta = stock_fundamentals.get('Beta', 'N/A')
        target_price = stock_fundamentals.get('Target Price', 'N/A')

        # Create a dictionary with processed data
        processed_data = {
            'symbol': symbol,
            'company_name': company_name,
            'Final Day Price': stock_price,
            'PER': per,
            'FPER': fper,
            'Beta': beta,
            'Target Price': target_price
        }

    except Exception as e:
        # Handle specific error
        return {'error': f'Unable to find data for symbol {symbol}: {str(e)}'}

    return processed_data

def analyze_stock(stock_data):
    # Initialize variables, ensuring all numeric fields are safely converted to floats
    company_name = stock_data.get('company_name', 'UNKNOWN')
    symbol = stock_data.get('symbol', 'UNKNOWN').upper()
    stock_price = safe_float_convert(stock_data.get('Final Day Price'), 0.0)
    per = safe_float_convert(stock_data.get('PER'), None)
    fper = safe_float_convert(stock_data.get('FPER'), None)
    target_price_by_banks = safe_float_convert(stock_data.get('Target Price'), 0.0)
    beta = safe_float_convert(stock_data.get('Beta'), 1)  # Default to 1 if Beta is not available

    # Calculate indicators with defaults
    percentage_var_month = 1 / per if per else 0.0
    var_puntual_month = stock_price * percentage_var_month if percentage_var_month else 0.0
    percentage_var_3_month = 1 / fper if fper else 0.0
    var_puntual_3_month = stock_price * percentage_var_3_month if percentage_var_3_month else 0.0

    # Calculate target price indicator
    target_price_indicator = (stock_price * per / fper) if per and fper else 0.0

    # Validation based on estimated targets
    validation_criteria = {
        'objective_monthly': var_puntual_month > stock_price,
        'target_price': target_price_by_banks > stock_price,
        'target_indicators': target_price_indicator > stock_price,
        'trimestral_objective': var_puntual_3_month > stock_price
    }
    buy_validations = sum(validation_criteria.values())
    buy_validation = "BUY" if buy_validations == 4 else "NONE"

    # Define lambda for formatting or defaulting to "0.00"
    format_or_default = lambda x: f"{x:.2f}" if x is not None and x != 0.0 else "0.00"

    # Assemble results with formatted values or "0.00" defaults
    results = {
        symbol: {
            "Estimate_targets": {
                "Mensual Value Target Monthly": format_or_default(var_puntual_month),
                "Target Price by Banks": format_or_default(target_price_by_banks),
                "Target Price Indicator": format_or_default(target_price_indicator),
                "Trimestral Value Objective": format_or_default(var_puntual_3_month)
            },
            "Validation_based_on_estimated_targets": {
                "Validation Objective Monthly": "BUY" if validation_criteria['objective_monthly'] else "NONE",
                "Validation Target Price": "BUY" if validation_criteria['target_price'] else "NONE",
                "Validation Target Indicators": "BUY" if validation_criteria['target_indicators'] else "NONE",
                "Trimestral Objective Validation": "BUY" if validation_criteria['trimestral_objective'] else "NONE",
                "Present Value Counter": buy_validations,
                "Buy Validation": buy_validation
            },
            "Validation_based_on_target_price": {
                "Target Prices vs Objectives Monthly": "BUY" if var_puntual_month and target_price_by_banks > var_puntual_month else "NONE",
                "Target Prices Indicators vs Target Prices Bank": "BUY" if target_price_indicator > target_price_by_banks else "NONE",
                "Futures Values Count": sum(validation_criteria.values())
            },
            "Condition_validators": {
                "Condition 1": "Strong Buy" if buy_validations == 4 else ("BUY" if buy_validations >= 3 else "SELL"),
                "Condition 2": "Strong Buy" if buy_validations == 2 else "N/A",
                "Counter FUT + PRES": buy_validations
            },
            "Final_validation": {
                "Decision Medium Term": "Strong Buy" if buy_validations > 1 else ("BUY" if buy_validations == 1 else "N/A"),
                "Risk": "Low Risk" if beta < 1 else ("Medium Risk" if 1 <= beta < 1.09 else "High Risk"),
                "Decision Medium Term vs Risk": "Buy" if buy_validations > 0 and beta < 1.09 else "Sell",
                "stock_grow": format_or_default(target_price_by_banks - stock_price)
            },
            "Company_name": company_name,
            "Stock_price": format_or_default(stock_price),
            "PER": format_or_default(per),
            "FPER": format_or_default(fper),
            "Target Price": format_or_default(target_price_by_banks),
            "Percentage_var_month": format_or_default(percentage_var_month),
            "VAR_puntual_month": format_or_default(var_puntual_month),
            "Percentage_var_3_month": format_or_default(percentage_var_3_month),
            "VAR_puntual_3_month": format_or_default(var_puntual_3_month)
        }
    }

    return results
