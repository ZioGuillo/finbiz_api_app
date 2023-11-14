import time
from flask import Flask, request, jsonify
from stocks import stocks_app
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Initialize metrics
metrics = PrometheusMetrics(app)

# Optional: Add some default metrics for all requests
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    metrics.histogram('flask_request_latency_seconds', 'Flask Request Latency',
                      buckets=[0.1, 0.2, 0.5, 1, 2, 5]).observe(request_latency)
    return response

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