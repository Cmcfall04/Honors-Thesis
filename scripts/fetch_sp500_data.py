"""Fetch S&P 500 (^GSPC) stock data for Jan 2024 - Dec 2024.

Downloads OHLCV data via yfinance — same method used for AAPL in the
main pipeline — and saves to results/sp500_stock_data.csv.

Usage (from scripts/ or project root):
    python scripts/fetch_sp500_data.py
"""

from pathlib import Path
import pandas as pd
import yfinance as yf

PROJECT_ROOT = Path(__file__).parent.parent

SYMBOL    = "^GSPC"
START     = "2024-01-01"
END       = "2024-12-31"
OUT_PATH  = PROJECT_ROOT / "results" / "sp500_stock_data.csv"


def fetch_sp500() -> None:
    print(f"Downloading {SYMBOL} stock data from {START} to {END}...")
    data = yf.download(SYMBOL, start=START, end=END)

    if data.empty:
        print("ERROR: received empty dataset. Check ticker symbol and date range.")
        return

    # Flatten MultiIndex columns that yfinance sometimes returns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if isinstance(col, tuple) else col
                        for col in data.columns.to_list()]

    print(f"\nDownloaded {len(data)} trading days")
    print(f"Columns : {list(data.columns)}")
    print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}")
    print("\nFirst 5 rows:")
    print(data.head())
    print("\nLast 5 rows:")
    print(data.tail())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUT_PATH)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    fetch_sp500()
