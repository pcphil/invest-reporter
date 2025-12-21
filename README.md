# invest-reporter
Agents to provide aggregate info on stock
\n+## Quickstart
\n+### 1) Create a virtual environment (Windows)
```bash
python -m venv .venv
.venv\\Scripts\\activate
```
\n+### 2) Install dependencies
```bash
pip install -r requirements.txt
```
\n+### 3) Fetch historical data and save to CSV
```bash
python main.py --ticker AAPL --period 1y --interval 1d --out data\\AAPL_1y_1d.csv
```
\n+Flags:
- **--ticker**: symbol, e.g. `AAPL`
- **--period**: range like `1mo`, `3mo`, `6mo`, `1y`, `5y`, `max` (default: `1y`)
- **--interval**: `1d`, `1h`, `5m`, etc. (depends on period; default: `1d`)
- **--adjusted**: use adjusted prices (dividends/splits applied)
- **--out**: custom output path; defaults to `data/{TICKER}_{period}_{interval}.csv`
\n+The CSV includes a `Ticker` column and `ReturnPct` computed from the `Close` price.
