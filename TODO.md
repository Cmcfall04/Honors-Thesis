# Thesis Project To-Do List

This document tracks improvements and next steps for the Apple Stock Sentiment Analysis tool (`main.py`).
Goal: Build a complete pipeline from **headlines + sentiment + daily features + stock movement prediction**.

---

## Completed
- [x] Downloaded stock data using `yfinance`.
- [x] Scraped Apple-related headlines from Yahoo Finance.
- [x] Filtered headlines with Apple-specific keywords.
- [x] Ran FinBERT sentiment analysis on headlines.
- [x] Saved results (headline + sentiment scores) to `apple_sentiment_analysis.csv`.
- [x] Documented process in `README.md`.

---

## To-Do (Next Steps)

### 1. Data Collection Improvements
- [x] Add headline dates
  - Parse `<time>` elements from Yahoo Finance when possible.
  - Fallback to current scrape date when `<time>` is unavailable.
  - Store alongside headlines in DataFrame (implemented in `main.py`).
- [x] Handle empty headline cases gracefully
  - Added multi-attempt scrape retries with logging when no data is found.
  - Exits cleanly after the configured retry count.
- [ ] Integrate historical headlines
  - [x] Seeded `data/historical_headlines.csv` with 2025 sample headlines.
  - [x] Automated FinBERT batch sentiment scoring to `historical_sentiment_analysis.csv`.
  - [ ] Acquire extended historical headline source (Kaggle, NewsAPI, Alpha Vantage, library DBs).
  - [ ] Merge with stock price data (`yfinance`) across the same date range once a real dataset is sourced.

---

### 2. Data Processing
- [x] Aggregate daily sentiment scores
  - Combined live + historical sentiment into daily averages with headline counts.
  - Output preview saved to console for validation.
- [x] Merge with stock data
  - Joined daily sentiment with AAPL closes and derived the `stock_move` label (next-day close).
- [x] Export merged dataset
  - Saved as `sentiment_stock_dataset.csv` including averages, headline counts, close prices, and labels.

---

### 3. Modeling
- [x] Build first baseline classifier
  - Trained `LogisticRegression` on `[Avg_Positive, Avg_Negative, Avg_Neutral]` features.
- [x] Evaluate model performance
  - Logged accuracy, precision, recall, F1, and confusion matrix metrics.
- [x] Save results
  - Exported metrics to `model_results.md` and confusion matrix to `confusion_matrix.png`.

---

### 4. Enhancements (Future Phases)
- [ ] Support multiple tickers (AAPL, MSFT, AMZN, etc.).
- [ ] Add simple technical indicators (e.g., moving averages, RSI, trading volume).
- [ ] Run experiments
  - Sentiment-only vs. Sentiment+Technical Indicators.
  - Different lookahead windows (same-day vs. next-day vs. 2-day).
- [ ] Error handling + logging
  - Log failed scrapes.
  - Add retries for HTTP errors.

---

## Notes for Thesis Write-Up
- Justify use of **headlines (not full articles)** as main sentiment source.
- Acknowledge limitations (scraping instability, noise, small data volume).
- Propose **full-article analysis + premium datasets** as future work.
- Document baseline model setup and evaluation clearly for reproducibility.
