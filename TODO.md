# 📌 Thesis Project To-Do List

This document tracks improvements and next steps for the Apple Stock Sentiment Analysis tool (`main.py`).  
Goal: Build a complete pipeline from **headlines → sentiment → daily features → stock movement prediction**.

---

## ✅ Completed
- [x] Downloaded stock data using `yfinance`.
- [x] Scraped Apple-related headlines from Yahoo Finance.
- [x] Filtered headlines with Apple-specific keywords.
- [x] Ran FinBERT sentiment analysis on headlines.
- [x] Saved results (headline + sentiment scores) to `apple_sentiment_analysis.csv`.
- [x] Documented process in `README.md`.

---

## 🔄 To-Do (Next Steps)

### 1. Data Collection Improvements
- [ ] **Add headline dates**  
  - Parse `<time>` elements from Yahoo Finance (if available).  
  - If not available, fallback = current scrape date (less accurate).  
  - Store alongside headlines in DataFrame.  

- [ ] **Handle empty headline cases gracefully**  
  - Already partially covered with `apple_headlines = []`.  
  - Expand to log when no data is found and retry scraping.  

- [ ] **Integrate Historical Headlines**  
  - Explore sources to move beyond "current headlines only":
    - **Kaggle datasets**: e.g., *Financial News for Stock Prediction*, *Stock Market News Dataset*.  
    - **NewsAPI** (free tier, allows limited historical queries).  
    - **Alpha Vantage News API** (check free tier).  
    - **University library subscriptions**: Factiva, ProQuest, Bloomberg, WSJ.  
  - Download or query headlines covering at least **6–12 months**.  
  - Standardize data format into:  
    ```
    Date | Headline
    ```
  - Run FinBERT sentiment analysis on this dataset (batch processing).
  - Merge with stock price data (`yfinance`) across the same date range.

---

### 2. Data Processing
- [ ] **Aggregate daily sentiment scores**  
  - Group headlines by date.  
  - Compute average positive, negative, and neutral scores per day.  
  - Example schema:  
    ```
    Date | Avg_Positive | Avg_Negative | Avg_Neutral
    ```

- [ ] **Merge with stock data**  
  - Align daily sentiment with `yfinance` daily close prices.  
  - Create label `Stock_Move`:  
    - `1` if next-day close > today’s close.  
    - `0` otherwise.  

- [ ] **Export merged dataset**  
  - Save as `sentiment_stock_dataset.csv`.  
  - Columns:  
    ```
    Date | Avg_Positive | Avg_Negative | Avg_Neutral | Stock_Move
    ```

---

### 3. Modeling
- [ ] **Build first baseline classifier**  
  - Use `LogisticRegression` from scikit-learn.  
  - Features: `[Avg_Positive, Avg_Negative, Avg_Neutral]`.  
  - Label: `Stock_Move`.  

- [ ] **Evaluate model performance**  
  - Accuracy score.  
  - Precision, Recall, F1-score.  
  - Confusion matrix.  
  - Compare against baseline (random 50/50 guess).  

- [ ] **Save results**  
  - Export metrics to a `results.md` or `results.csv` file.  
  - Visualize confusion matrix with `matplotlib`.  

---

### 4. Enhancements (Future Phases)
- [ ] **Support multiple tickers** (AAPL, MSFT, AMZN, etc.).  
- [ ] **Add simple technical indicators** (e.g., moving averages, RSI, trading volume).  
- [ ] **Run experiments**  
  - Sentiment-only vs. Sentiment+Technical Indicators.  
  - Different lookahead windows (same-day vs. next-day vs. 2-day).  
- [ ] **Error handling + logging**  
  - Log failed scrapes.  
  - Add retries for HTTP errors.  

---

## 📝 Notes for Thesis Write-Up
- Justify use of **headlines (not full articles)** as main sentiment source.  
- Acknowledge limitations (scraping instability, noise, small data volume).  
- Propose **full-article analysis + premium datasets** as future work.  
- Document baseline model setup and evaluation clearly for reproducibility.  

---
