import time
from flask import Flask, request, jsonify
from stocks import stocks_app
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Initialize metrics
metrics = PrometheusMetrics(app) # export metrics to /metrics endpoint
metrics.info('app_info', 'Application info', version='1.0.3', app_name='app_api_streaming')

@app.route('/')
def hello_world():
    data = b'Hello, World!'
    status = '200 OK'
    response_headers = [
      ('Content-type', 'text/plain'),
      ('Content-Length', str(len(data)))
    ]
    return data, status, response_headers

@app.get('/health')
def health():
    return {"status" : "UP"}

# Stocks Functions

# Register the blueprint from the stocks module
app.register_blueprint(stocks_app, url_prefix='/stocks')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)