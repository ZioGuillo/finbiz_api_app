from finvizfinance.quote import finvizfinance

def process_stock_data(symbol):
    # Initialize the stock object
    try:
        stock = finvizfinance(symbol)
        stock_fundamentals = stock.ticker_fundament()

        # Extract the required data
        stock_price = float(stock_fundamentals.get('Price', 'N/A'))
        per = stock_fundamentals.get('P/E', 'N/A')
        fper = stock_fundamentals.get('Forward P/E', 'N/A')
        beta = stock_fundamentals.get('Beta', 'N/A')
        target_price = stock_fundamentals.get('Target Price', 'N/A')

        processed_data = {
            'symbol': symbol,
            'Final Day Price': stock_price,
            'PER': per,
            'FPER': fper,
            'Beta': beta,
            'Target Price': target_price
        }

    except Exception as e:
        # Handle specific error
        return {'error': f'Unable to find data for symbol {symbol}'}
        #return {'error': f'Unable to find data for symbol {symbol}: {str(e)}'}

    return processed_data

def analyze_stock(stock_data):
    symbol = stock_data.get('symbol', 'UNKNOWN').upper()
    per = stock_data.get('PER', '-')
    fper = stock_data.get('FPER', '-')
    stock_price = float(stock_data.get('Final Day Price', 'N/A'))

    # Check for valid PER and FPER
    per = float(per) if per.replace('.', '', 1).isdigit() else 'NONE'
    fper = float(fper) if fper.replace('.', '', 1).isdigit() else 'NONE'

    # Calculate var_puntual_month and var_puntual_3_month
    percentage_var_month = 1 / per if per != 'NONE' else 'NONE'
    var_puntual_month = stock_price * percentage_var_month if percentage_var_month != 'NONE' else 'NONE'
    percentage_var_3_month = 1 / fper if fper != 'NONE' else 'NONE'
    var_puntual_3_month = stock_price * percentage_var_3_month if percentage_var_3_month != 'NONE' else 'NONE'

    # Criteria 1: Estimates Targets
    mensual_value_target_monthly = stock_price + var_puntual_month if var_puntual_month != 'NONE' else 'NONE'
    target_price_by_banks = float(stock_data.get('Target Price', 'N/A')) if stock_data.get('Target Price', 'N/A') != 'N/A' else 0
    target_price_indicator = (stock_price * (per / fper)) if (per != 'NONE' and fper != 'NONE') else 0
    trimestral_value_objective = stock_price + var_puntual_3_month if var_puntual_3_month != 'NONE' else 'NONE'

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
    target_price_by_banks = float(stock_data.get('Target Price', 0)) if stock_data.get('Target Price', 'N/A') != 'N/A' else 0

    stock_price = float(stock_data.get('Final Day Price', 'N/A')) if stock_data.get('Final Day Price', 'N/A') != 'N/A' else 0
    grow = target_price_by_banks - stock_price if target_price_by_banks and stock_price else 'N/A'


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
