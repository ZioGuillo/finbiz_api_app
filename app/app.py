import os
import secrets
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, Response, flash
from flask_cors import CORS
from flask_session import Session
from prometheus_flask_exporter import PrometheusMetrics
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv

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
    return render_template('index.html')

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
    app.run(host='0.0.0.0', port=5000, debug=False)
