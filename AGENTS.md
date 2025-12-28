# Invest-Reporter Agents Documentation

## Overview
FastAPI service for real-time stock data aggregation via yfinance. Foundation for AI agents.

## Endpoints

| Endpoint | Method | Purpose | Params |
|----------|--------|---------|--------|
| `/health` | GET | Service status | — |
| `/calculate/sum` | GET | Arithmetic operation | `a`, `b` (float) |
| `/stock/{ticker}` | GET | Stock info (price, cap, name) | `ticker_symbol` (str) |

**Response**: JSON with symbol, shortName, currentPrice, marketCap

## Setup
```bash
python -m venv venv
.\venv\Scripts\activate
pip install fastapi yfinance uvicorn
uvicorn main:app --reload  # Run at http://localhost:8000
```

## Dependencies
- **FastAPI**: REST framework
- **yfinance**: Yahoo Finance API
- **uvicorn**: ASGI server

## Planned Agents

1. **Stock Analysis**: Multi-stock comparison, P/E, dividend yield, recommendations
2. **Portfolio**: Allocation tracking, rebalancing suggestions
3. **Market Intelligence**: Sector trends, market alerts
4. **Financial Reports**: Historical trends, sentiment analysis, predictions

## Configuration
Optional `.env` variables:
- `OPENAI_API_KEY` - For AI analysis
- `STOCK_DATA_CACHE_TTL` - Cache duration (default: 300s)
- `MAX_STOCKS_PER_QUERY` - Rate limit (default: 10)

## Testing
```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/calculate/sum?a=10&b=20"
curl "http://localhost:8000/stock/AAPL"
```

## Enhancements
- Add caching for stock data
- Implement rate limiting & auth
- Error status codes (400, 404, 500)
- Async batch ticker processing
- Database for historical data
- CORS configuration

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Modules missing | `pip install -r requirements.txt` |
| Port in use | `uvicorn main:app --port 8001` |
| yfinance timeout | Check internet; add retry logic |
| Invalid ticker | Verify on Yahoo Finance |
