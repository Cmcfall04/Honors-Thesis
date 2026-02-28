"""S&P 500 sentiment analysis pipeline.

Identical pipeline to main.py (FinBERT scoring, technical indicators,
Experiment 1 next-day and Experiment 2 intraday logistic regression models)
applied to S&P 500 (^GSPC) data.

All output files are prefixed with 'sp500_' to keep results separate from
the Apple (AAPL) analysis.

Usage (from project root, with .venv activated):
    python scripts/main_sp500.py
"""

from pathlib import Path

# Import every function from the existing pipeline — no code duplication.
from main import (
    fetch_stock_data,
    load_historical_headlines,
    load_finbert_model,
    analyze_headlines,
    aggregate_daily_sentiment,
    merge_sentiment_with_stock,
    merge_sentiment_with_stock_intraday,
    evaluate_models_with_cv,
    train_comparison_models,
)

# ---------------------------------------------------------------------------
# S&P 500 Configuration  (overrides the AAPL defaults in main.py)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent

STOCK_SYMBOL = "^GSPC"
START_DATE   = "2024-01-01"
END_DATE     = "2024-12-31"

# Input: S&P 500 headlines produced by proquest_preprocessor.py
HISTORICAL_HEADLINES_PATH = (
    PROJECT_ROOT / "data" / "processed" / "wsj_sp500_proquest_filtered.csv"
)

# No live-scrape fallback for S&P 500 — if the ProQuest file is missing,
# the pipeline will stop with a clear error message.
HISTORICAL_HEADLINES_FALLBACK = None

# Outputs — every file is prefixed with 'sp500_'
HISTORICAL_SENTIMENT_OUTPUT = (
    PROJECT_ROOT / "results" / "sp500_historical_sentiment_analysis.csv"
)

# Experiment 1: Next-Day prediction
AGGREGATED_DATA_OUTPUT  = PROJECT_ROOT / "results" / "sp500_sentiment_stock_dataset_nextday.csv"
MODEL_COMPARISON_RESULTS = PROJECT_ROOT / "results" / "sp500_model_comparison_nextday.md"

# Experiment 2: Intraday prediction
INTRADAY_DATA_OUTPUT        = PROJECT_ROOT / "results" / "sp500_sentiment_stock_dataset_intraday.csv"
INTRADAY_COMPARISON_RESULTS = PROJECT_ROOT / "results" / "sp500_model_comparison_intraday.md"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 80)
    print("S&P 500 SENTIMENT ANALYSIS PIPELINE")
    print(f"Symbol: {STOCK_SYMBOL}  |  Period: {START_DATE} to {END_DATE}")
    print("=" * 80)

    # ── Stock data ────────────────────────────────────────────────────────
    stock_data = fetch_stock_data(STOCK_SYMBOL, START_DATE, END_DATE)

    # ── Historical sentiment: load cache or run FinBERT ───────────────────
    source_path = HISTORICAL_HEADLINES_PATH

    cache_valid = (
        HISTORICAL_SENTIMENT_OUTPUT.exists()
        and source_path.exists()
        and HISTORICAL_SENTIMENT_OUTPUT.stat().st_mtime >= source_path.stat().st_mtime
    )

    if cache_valid:
        import pandas as pd
        print(
            f"\nLoading cached S&P 500 sentiment scores from "
            f"'{HISTORICAL_SENTIMENT_OUTPUT}'..."
        )
        historical_sentiment_df = pd.read_csv(HISTORICAL_SENTIMENT_OUTPUT)
        historical_sentiment_df["date"] = pd.to_datetime(
            historical_sentiment_df["date"], errors="coerce"
        )
        print(
            f"Loaded {len(historical_sentiment_df)} cached records. "
            "Skipping FinBERT re-scoring."
        )
    else:
        if not source_path.exists():
            raise FileNotFoundError(
                f"S&P 500 headlines file not found: {source_path}\n"
                "Run 'python scripts/proquest_preprocessor.py' first."
            )

        historical_headlines_df = load_historical_headlines(source_path)
        historical_records = (
            historical_headlines_df.to_dict("records")
            if not historical_headlines_df.empty
            else []
        )
        tokenizer, model = load_finbert_model()
        historical_sentiment_df = analyze_headlines(
            historical_records,
            tokenizer,
            model,
            source_label="historical S&P 500 headlines",
        )
        if not historical_sentiment_df.empty:
            print("\nSentiment Analysis Summary (S&P 500 Headlines):")
            print(
                historical_sentiment_df[
                    ["date", "headline", "sentiment", "positive", "negative", "neutral"]
                ].head()
            )
            HISTORICAL_SENTIMENT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            historical_sentiment_df.to_csv(HISTORICAL_SENTIMENT_OUTPUT, index=False)
            print(
                f"\nCached S&P 500 sentiment scores saved to "
                f"'{HISTORICAL_SENTIMENT_OUTPUT}'"
            )

    daily_sentiment_df = aggregate_daily_sentiment([historical_sentiment_df])

    # ── Experiment 1: Next-Day Prediction ────────────────────────────────
    print("\n" + "=" * 80)
    print("EXPERIMENT 1 (S&P 500): NEXT-DAY PREDICTION")
    print("Target:   Will tomorrow's close be higher than today's close?")
    print("Features: same-day sentiment + same-day technical indicators")
    print("=" * 80)

    merged_nextday = merge_sentiment_with_stock(daily_sentiment_df, stock_data)
    if not merged_nextday.empty:
        columns_to_export_nextday = [
            "date",
            "avg_positive",
            "avg_negative",
            "avg_neutral",
            "headline_count",
            "close",
            "next_close",
            "stock_move_nextday",
            "return_1d",
            "price_vs_sma20",
            "rsi_change",
        ]
        AGGREGATED_DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        merged_nextday[columns_to_export_nextday].to_csv(
            AGGREGATED_DATA_OUTPUT, index=False
        )
        print(f"\nNext-day dataset saved to '{AGGREGATED_DATA_OUTPUT}'")

        cv_results_nextday = evaluate_models_with_cv(
            merged_nextday,
            target_column="stock_move_nextday",
            prediction_type="Next-Day (S&P 500)",
            n_splits=5,
        )

        train_comparison_models(
            merged_nextday,
            MODEL_COMPARISON_RESULTS,
            MODEL_COMPARISON_RESULTS,   # placeholder; individual CMs use cm_suffix
            target_column="stock_move_nextday",
            prediction_type="Next-Day (S&P 500)",
            cv_results=cv_results_nextday,
            cm_suffix="sp500_nextday",
        )
    else:
        print("Next-day dataset was not generated.")

    # ── Experiment 2: Intraday Prediction ────────────────────────────────
    print("\n" + "=" * 80)
    print("EXPERIMENT 2 (S&P 500): INTRADAY PREDICTION")
    print("Target:   Will today's close be higher than today's open?")
    print("Features: same-day sentiment + overnight gap + at-open technical indicators")
    print("=" * 80)

    merged_intraday = merge_sentiment_with_stock_intraday(
        daily_sentiment_df, stock_data
    )
    if not merged_intraday.empty:
        columns_to_export_intraday = [
            "date",
            "avg_positive",
            "avg_negative",
            "avg_neutral",
            "headline_count",
            "open",
            "close",
            "stock_move_intraday",
            "overnight_gap",
            "open_vs_sma20",
            "rsi_change_lag1",
        ]
        INTRADAY_DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        merged_intraday[columns_to_export_intraday].to_csv(
            INTRADAY_DATA_OUTPUT, index=False
        )
        print(f"\nIntraday dataset saved to '{INTRADAY_DATA_OUTPUT}'")

        cv_results_intraday = evaluate_models_with_cv(
            merged_intraday,
            target_column="stock_move_intraday",
            prediction_type="Intraday (S&P 500)",
            n_splits=5,
            technical_features=["overnight_gap", "open_vs_sma20", "rsi_change_lag1"],
        )

        train_comparison_models(
            merged_intraday,
            INTRADAY_COMPARISON_RESULTS,
            INTRADAY_COMPARISON_RESULTS,  # placeholder; individual CMs use cm_suffix
            target_column="stock_move_intraday",
            prediction_type="Intraday (S&P 500)",
            cv_results=cv_results_intraday,
            technical_features=["overnight_gap", "open_vs_sma20", "rsi_change_lag1"],
            cm_suffix="sp500_intraday",
        )
    else:
        print("Intraday dataset was not generated.")

    print("\n" + "=" * 80)
    print("S&P 500 PIPELINE COMPLETE")
    print("Results saved to results/sp500_*")
    print("=" * 80)


if __name__ == "__main__":
    main()
