 import argparse
 from pathlib import Path
 from typing import Optional
 import sys

 import pandas as pd
 import yfinance as yf


 def fetch_history(
     ticker: str,
     period: str = "1y",
     interval: str = "1d",
     auto_adjust: bool = False,
 ) -> pd.DataFrame:
     """Fetch historical price data for a ticker using yfinance.

     Returns a DataFrame with a DatetimeIndex and adds convenience columns.
     """
     if not ticker:
         raise ValueError("ticker must be provided")

     history = yf.Ticker(ticker).history(
         period=period,
         interval=interval,
         auto_adjust=auto_adjust,
     )

     if history.empty:
         raise RuntimeError(
             f"No data returned for {ticker} (period={period}, interval={interval})."
         )

     # Ensure index is named and accessible when saving
     history.index.name = "Date"
     history["Ticker"] = ticker
     # Simple daily return percentage based on Close price
     if "Close" in history.columns:
         history["ReturnPct"] = history["Close"].pct_change() * 100.0

     return history


 def save_dataframe_to_csv(df: pd.DataFrame, output_path: Path) -> None:
     """Save DataFrame to CSV, creating parent directories as needed."""
     output_path.parent.mkdir(parents=True, exist_ok=True)
     df.to_csv(output_path)


 def build_default_output_path(
     ticker: str, period: str, interval: str, directory: Optional[Path] = None
 ) -> Path:
     directory = directory or Path("data")
     filename = f"{ticker.upper()}_{period}_{interval}.csv"
     return directory / filename


 def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
     parser = argparse.ArgumentParser(
         description="Fetch historical market data with yfinance and save as CSV",
     )
     parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
     parser.add_argument(
         "--period",
         default="1y",
         help="Data period (e.g. 1mo, 3mo, 6mo, 1y, 5y, max)",
     )
     parser.add_argument(
         "--interval",
         default="1d",
         help="Sampling interval (e.g. 1d, 1h, 5m). Depends on period.",
     )
     parser.add_argument(
         "--adjusted",
         action="store_true",
         help="Use adjusted prices (yfinance auto_adjust).",
     )
     parser.add_argument(
         "--out",
         default=None,
         help="Output CSV path. Defaults to data/{TICKER}_{period}_{interval}.csv",
     )
     return parser.parse_args(argv)


 def main(argv: Optional[list[str]] = None) -> int:
     args = parse_args(argv)

     output_path = (
         Path(args.out)
         if args.out
         else build_default_output_path(args.ticker, args.period, args.interval)
     )

     try:
         df = fetch_history(
             ticker=args.ticker,
             period=args.period,
             interval=args.interval,
             auto_adjust=args.adjusted,
         )
         save_dataframe_to_csv(df, output_path)
     except Exception as exc:
         print(f"Error: {exc}", file=sys.stderr)
         return 1

     print(
         f"Saved {len(df):,} rows for {args.ticker.upper()} to {output_path.as_posix()}"
     )
     return 0


 if __name__ == "__main__":
     raise SystemExit(main())


