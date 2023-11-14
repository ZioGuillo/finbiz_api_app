
from flask import Blueprint, jsonify, render_template, request
from finbiz import analyze_stock, process_stock_data


stocks_app = Blueprint('stocks_app', __name__)

@stocks_app.route('/')
def home():
    return render_template('index.html', data=None)

@stocks_app.route('/data', methods=['GET'])
def get_stock():
    # Get the stock symbol from query parameters
    symbol = request.args.get('symbol', None)

    if not symbol:
        return jsonify({'error': 'No symbol provided'}), 400

    processed_stock_data = process_stock_data(symbol)
    return jsonify(processed_stock_data)

@stocks_app.route('/analyze', methods=['GET'])
def analyze_data():
    symbol = request.args.get('symbol', None)
    if symbol:
        processed_data = process_stock_data(symbol)
        analyzed_data = analyze_stock(processed_data)
        print(analyzed_data)  # Debugging line to check data structure
        return render_template('index.html', data=analyzed_data, symbol=symbol)
    return render_template('index.html', data=None, symbol=None)
