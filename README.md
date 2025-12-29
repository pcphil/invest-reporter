# Invest-Reporter

A FastAPI-based service for real-time stock data aggregation using yfinance. This project provides a foundation for building AI agents that analyze financial data and stock information.

## Features

- **Stock Data Retrieval**: Fetch real-time stock information including price, market cap, and company name
- **Arithmetic Operations**: Basic calculate endpoint for testing
- **Health Check**: Service status monitoring
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation

## Project Structure

```
invest-reporter/
├── api.py              # Main FastAPI application
├── requirements.txt    # Project dependencies
├── AGENTS.md          # Planned AI agents documentation
├── README.md          # This file
├── LICENSE            # Project license
└── venv/              # Virtual environment
```

## Endpoints

| Endpoint | Method | Purpose | Parameters | Response |
|----------|--------|---------|-----------|----------|
| `/health` | GET | Service health check | — | `{"Hello": "World"}` |
| `/calculate/sum` | GET | Sum two numbers | `a`, `b` (float) | `{"sum": result}` |
| `/stock/{ticker_symbol}` | GET | Get stock information | `ticker_symbol` (str) | `{"symbol", "shortName", "currentPrice", "marketCap"}` |

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

Start the development server:
```bash
python api.py
```

The API will be available at `http://localhost:8000`

Access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Testing Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Calculate Sum:**
```bash
curl "http://localhost:8000/calculate/sum?a=10&b=20"
```

**Stock Information:**
```bash
curl "http://localhost:8000/stock/AAPL"
```
## Open Telemetry Setup
### Windows Local Tracing
```
set OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
set OTEL_PYTHON_LOG_LEVEL=debug
set PYTHONUNBUFFERED="1"
opentelemetry-instrument --traces_exporter console --metrics_exporter console --logs_exporter console --service_name investor python api.py
```

### Docker Compose Collection

# From your-project/ directory
docker compose -f otel-compose.yml up -d

# Check logs
docker compose -f otel-compose.yml logs -f otel-collector

# Test connectivity to your API from container
docker compose -f otel-compose.yml exec otel-collector curl http://host.docker.internal:8000/health

## Dependencies

- **fastapi** - Modern Python web framework for building APIs
- **yfinance** - Yahoo Finance API wrapper for fetching stock data
- **opentelemetry-distro** - Observability and monitoring

See [requirements.txt](requirements.txt) for the complete list.

## Planned Features

Refer to [AGENTS.md](AGENTS.md) for documentation on planned AI agents including:
- Stock Analysis Agent
- Portfolio Management Agent
- Market Intelligence Agent
- Financial Reports Agent

## Configuration

Environment variables (optional):
- `OPENAI_API_KEY` - For AI analysis features
- `STOCK_DATA_CACHE_TTL` - Cache duration in seconds (default: 300)
- `MAX_STOCKS_PER_QUERY` - Maximum stocks per request (default: 10)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module import errors | Ensure virtual environment is activated and all dependencies are installed: `pip install -r requirements.txt` |
| Port 8000 already in use | Change port in `api.py` or use: `python -m uvicorn api:app --port 8001` |
| yfinance timeout | Check internet connection and verify ticker symbols are valid on Yahoo Finance |
| Invalid ticker symbol | Verify the ticker exists on [Yahoo Finance](https://finance.yahoo.com) |

## Development

To use a different port:
```bash
python -m uvicorn api:app --port 8001 --reload
```

The `--reload` flag enables auto-restart when code changes are detected.

## License

See [LICENSE](LICENSE) file for details.

## Next Steps

- Implement caching for stock data to improve performance
- Add request validation and error handling (400, 404, 500 status codes)
- Implement rate limiting and authentication
- Add async batch processing for multiple tickers
- Set up database for historical data storage
- Configure CORS for frontend integration
