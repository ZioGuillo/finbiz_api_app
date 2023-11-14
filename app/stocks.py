
from flask import Blueprint, jsonify, render_template, request
from finbiz import analyze_stock, process_stock_data


stocks_app = Blueprint('stocks_app', __name__)

@stocks_app.route('/')
def home():
    return "Welcome to the Stock Analysis App"  # Later, you'll replace this with a call to render your homepage template

@stocks_app.route('/data', methods=['GET'])
def get_stock():
    # Get the stock symbol from query parameters
    symbol = request.args.get('symbol', None)

    if not symbol:
        return jsonify({'error': 'No symbol provided'}), 400

    processed_stock_data = process_stock_data(symbol)
    return jsonify(processed_stock_data)

@stocks_app.route('/visualize')
def visualize_data():
    # Code to display data
    return render_template('visualize.html', data=processed_data)

@stocks_app.route('/analyze', methods=['GET'])
def analyze():
    symbol = request.args.get('symbol', None)
    if not symbol:
        return jsonify({'error': 'No symbol provided'}), 400

    # Fetch stock data using your existing method
    stock_data = process_stock_data(symbol)

    # Analyze the stock
    analysis_results = analyze_stock(stock_data)

    return jsonify(analysis_results)