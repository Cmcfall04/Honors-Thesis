# S&P 500 Sentiment Analysis Pipeline — Methodology

This document explains how the S&P 500 results were produced, from raw data
collection through model evaluation.

---

## 1. Data Collection

### 1.1 Headlines — ProQuest / Wall Street Journal

WSJ articles mentioning the S&P 500 for the full calendar year 2024 were
exported from the ProQuest database as CSV files in three separate batches:

| File | Coverage |
|------|----------|
| `data/raw/S&P_firstbatch.csv` | Early 2024 |
| `data/raw/S&P_secondbatch.csv` | Mid 2024 |
| `data/raw/S&P_thirdbatch.csv` | Late 2024 |

### 1.2 Stock Price Data — Yahoo Finance

Daily OHLCV (Open, High, Low, Close, Volume) data for the S&P 500 index
(`^GSPC`) was downloaded via `yfinance` for the period **2024-01-01 to
2024-12-31**.

---

## 2. Preprocessing

### 2.1 Merging Batches (`scripts/proquest_preprocessor.py`)

The three raw CSVs were merged into a single dataset. During this step the
script:

- Tried multiple encodings (`utf-8`, `latin-1`, `cp1252`, `iso-8859-1`) to
  handle ProQuest export quirks.
- Inferred the date and headline columns by name matching.
- Standardized both columns to `date` (YYYY-MM-DD) and `headline`.
- Dropped rows with missing or empty headlines.
- Parsed and validated all dates, dropping any that could not be parsed.
- Removed duplicate `(date, headline)` pairs.
- Sorted by date.

**Output:** `data/processed/wsj_sp500_proquest.csv` — **984 headlines** across
**232 unique dates**.

### 2.2 Leakage Filtering (`scripts/filter_sp500_headlines.py`)

S&P 500 headline data requires a filtering step to remove articles that
**reveal the same-day market outcome**. Keeping these would allow the model to
train on information that was not available before market open — a form of
data leakage.

Two categories of headlines were removed:

**Category A — Daily market-recap prefixes** (removed unconditionally):

- `"Stock market today: …"`
- `"Wall Street today: …"`
- `"Markets & Finance -- Monday's Markets: …"` (and other weekdays)
- `"Markets -- Wednesday's Markets: …"` etc.
- `"Exchange --- Friday's Markets: …"` etc.

**Category B — Same-day outcome phrases** linked to the S&P 500, Dow, or
Nasdaq (e.g. *"S&P 500 rose"*, *"Nasdaq fell"*, *"Wall Street surged"*).

A **safe-phrase whitelist** prevented over-filtering: headlines containing
forward-looking language (`could`, `would`, `might`, `forecast`, `analysts
say`, `outlook`, etc.) were retained even if they contained an outcome verb,
because they reflect pre-market analysis rather than revealed results.

**Results of filtering:**

| | Count |
|---|---|
| Headlines before filtering | 984 |
| Headlines removed (leakage) | 150 |
| **Headlines retained** | **834** |
| Unique dates retained | 214 |

Removed headlines were saved separately for inspection:
`data/processed/wsj_sp500_removed_headlines.csv`.

**Output:** `data/processed/wsj_sp500_proquest_filtered.csv`

---

## 3. Sentiment Scoring — FinBERT

Each headline in the filtered dataset was scored using **FinBERT**
(`yiyanghkust/finbert-tone`), a BERT model fine-tuned on financial text.
FinBERT outputs three probability scores per headline:

| Score | Meaning |
|---|---|
| `positive` | Probability the headline conveys positive financial sentiment |
| `negative` | Probability the headline conveys negative financial sentiment |
| `neutral` | Probability the headline is neutral |

The label assigned is whichever class has the highest probability.

**Output:** `results/sp500_historical_sentiment_analysis.csv` — one row per
headline with date, headline text, label, and all three probability scores.
This file is used as a cache: if it is newer than the input CSV, FinBERT is
not re-run.

---

## 4. Feature Engineering

### 4.1 Daily Sentiment Aggregation

Headlines were grouped by date and averaged to produce one row per trading day:

| Feature | Derivation |
|---|---|
| `avg_positive` | Mean positive score across all headlines that day |
| `avg_negative` | Mean negative score across all headlines that day |
| `avg_neutral` | Mean neutral score across all headlines that day |
| `headline_count` | Number of headlines that day |

### 4.2 Technical Indicators

Three momentum-based technical indicators were computed from the daily close
prices (Wilder's smoothed EMA used for RSI, consistent with standard financial
data terminals):

| Feature | Definition |
|---|---|
| `return_1d` | Daily percentage change in close price |
| `price_vs_sma20` | `(Close − SMA₂₀) / SMA₂₀` — position relative to 20-day moving average |
| `rsi_change` | Day-over-day change in RSI₁₄ (momentum acceleration) |

---

## 5. Experiments

Both experiments used **logistic regression** with `class_weight='balanced'`
(to prevent collapse to the majority class) and **StandardScaler**
normalization applied independently to each feature set.

Three models were compared in each experiment:

| Model | Features |
|---|---|
| **Technical Only** | `return_1d`, `price_vs_sma20`, `rsi_change` |
| **Sentiment Only** | `avg_positive`, `avg_negative`, `avg_neutral` |
| **Technical + Sentiment** | All six features combined |

### Experiment 1: Next-Day Prediction

**Target:** Will tomorrow's close price be higher than today's close?

- Features: same-day sentiment + same-day technical indicators
- `next_close` was computed on the **full** consecutive stock series before the
  inner join with sentiment, so gaps in WSJ coverage do not cause the shift to
  skip actual trading days.

**Dataset:** `results/sp500_sentiment_stock_dataset_nextday.csv`
(201 rows after merging and dropping NaN from rolling windows)

**Train/Test Split (time-based, 70/30):**

| Period | Dates | Samples |
|---|---|---|
| Train | 2024-01-30 → 2024-09-30 | 140 |
| Test | 2024-10-01 → 2024-12-27 | 61 |

### Experiment 2: Intraday Prediction

**Target:** Will today's close price be higher than today's open?

- Features: same-day sentiment + **lagged** at-open technical indicators
  (computed from the prior trading day's data, so no information from the
  current session leaks in).

| Feature | Definition |
|---|---|
| `overnight_gap` | `(Open(t) − Close(t−1)) / Close(t−1)` |
| `open_vs_sma20` | `(Open(t) − SMA₂₀(t−1)) / SMA₂₀(t−1)` |
| `rsi_change_lag1` | RSI change from day t−2 to t−1 |

Lags are applied on the full stock series **before** merging with sentiment,
preserving correct temporal alignment.

**Dataset:** `results/sp500_sentiment_stock_dataset_intraday.csv`

**Train/Test Split (time-based, 70/30):**

| Period | Dates | Samples |
|---|---|---|
| Train | 2024-01-31 → 2024-10-01 | 140 |
| Test | 2024-10-02 → 2024-12-30 | 61 |

---

## 6. Evaluation

### 6.1 Time-Based Train/Test Split

The primary evaluation used a strict time-based 70/30 split (no shuffling) to
simulate realistic out-of-sample forecasting.

### 6.2 5-Fold Time-Series Cross-Validation

`TimeSeriesSplit` (scikit-learn) was also applied to get a more robust
estimate of performance across different time windows. Each fold trains on all
data before the test window.

### 6.3 McNemar's Test

Pairwise statistical significance was tested using McNemar's exact binomial
test on the same held-out test cases, assessing whether model differences
could be due to chance (threshold: p < 0.05).

---

## 7. Results

### Experiment 1: Next-Day Prediction

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| Technical Only | 47.54% | 55.56% | 42.86% | 48.39% |
| Sentiment Only | 40.98% | 48.57% | 48.57% | 48.57% |
| Technical + Sentiment | 47.54% | 55.56% | 42.86% | 48.39% |

**5-Fold CV (mean ± std):**

| Model | Accuracy |
|---|---|
| Technical Only | 49.70% ± 3.09% |
| Sentiment Only | 50.30% ± 11.27% |
| Technical + Sentiment | 47.27% ± 4.54% |

**McNemar's test:** No pairwise comparison reached significance (all p ≥ 0.05).

### Experiment 2: Intraday Prediction

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| Technical Only | 52.46% | 57.14% | 48.48% | 52.46% |
| Sentiment Only | 50.82% | 54.05% | 60.61% | 57.14% |
| Technical + Sentiment | 45.90% | 50.00% | 51.52% | 50.75% |

**5-Fold CV (mean ± std):**

| Model | Accuracy |
|---|---|
| Technical Only | 50.30% ± 4.54% |
| Sentiment Only | 50.91% ± 5.21% |
| Technical + Sentiment | 50.30% ± 8.70% |

**McNemar's test:** No pairwise comparison reached significance (all p ≥ 0.05).

### Confusion Matrices

Saved to `results/`:

- `confusion_matrix_technical_sp500_nextday.png`
- `confusion_matrix_sentiment_sp500_nextday.png`
- `confusion_matrix_combined_sp500_nextday.png`
- `confusion_matrix_technical_sp500_intraday.png`
- `confusion_matrix_sentiment_sp500_intraday.png`
- `confusion_matrix_combined_sp500_intraday.png`

---

## 8. Scripts Reference

| Script | Purpose |
|---|---|
| `scripts/proquest_preprocessor.py` | Merge and clean raw ProQuest batches |
| `scripts/filter_sp500_headlines.py` | Remove data-leakage headlines |
| `scripts/fetch_sp500_data.py` | Download `^GSPC` price data from yfinance |
| `scripts/main_sp500.py` | Run full FinBERT scoring + model pipeline |

**Execution order (from project root with `.venv` activated):**

```powershell
python scripts/proquest_preprocessor.py
python scripts/filter_sp500_headlines.py
python scripts/main_sp500.py
```

---

*Generated: 2026-02-28*
