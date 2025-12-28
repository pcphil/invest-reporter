from fastapi import FastAPI
from yfinance import Ticker
from opentelemetry import trace
from opentelemetry import metrics

import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Set up OpenTelemetry tracer and meter
tracer = trace.get_tracer("investor-tracer")
meter = metrics.get_meter("investor-meter")

health_check_counter = meter.create_counter(
    "health_check_requests",
    description="Counts the number of health check requests"
)


app = FastAPI()

@app.get("/health")
def read_root():
    result = "Service is healthy"
    with tracer.start_as_current_span("health-check-span"):
        logger.info("Health check endpoint called")
        health_check_counter.add(1, {"value": "health_check"})
    return {"status": result}
@app.get("/calculate/sum")
def calculate_sum(a: float, b: float):

    logger.info(f"Calculating sum of {a} and {b}")
    return {"sum": a + b}

@app.get("/stock/NVDA")
def get_stock_info():
    with tracer.start_as_current_span("fetch-nvda-stock-info"):
        ticker = Ticker("NVDA")
        info = ticker.info
    logger.info(f"Fetched stock info for NVDA: {info}")
    return {
        "symbol": info.get("symbol"),
        "shortName": info.get("shortName"),
        "currentPrice": info.get("currentPrice"),
        "marketCap": info.get("marketCap")
    }

uvicorn.run(app, host="0.0.0.0", port=8000)