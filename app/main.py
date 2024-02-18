from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, Response
from flask_cors import CORS
from flask_session import Session
from prometheus_flask_exporter import PrometheusMetrics
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
from flask_caching import Cache
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import secrets

# Assuming get_last_prices_by_all_sector, stocks_app, process_stock_data, and analyze_stock are correctly imported
from stock_list import get_last_prices_by_all_sector
from stocks import stocks_app, process_stock_data, analyze_stock
from form_tool import FormTool
import plotly.graph_objects as go

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=secrets.token_hex(16),
    SESSION_TYPE='filesystem',
    SESSION_COOKIE_SECURE=True,
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=int(os.getenv('SESSION_LIFETIME', 3600)),
    CACHE_TYPE='simple'
)

cache = Cache(app)
cache.init_app(app)
csrf = CSRFProtect(app)
CORS(app, supports_credentials=True)
Session(app)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0', app_name='finbiz_app')

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def update_stock_data():
    """Fetch and cache the stock data."""
    stock_data = get_last_prices_by_all_sector()  # Assume this fetches data correctly
    cache.set('stock_data', stock_data, timeout=600)

scheduler.add_job(func=update_stock_data, trigger="interval", minutes=10)
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    stock_data_by_sector = cache.get('stock_data')
    if not stock_data_by_sector:
        flash("Stock data is currently being updated. Please try again shortly.", "info")
        return redirect(url_for('index'))

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
    return render_template('error_page.html', error_message="An error occurred.")

# Register the blueprint from the stocks module
app.register_blueprint(stocks_app, url_prefix='/stocks')

if __name__ == '__main__':
    update_stock_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
