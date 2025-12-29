from fastapi import FastAPI, Request
from fastapi.responses import Response
from yfinance import Ticker
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from middleware.wide_event import WideEventMiddleware

import logging
import uvicorn
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging to file and console
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


# -- Required for OpenTelemetry Docker Compose, Comment if not using docker -- #
# Configure OTLP exporters
# otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4318")

# # Set up trace exporter and provider
# trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
# trace_provider = TracerProvider()
# trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
# trace.set_tracer_provider(trace_provider)

# # Set up metrics exporter and provider
# metrics_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
# metrics_reader = PeriodicExportingMetricReader(metrics_exporter)
# metrics_provider = MeterProvider(metric_readers=[metrics_reader])
# metrics.set_meter_provider(metrics_provider)

# -- END -- #

# Set up OpenTelemetry tracer and meter
tracer = trace.get_tracer("investor-tracer")
meter = metrics.get_meter("investor-meter")

# For Metrics: Create a counter for health check requests
health_check_counter = meter.create_counter(
    "health_check_requests",
    description="Counts the number of health check requests"
)

app = FastAPI()
app.add_middleware(WideEventMiddleware)

stocks = json.load(open("data/stocks.json"))

@app.get("/health")
def read_root(request: Request):
    # Wide Event Approach
    result = "Service is healthy"
    user_id = '123'
    
    health_check_counter.add(1, {"value": "health_check"})
    
    # Add business context to wide_event using batch helper
    request.state.add_event_data_batch({
        "endpoint": "health",
        "result": result,
        "user_id": user_id,
        "user_name": "phil"
    })
    
    return {"status": result}

@app.get("/user/{user_id}")
def get_user(user_id: int, request: Request):
    # OTEL Approach add business context for tracing
    with tracer.start_as_current_span("get-user-span") as span:
        # Approach 1 Add user context attributes to with OTEL Tracer
        span.set_attribute("user.id", user_id)
        span.set_attribute("user.role", "standard")
        span.set_attribute("user.name", "phil")
        logger.info(f"Fetching user with ID: {user_id}")

        # # Approach 2 Add user context to wide event middleware
        # request.state.wide_event["endpoint"] = "get_user"
        # request.state.wide_event["user_id"] = user_id
        # request.state.wide_event["user_role"] = "standard"
        # request.state.wide_event["user_name"] = "phil"
    return {"user_id": user_id}

@app.get("/calculate/sum")
def calculate_sum(request: Request):
    # WIDE EVENT APPROACH
    result = 1 + 1
    logger.info(f"Calculating sum of {1} and {1}")
    request.state.add_event_data_batch({
        "endpoint": "calculate_sum",
        "operands": {"a": 1, "b": 1},
        "sum": result
    })
    return {"sum": result}

@app.get("/stock/NVDA")
def get_stock_info(request: Request):
    # OTEL Approach
    with tracer.start_as_current_span("fetch-nvda-stock-info") as span:
        ticker = Ticker("NVDA")
        info = ticker.info
        span.set_attribute("stock.symbol", "NVDA")
        span.set_attribute("stock.currentPrice", info.get("currentPrice"))
        span.set_attribute("stock.marketCap", info.get("marketCap"))
        
        # # Wide Event Approach
        # request.state.wide_event["endpoint"] = "get_stock_info"
        # request.state.wide_event["stock_symbol"] = info.get("symbol")
        # request.state.wide_event["stock_price"] = info.get("currentPrice")
        # request.state.wide_event["market_cap"] = info.get("marketCap")
    logger.info(f"Fetched stock info for NVDA: {info}")
    return {
        "symbol": info.get("symbol"),
        "shortName": info.get("shortName"),
        "currentPrice": info.get("currentPrice"),
        "marketCap": info.get("marketCap")
    }
@app.get("/stocks/{ticker}")
def get_stock_by_ticker(ticker: str, request: Request):
    # WIDE EVENT APPROACH
    with tracer.start_as_current_span("fetch-stock-info") as span:
        stock_data = stocks.get(ticker.upper())
        if not stock_data:
            logger.error(f"Stock data for ticker {ticker} not found")
            request.state.wide_event["endpoint"] = "get_stock_by_ticker"
            request.state.wide_event["stock_ticker"] = ticker
            request.state.wide_event["error"] = "Ticker not found"
            return {"error": "Ticker not found"}, 404
        span.set_attribute("stock.symbol", ticker.upper())
        request.state.wide_event["endpoint"] = "get_stock_by_ticker"
        request.state.wide_event["stock_ticker"] = ticker.upper()
        request.state.wide_event["stock_data"] = stock_data
    logger.info(f"Fetched stock data for {ticker}: {stock_data}")
    return stock_data

# OTLP endpoints (REQUIRED)
@app.post("/v1/traces")
async def traces(request: Request):
    body = await request.body()
    print(f"Traces: {len(body)} bytes")
    return Response(status_code=200)

@app.post("/v1/metrics")
async def metrics(request: Request):
    body = await request.body()
    print(f"Metrics: {len(body)} bytes")
    return Response(status_code=200)

@app.post("/v1/logs")
async def logs(request: Request):
    body = await request.body()
    print(f"Logs: {len(body)} bytes")
    return Response(status_code=200)

uvicorn.run(app, host="0.0.0.0", port=8000)