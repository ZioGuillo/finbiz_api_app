import os
import secrets
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, Response, flash
from flask_cors import CORS
from flask_session import Session
from prometheus_flask_exporter import PrometheusMetrics
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv

import plotly.graph_objects as go
import numpy as np

# Assuming stocks_app, process_stock_data, and analyze_stock are correctly imported from your stocks module
from stocks import stocks_app, process_stock_data, analyze_stock
from form_tool import FormTool  # Assuming FormTool is the correct import based on your context

# Load environment variables from .env file
load_dotenv()

secret_key = secrets.token_hex(16)  # 16 bytes (128 bits) is a common length for secret keys

app = Flask(__name__)
# Use environment variables for configuration
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_LIFETIME', 3600))  # Default to 1 hour

# Initialize extensions
csrf = CSRFProtect(app)
CORS(app, supports_credentials=True)
Session(app)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0', app_name='finbiz_app')

@app.route('/')
def index():
    # Fetch stock data for each sector. This is a placeholder.
    # You would replace this with actual data fetching logic.
    stock_data_by_sector = {
        'Technology': [
            {'symbol': 'AAPL', 'price': '150.00', 'company_name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'price': '280.00', 'company_name': 'Microsoft Corporation'},
            {'symbol': 'GOOGL', 'price': '2700.00', 'company_name': 'Alphabet Inc.'},
            {'symbol': 'META', 'price': '320.00', 'company_name': 'Meta Platforms, Inc.'},
            {'symbol': 'INTC', 'price': '48.00', 'company_name': 'Intel Corporation'}
        ],
        'Health Care': [
            {'symbol': 'JNJ', 'price': '170.00', 'company_name': 'Johnson & Johnson'},
            {'symbol': 'PFE', 'price': '42.00', 'company_name': 'Pfizer Inc.'},
            {'symbol': 'MRK', 'price': '76.00', 'company_name': 'Merck & Co., Inc.'},
            {'symbol': 'ABBV', 'price': '105.00', 'company_name': 'AbbVie Inc.'},
            {'symbol': 'TMO', 'price': '480.00', 'company_name': 'Thermo Fisher Scientific Inc.'}
        ],
        'Financials': [
            {'symbol': 'JPM', 'price': '125.00', 'company_name': 'JPMorgan Chase & Co.'},
            {'symbol': 'BAC', 'price': '30.00', 'company_name': 'Bank of America Corp'},
            {'symbol': 'WFC', 'price': '45.00', 'company_name': 'Wells Fargo & Company'},
            {'symbol': 'C', 'price': '65.00', 'company_name': 'Citigroup Inc.'},
            {'symbol': 'GS', 'price': '350.00', 'company_name': 'The Goldman Sachs Group, Inc.'}
        ],
        'Consumer Discretionary': [
            {'symbol': 'AMZN', 'price': '105.00', 'company_name': 'Amazon.com, Inc.'},
            {'symbol': 'TSLA', 'price': '900.00', 'company_name': 'Tesla, Inc.'},
            {'symbol': 'HD', 'price': '310.00', 'company_name': 'The Home Depot, Inc.'},
            {'symbol': 'MCD', 'price': '240.00', 'company_name': 'McDonald\'s Corporation'},
            {'symbol': 'NKE', 'price': '130.00', 'company_name': 'Nike, Inc.'}
        ],
        'Consumer Staples': [
            {'symbol': 'PG', 'price': '140.00', 'company_name': 'The Procter & Gamble Company'},
            {'symbol': 'KO', 'price': '60.00', 'company_name': 'The Coca-Cola Company'},
            {'symbol': 'PEP', 'price': '165.00', 'company_name': 'PepsiCo, Inc.'},
            {'symbol': 'WMT', 'price': '135.00', 'company_name': 'Walmart Inc.'},
            {'symbol': 'COST', 'price': '490.00', 'company_name': 'Costco Wholesale Corporation'}
        ],
        'Energy': [
            {'symbol': 'XOM', 'price': '90.00', 'company_name': 'Exxon Mobil Corporation'},
            {'symbol': 'CVX', 'price': '115.00', 'company_name': 'Chevron Corporation'},
            {'symbol': 'COP', 'price': '95.00', 'company_name': 'ConocoPhillips'},
            {'symbol': 'SLB', 'price': '40.00', 'company_name': 'Schlumberger Limited'},
            {'symbol': 'EOG', 'price': '110.00', 'company_name': 'EOG Resources, Inc.'}
        ],
        'Industrials': [
            {'symbol': 'GE', 'price': '75.00', 'company_name': 'General Electric Company'},
            {'symbol': 'MMM', 'price': '150.00', 'company_name': '3M Company'},
            {'symbol': 'BA', 'price': '200.00', 'company_name': 'The Boeing Company'},
            {'symbol': 'HON', 'price': '180.00', 'company_name': 'Honeywell International Inc.'},
            {'symbol': 'UNP', 'price': '210.00', 'company_name': 'Union Pacific Corporation'}
        ],
        # Add other sectors following the same structure
        'Utilities': [
            {'symbol': 'NEE', 'price': '75.00', 'company_name': 'NextEra Energy, Inc.'},
            {'symbol': 'DUK', 'price': '100.00', 'company_name': 'Duke Energy Corporation'},
            {'symbol': 'SO', 'price': '62.00', 'company_name': 'The Southern Company'},
            {'symbol': 'AEP', 'price': '80.00', 'company_name': 'American Electric Power Company, Inc.'},
            {'symbol': 'EXC', 'price': '43.00', 'company_name': 'Exelon Corporation'}
        ],
        'Real Estate': [
            {'symbol': 'AMT', 'price': '250.00', 'company_name': 'American Tower Corporation'},
            {'symbol': 'PLD', 'price': '110.00', 'company_name': 'Prologis, Inc.'},
            {'symbol': 'CCI', 'price': '170.00', 'company_name': 'Crown Castle International Corp.'},
            {'symbol': 'EQIX', 'price': '700.00', 'company_name': 'Equinix, Inc.'},
            {'symbol': 'SPG', 'price': '120.00', 'company_name': 'Simon Property Group, Inc.'}
        ],
        'Materials': [
            {'symbol': 'LIN', 'price': '290.00', 'company_name': 'Linde plc'},
            {'symbol': 'ECL', 'price': '160.00', 'company_name': 'Ecolab Inc.'},
            {'symbol': 'SHW', 'price': '250.00', 'company_name': 'The Sherwin-Williams Company'},
            {'symbol': 'APD', 'price': '280.00', 'company_name': 'Air Products and Chemicals, Inc.'},
            {'symbol': 'DD', 'price': '72.00', 'company_name': 'DuPont de Nemours, Inc.'}
        ],
        'Telecommunication Services': [
            {'symbol': 'T', 'price': '24.00', 'company_name': 'AT&T Inc.'},
            {'symbol': 'VZ', 'price': '50.00', 'company_name': 'Verizon Communications Inc.'},
            {'symbol': 'TMUS', 'price': '130.00', 'company_name': 'T-Mobile US, Inc.'},
            {'symbol': 'CHTR', 'price': '600.00', 'company_name': 'Charter Communications, Inc.'},
            {'symbol': 'SBAC', 'price': '206.00', 'company_name': 'SBA Communications Corporation'}
            # Placeholder for another Telecommunication Service company if needed
        ]
    }

     # Prepare data for the heat map
    z_values = []  # This will contain the heat map values
    hover_text = []  # This will contain the hover-over text
    x_labels = []  # This will contain the x-axis labels for the sector with the most stocks

    # Find the sector with the most stocks and use its symbols as x-axis labels
    max_stocks = max(len(stocks) for stocks in stock_data_by_sector.values())
    for sector, stocks in stock_data_by_sector.items():
        if len(stocks) == max_stocks:
            x_labels = [stock['symbol'] for stock in stocks]
            break

    # Normalize the prices and create hover text
    for sector, stocks in stock_data_by_sector.items():
        prices = [float(stock['price']) for stock in stocks]
        hover_row = [f"{stock['symbol']}<br>Sector: {sector}<br>Price: ${stock['price']}" for stock in stocks]
        
        # Pad sectors with fewer stocks to match the max number of stocks
        if len(stocks) < max_stocks:
            prices.extend([None] * (max_stocks - len(stocks)))
            hover_row.extend([''] * (max_stocks - len(stocks)))
        
        z_values.append(prices)
        hover_text.append(hover_row)

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=list(stock_data_by_sector.keys()),
        hoverongaps=False,
        text=hover_text,
        hoverinfo='text',
        colorscale='Reds',
    ))

    # Update layout for a cleaner look
    fig.update_layout(
        title=None,
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    # Make cells square
    fig.update_yaxes(
        scaleanchor='x',
        scaleratio=1,
    )

    # Disable interactive buttons but enable hover
    config = {'displayModeBar': False}

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False, config=config)

    # Pass the plot HTML to your template
    return render_template('index.html', stock_data_by_sector=stock_data_by_sector, plot_html=plot_html)

@app.route('/health')
def health():
    return Response(status=200)

@app.route('/stocks/analyze', methods=['GET', 'POST'])
def display_analysis():
    form = FormTool()
    symbol = ''
    if request.method == 'POST':
        symbol = form.symbol.data.upper() if form.validate_on_submit() else request.form.get('symbol', '').upper()
    else:
        symbol = request.args.get('symbol', session.get('symbol', '')).upper()

    if not symbol:
        flash("No symbol provided", "error")
        return redirect(url_for('index'))

    stock_data = process_stock_data(symbol)
    
    if 'error' in stock_data or stock_data.get('company_name') == 'UNKNOWN':
        flash(f'Stock symbol {symbol} does not exist.', 'error')
        return redirect(url_for('error_page'))  # This now refers to the correct route.


    analysis_results = analyze_stock(stock_data)
    
    session['analysis_results'] = analysis_results
    session['symbol'] = symbol
    return redirect(url_for('show_analysis_results'))


@app.route('/stocks/results')
def show_analysis_results():
    analysis_results = session.get('analysis_results', {})
    symbol = session.get('symbol', '').upper()

    if symbol not in analysis_results:
        flash('The requested symbol does not exist. Please try again.', 'error')
        return redirect(url_for('index'))
    return render_template('analysis_results.html', results=analysis_results, symbol=symbol)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

@app.route('/error')
def error_page():
    # Here, you can customize the error message or use a generic one.
    return render_template('error_page.html', error_message="An error occurred.")

# Register the blueprint from the stocks module
app.register_blueprint(stocks_app, url_prefix='/stocks')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
