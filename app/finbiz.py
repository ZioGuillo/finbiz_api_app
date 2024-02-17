from finvizfinance.quote import finvizfinance

def safe_float_convert(value, default=0.0):
    """Attempts to convert a value to float, returns default if conversion fails."""
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
    company_name = stock_data.get('company_name', 'UNKNOWN')
    symbol = stock_data.get('symbol', 'UNKNOWN').upper()
    per = stock_data.get('PER', '-')
    fper = stock_data.get('FPER', '-')
    # Use the safe_float_convert function to safely convert 'Final Day Price'
    stock_price = safe_float_convert(stock_data.get('Final Day Price', 'N/A'), 0.0)

    # Check for valid PER and FPER
    per = float(per) if per.replace('.', '', 1).isdigit() else 'NONE'
    fper = float(fper) if fper.replace('.', '', 1).isdigit() else 'NONE'

    # Calculate var_puntual_month and var_puntual_3_month
    # Calculate percentage_var_month and handle cases where per is 'NONE'
    percentage_var_month = "{:.4f}".format(1 / float(per)) if per != 'NONE' else 'NONE'

    # Calculate var_puntual_month and handle cases where percentage_var_month is 'NONE'
    var_puntual_month = "{:.2f}".format(stock_price * float(percentage_var_month)) if percentage_var_month != 'NONE' else 'NONE'

    # Calculate percentage_var_3_month and handle cases where fper is 'NONE'
    percentage_var_3_month = "{:.4f}".format(1 / float(fper)) if fper != 'NONE' else 'NONE'

    # Calculate var_puntual_3_month and handle cases where percentage_var_3_month is 'NONE'
    var_puntual_3_month = "{:.2f}".format(stock_price * float(percentage_var_3_month)) if percentage_var_3_month != 'NONE' else 'NONE'

    # Criteria 1: Estimates Targets
    # Calculate mensual_value_target_monthly and handle cases where var_puntual_month is 'NONE'
    mensual_value_target_monthly = "{:.2f}".format(stock_price + float(var_puntual_month)) if var_puntual_month != 'NONE' else 'NONE'

    # Ensure target_price_by_banks is a float. You've handled 'N/A', so this should be okay.
    target_price_by_banks = float(stock_data.get('Target Price', 0))  # Default to 0 if 'N/A'

    # Convert target_price_indicator to float for comparison
    target_price_indicator = float((stock_price * (float(per) / float(fper)))) if (per != 'NONE' and fper != 'NONE') else 0

    # Calculate trimestral_value_objective and handle cases where var_puntual_3_month is 'NONE'
    trimestral_value_objective = "{:.2f}".format(stock_price + float(var_puntual_3_month)) if var_puntual_3_month != 'NONE' else 'NONE'

    # Second Criteria: Validation Based on Estimated Targets
    validation_objective_monthly = "BUY" if isinstance(mensual_value_target_monthly, float) and mensual_value_target_monthly > stock_price else "NONE"
    validation_target_price = "BUY" if isinstance(target_price_by_banks, float) and target_price_by_banks > stock_price else "NONE"
    validation_target_indicators = "BUY" if isinstance(target_price_indicator, float) and target_price_indicator > stock_price else "NONE"
    trimestral_objective_validation = "BUY" if isinstance(trimestral_value_objective, float) and trimestral_value_objective > stock_price else "NONE"

    # Counting BUY validations
    present_value_counter = [validation_objective_monthly, validation_target_price, validation_target_indicators, trimestral_objective_validation].count("BUY")

    # Buy Validation
    buy_validation = "BUY" if present_value_counter == 4 else "NONE"

    # Additional Criteria: Validation Based on Target Price
    target_prices_vs_objectives_monthly = "BUY" if isinstance(mensual_value_target_monthly, float) and target_price_by_banks > mensual_value_target_monthly else "NONE"
    # Now do the comparison
    target_prices_indicators_vs_target_prices_bank = "BUY" if target_price_indicator > target_price_by_banks else "NONE"
    # Counting BUY validations
    futures_values_count = [target_prices_vs_objectives_monthly, target_prices_indicators_vs_target_prices_bank].count("BUY")

    # Criteria for Condition Validators
    condition1 = "Strong Buy" if present_value_counter == 4 else ("BUY" if present_value_counter == 3 else "SELL")
    condition2 = "Strong Buy" if futures_values_count == 2 else "N/A"

    # Counter for combined 'Strong Buy' outcomes
    counter_fut_pres = [condition1, condition2].count("Strong Buy")

    # Decision Medium Term
    decision_medium_term = "Strong Buy" if counter_fut_pres == 2 else ("BUY" if counter_fut_pres == 1 else "N/A")

    # Risk
    beta_value = float(stock_data.get('Beta', 1))  # Default to 1 if Beta is not available
    if beta_value < 1:
        risk = "Low Risk"
    elif 1 <= beta_value < 1.09:
        risk = "Medium Risk"
    else:
        risk = "High Risk"

    # Decision Medium Term vs Risk
    if decision_medium_term == "Strong Buy" and risk == "Low Risk":
        decision_medium_term_vs_risk = "Strong Buy"
    elif decision_medium_term == "Strong Buy" and risk == "Medium Risk":
        decision_medium_term_vs_risk = "Buy"
    elif decision_medium_term == "Buy" and risk == "Low Risk":
        decision_medium_term_vs_risk = "Buy"
    else:
        decision_medium_term_vs_risk = "Sell"
        
    # Stock Growth Calculation
    # Convert target_price_by_banks to float or set to a default value
    # Convert target_price_by_banks to float, handle cases where it's 'N/A'
    target_price_by_banks = "{:.2f}".format(float(stock_data.get('Target Price', 'N/A'))) if stock_data.get('Target Price', 'N/A') != 'N/A' else 'N/A'

    # Convert stock_price to float, handle cases where it's 'N/A'
    stock_price = "{:.2f}".format(float(stock_data.get('Final Day Price', 'N/A'))) if stock_data.get('Final Day Price', 'N/A') != 'N/A' else 'N/A'

    # Calculate grow and format it with 4 decimal places
    grow = "{:.4f}".format(float(target_price_by_banks) - float(stock_price)) if target_price_by_banks != 'N/A' and stock_price != 'N/A' else 'N/A'

    # Structuring the results with the stock symbol in uppercase as the primary key
    results = {
        symbol: {
            "Estimate_targets": {
                "Mensual Value Target Monthly": mensual_value_target_monthly,
                "Target Price by Banks": target_price_by_banks,
                "Target Price Indicator": target_price_indicator,
                "Trimestral Value Objective": trimestral_value_objective
            },
            "Validation_based_on_estimated_targets": {
                "Validation Objective Monthly": validation_objective_monthly,
                "Validation Target Price": validation_target_price,
                "Validation Target Indicators": validation_target_indicators,
                "Trimestral Objective Validation": trimestral_objective_validation,
                "Present Value Counter": present_value_counter,
                "Buy Validation": buy_validation
            },
            "Validation_based_on_target_price": {
                "Target Prices vs Objectives Monthly": target_prices_vs_objectives_monthly,
                "Target Prices Indicators vs Target Prices Bank": target_prices_indicators_vs_target_prices_bank,
                "Futures Values Count": futures_values_count
            },
            "Condition_validators": {
                "Condition 1": condition1,
                "Condition 2": condition2,
                "Counter FUT + PRES": counter_fut_pres
            },
            "Final_validation": {
                "Decision Medium Term": decision_medium_term,
                "Risk": risk,
                "Decision Medium Term vs Risk": decision_medium_term_vs_risk,
                "stock_grow": grow
            },
            "Company_name": company_name,
            "Stock_price": stock_price,
            "PER": per,
            "FPER": fper,
            "Target Price": target_price_by_banks,
            "Percentage_var_month": percentage_var_month,
            "VAR_puntual_month": var_puntual_month,
            "Percentage_var_3_month": percentage_var_3_month,
            "VAR_puntual_3_month": var_puntual_3_month
        }
    }

    return results
