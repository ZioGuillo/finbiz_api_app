import time
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS  # Import CORS
from flask_session import Session  # You might need to install flask-session
# Ensure stocks_app is correctly imported from your stocks module
from stocks import stocks_app, process_stock_data, analyze_stock
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask
from flask_session import Session
import os
from dotenv import load_dotenv
import base64
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from form_tool import FormTool  # Import the YourForm class from the appropriate module
import binascii
import secrets

secret_key = secrets.token_hex(16)  # 16 bytes (128 bits) is a common length for secret keys

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

# Get allowed origins from environment variables
allowed_origins = os.getenv("ALLOWED_ORIGINS").split(",")

# Use environment variables for configuration
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'

csrf = CSRFProtect(app)

CORS(app, resources={r"/*": {"origins": allowed_origins, "send_wildcard": True}})
   
Session(app)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='0.46.0', app_name='finbiz_app')

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.get('/health')
def health():
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', '0')  # Length of an empty response
    ]
    return Response(status=status, headers=response_headers)

@app.route('/stocks/analyze', methods=['GET', 'POST'])
def display_analysis():
    
    form = FormTool()
    if form.validate_on_submit():
        symbol = form.symbol.data.upper()

    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
    else:
        symbol = request.args.get('symbol').upper() or session.get('symbol').upper()

    if not symbol:
        if request_wants_json():
            return jsonify({"error": "No symbol provided"}), 400
        else:
            return redirect(url_for('hello_world'))

    stock_data = process_stock_data(symbol)
    analysis_results = analyze_stock(stock_data)

    if request_wants_json():
        return jsonify(analysis_results)
    else:
        session['analysis_results'] = analysis_results
        session['symbol'] = symbol
        return redirect(url_for('show_analysis_results'))

@app.route('/stocks/results')
def show_analysis_results():
    analysis_results = session.get('analysis_results')
    symbol = session.get('symbol')
    return render_template('analysis_results.html', results=analysis_results, symbol=symbol)

# Generate CSRF token for inclusion in the form
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

def request_wants_json():
    """Determine if the request prefers JSON."""
    json_mimetype = 'application/json'
    html_mimetype = 'text/html'
    best = request.accept_mimetypes.best_match([json_mimetype, html_mimetype])
    return best == json_mimetype and \
           request.accept_mimetypes[best] > request.accept_mimetypes[html_mimetype]


# Register the blueprint from the stocks module
app.register_blueprint(stocks_app, url_prefix='/stocks')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
