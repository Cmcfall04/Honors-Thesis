# 📌 WSJ Data Pipeline for Thesis Project

This document explains how to collect, process, and analyze **Wall Street Journal (WSJ)** data (via ProQuest) for predicting short-term stock market movements using sentiment analysis and stock price data.

---

## 1. Why WSJ via ProQuest?

- ✅ High-quality, business-focused publication.  
- ✅ Historical depth back to 1984 through ProQuest.  
- ✅ Easy export in CSV/Excel format → structured, reproducible dataset.  
- ✅ Strong academic credibility (widely respected and citable).  

For this project, **WSJ via ProQuest** will serve as the **sole primary dataset**.

---

## 2. Collecting WSJ Data from ProQuest

### Step 1: Search
1. Open **ProQuest** and go to **Advanced Search**.  
2. Select **Wall Street Journal (Publication title)** as the source.  
3. Use Boolean queries for Apple-related content:  
4. Apply a **date range** (e.g., last 12 months).  

### Step 2: Export
1. Export search results in **CSV/Excel** format.  
2. Include fields:  


⚠️ ProQuest may limit bulk exports (e.g., 100–500 records per batch). Export multiple batches and merge them if needed.

---

## 3. Pipeline Implementation

The pipeline has five main stages, now **fully automated** in the codebase:

### Stage 1: Preprocess ProQuest Data
**Script:** `proquest_preprocessor.py`

1. Place your ProQuest CSV export(s) in the `data/` directory
2. Run the preprocessor:
   ```bash
   python proquest_preprocessor.py
   ```
3. The script will:
   - Automatically detect ProQuest export files (proquest*.csv, wsj*.csv, export*.csv)
   - Merge multiple batches if you exported in chunks
   - Standardize column names (Date → date, Title → headline)
   - Remove duplicates and invalid dates
   - Output cleaned file: `data/wsj_apple_proquest.csv`

**Accepted ProQuest Column Names:**
- Date columns: "Publication Date", "Date", "Pub Date", "Published"
- Title columns: "Title", "Headline", "Article Title"

---

### Stage 2: Sentiment Analysis
**Script:** `main.py` (automated)

- Loads `data/wsj_apple_proquest.csv`
- Applies **FinBERT** model to each headline
- Outputs sentiment scores: **positive, negative, neutral**
- Saves to: `historical_sentiment_analysis.csv`

---

### Stage 3: Aggregate Daily Sentiment
**Script:** `main.py` (automated)

- Groups headlines by **Date**
- Computes **average positive, negative, and neutral sentiment** per day
- Counts number of headlines per day
- Output format:
  ```
  date, avg_positive, avg_negative, avg_neutral, headline_count
  ```

---

### Stage 4: Merge with Stock Price Data
**Script:** `main.py` (automated)

- Downloads AAPL stock data for 2024 via `yfinance`
- Merges with sentiment data on **Date**
- Creates classification label:
  - `stock_move = 1` if next day's close > today's close
  - `stock_move = 0` otherwise
- Saves to: `sentiment_stock_dataset.csv`

---

### Stage 5: Build Baseline Model
**Script:** `main.py` (automated)

- Trains **Logistic Regression** classifier
- Input features: `avg_positive, avg_negative, avg_neutral`
- Target label: `stock_move`
- 70/30 train-test split (stratified)
- Evaluation metrics:
  - Accuracy, Precision, Recall, F1-score
  - Confusion matrix visualization
- Outputs:
  - `model_results.md` - Text metrics
  - `confusion_matrix.png` - Visual matrix

---

## 3.1 Complete Workflow

```bash
# Step 1: Export WSJ data from ProQuest (manual)
# Save CSV file(s) to data/ directory

# Step 2: Preprocess ProQuest exports
python proquest_preprocessor.py

# Step 3: Run full pipeline
python main.py
```

The pipeline will automatically:
- Load ProQuest data
- Download 2024 AAPL stock prices
- Score all headlines with FinBERT
- Aggregate daily sentiment
- Merge with stock data
- Train and evaluate baseline model
- Generate visualizations and results  

---

## 4. Extensions (Future Work)

- Expand analysis to other companies (e.g., Microsoft, Amazon).  
- Add **technical indicators** (moving averages, RSI, volume) alongside sentiment features.  
- Experiment with additional models (e.g., Random Forest, XGBoost).  
- Test different lookahead windows (same-day vs. next-day vs. two-day movements).  
- Compare different time ranges (short-term vs. long-term).  

---
