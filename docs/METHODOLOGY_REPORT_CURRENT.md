# Methodology Report — Current Pipeline
*Apple Inc. (AAPL) Sentiment-Driven Stock Prediction*
*Last Updated: February 2026*

---

## 1. Research Design Overview

This study investigates whether sentiment extracted from professional financial news headlines can improve short-term stock price direction prediction, either independently or when combined with technical indicators derived from market data. The analysis is structured around two distinct prediction tasks — next-day and intraday — to assess whether news sentiment provides value across different forecasting horizons.

Both tasks are formulated as binary classification problems. All predictive features are constructed strictly from information available at the time of prediction, ensuring no future information is incorporated into the modeling process.

- **Asset**: Apple Inc. (AAPL)
- **Analysis Period**: January 2024 – December 2024 (one full calendar year)
- **Model**: Logistic Regression (single model; focus is feature comparison, not model selection)
- **Significance Level**: α = 0.05

**Asset selection rationale**: Apple Inc. (AAPL) was selected for four reasons. First, it is one of the most extensively covered companies in the financial press — the Wall Street Journal publishes Apple-related headlines on a near-weekly basis throughout the year, providing sufficient headline density for meaningful daily sentiment aggregation. Second, AAPL is one of the largest and most liquid equities in the world, minimising the risk that results are driven by thin-market microstructure effects. Third, its inclusion in the S&P 500 and status as a widely held institutional stock makes it a natural subject for market-efficiency research. Fourth, the concentration on a single, well-understood asset ensures that observed sentiment-return relationships are not obscured by cross-sectional variation across companies. The limitation of single-asset generalisation is acknowledged in the limitations section.

---

## 2. Data Sources

### 2.1 News Headlines — Wall Street Journal via ProQuest

Historical Apple-related news headlines were sourced from the Wall Street Journal through the ProQuest academic database. Only articles containing Apple-specific terms in the headline were retained, ensuring that sentiment signals are directly relevant to the target asset. Headlines were preprocessed using a dedicated script (`proquest_preprocessor.py`) that normalises dates, removes duplicates, and outputs a clean CSV (`wsj_apple_proquest.csv`).

**Fields used**: `date`, `headline`

### 2.2 Stock Price Data — Yahoo Finance (`yfinance`)

Daily OHLCV (Open, High, Low, Close, Volume) data for AAPL were retrieved using the `yfinance` Python library. Only trading days are present in this dataset; weekends and market holidays are automatically excluded.

**Fields used**: `Open`, `Close` (adjusted for splits)

---

## 3. Sentiment Scoring — FinBERT

Sentiment was scored at the headline level using **FinBERT** (`ProsusAI/finbert`), a BERT-based transformer model pre-trained on financial text. Each headline is passed through the model, which outputs a softmax probability distribution over three classes:

| Index | Label |
|---|---|
| 0 | Neutral |
| 1 | Positive |
| 2 | Negative |

The probability scores (not discrete labels) are retained for feature engineering, preserving the model's confidence information.

### 3.1 Caching

To avoid re-running FinBERT on every pipeline execution, scored results are saved to `results/historical_sentiment_analysis.csv` on first run. On subsequent runs, the pipeline checks whether this cache file exists and is at least as recent as the source headlines file. If so, it loads from cache and skips FinBERT entirely, making re-runs substantially faster.

### 3.2 Daily Sentiment Aggregation

Individual headline scores are aggregated to the trading-day level using the **mean** across all headlines published on that day:

```
avg_positive(t) = mean of positive probabilities across all headlines on day t
avg_negative(t) = mean of negative probabilities across all headlines on day t
avg_neutral(t)  = mean of neutral  probabilities across all headlines on day t
```

Days with no headlines have no sentiment observation and are excluded from both experiments via the inner join with stock data (see Section 5).

---

## 4. Technical Indicators

All technical indicators are calculated on the **full consecutive trading-day series** (every market day, regardless of whether a headline exists). This is critical — computing lags or rolling windows after the inner join with sentiment would cause gaps in WSJ coverage to produce incorrect lag alignments (e.g., Jan 7's lag would skip Jan 6 if Jan 6 had no headline).

The three core indicators are calculated as follows:

### 4.1 One-Day Return (`return_1d`)
```
return_1d(t) = (Close(t) - Close(t-1)) / Close(t-1)
```
Captures short-term price momentum. Fully known by market close on day t.

### 4.2 Relative Position to 20-Day SMA (`price_vs_sma20`)
```
SMA_20(t)       = mean of Close over the last 20 trading days (t-19 to t)
price_vs_sma20(t) = (Close(t) - SMA_20(t)) / SMA_20(t)
```
Measures how far the current price deviates from its recent trend. Positive = above trend; negative = below trend.

### 4.3 RSI Momentum Change (`rsi_change`)
```
RSI_14(t)   = 100 - (100 / (1 + AvgGain(t) / AvgLoss(t)))
              using Wilder's smoothed EMA (alpha = 1/14)
rsi_change(t) = RSI_14(t) - RSI_14(t-1)
```
Captures acceleration or deceleration of momentum rather than absolute momentum level.

> **Note**: The rolling SMA and EMA windows produce NaN values for approximately the first 20 rows of the stock series. These rows are dropped during dataset construction.

---

## 5. Experiment Designs

### Experiment 1: Next-Day Price Direction Prediction

**Research question**: Can same-day news sentiment and same-day technical indicators predict whether tomorrow's closing price will be higher than today's?

**Target variable**:
```
next_close(t)        = Close(t+1)   ← forward-shifted on the full stock series
stock_move_nextday(t) = 1 if next_close(t) > Close(t) else 0
```

**Feature set**:

| Feature | Description | Timing |
|---|---|---|
| `avg_positive` | Mean positive sentiment probability | Same day (t) |
| `avg_negative` | Mean negative sentiment probability | Same day (t) |
| `avg_neutral` | Mean neutral sentiment probability | Same day (t) |
| `return_1d` | Today's daily return | Close(t) |
| `price_vs_sma20` | Close(t) vs 20-day SMA | Close(t) |
| `rsi_change` | Change in RSI_14 today | Close(t) |

**Merge**: Inner join of daily sentiment with stock data on `date`. Only trading days with both a stock price and at least one headline are retained.

**Dataset**: 159 rows before NaN removal; **144 rows** after dropping rows with missing technical indicators (from rolling windows).

---

### Experiment 2: Intraday Price Direction Prediction

**Research question**: Can same-day news sentiment and information available at market open predict whether today's closing price will be higher than today's opening price?

**Target variable**:
```
stock_move_intraday(t) = 1 if Close(t) > Open(t) else 0
```

**Feature set**:

| Feature | Formula | Timing |
|---|---|---|
| `avg_positive` | Mean positive sentiment probability | Same day news (t) |
| `avg_negative` | Mean negative sentiment probability | Same day news (t) |
| `avg_neutral` | Mean neutral sentiment probability | Same day news (t) |
| `overnight_gap` | `(Open(t) - Close(t-1)) / Close(t-1)` | Known at market open |
| `open_vs_sma20` | `(Open(t) - SMA_20(t-1)) / SMA_20(t-1)` | Known at market open |
| `rsi_change_lag1` | `RSI_14(t-1) - RSI_14(t-2)` | Known at market open |

**Rationale for at-open technical features**:

- **Overnight gap**: The gap between yesterday's close and today's open captures pre-market activity, after-hours news reactions, and overnight sentiment. It is more timely than yesterday's close-based return and directly contextualises the intraday prediction task.
- **Open vs SMA20**: Compares today's opening price to the 20-day moving average built from prior closing prices (all known before market opens). This is what intraday traders observe at 9:30 AM.
- **RSI change lag-1**: RSI is computed from closing prices. The most current RSI reading available at market open is yesterday's, so the lag-1 RSI change is both correct and realistic.

**Lag alignment**: All at-open technical features are computed on the **full consecutive trading-day series** before the inner join with sentiment. This ensures that lags always refer to the true previous trading day, not the previous news day.

**Dataset**: 143 rows (after inner join and NaN removal from rolling windows).

---

## 6. Model Training

### 6.1 Feature Configurations

For each experiment, three logistic regression models are trained independently to isolate the contribution of each feature type:

| Configuration | Features Used |
|---|---|
| **Technical Only** | Technical indicators only (3 features) |
| **Sentiment Only** | `avg_positive`, `avg_negative`, `avg_neutral` (3 features) |
| **Technical + Sentiment** | All 6 features combined |

### 6.2 Logistic Regression

```
P(Y=1 | X) = 1 / (1 + exp(-z))
where z = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ

Decision rule: ŷ = 1 if P(Y=1|X) ≥ 0.5, else 0
```

- **Solver**: `lbfgs`
- **Regularisation**: L2 (C = 1.0)
- **Class weight**: `'balanced'`
- **Max iterations**: 1000
- **Random state**: 42

Logistic Regression was selected for its interpretability, suitability for small datasets, and established use as a baseline in financial prediction research. The focus of this study is on feature comparison rather than model optimisation.

**Class imbalance treatment**: Both experiments exhibit class imbalance in the test set — the "Up" class accounts for approximately 61% of next-day observations and 67% of intraday observations, reflecting a broadly bullish market period for AAPL in 2024. To prevent the classifier from collapsing to always predicting the majority class, `class_weight='balanced'` is applied to all models. This setting causes scikit-learn to inversely weight each class by its frequency in the training set, so misclassifying the minority ("Down") class incurs a proportionally higher penalty during training. This is preferred over resampling techniques (e.g. SMOTE) for small financial time-series datasets where synthetic data generation risks distorting the temporal structure of returns.

**Hyperparameter tuning**: Regularisation strength (C = 1.0) was intentionally held at the default value and no grid search was performed. Given the limited dataset size (100 training samples), hyperparameter tuning would risk overfitting to training-period idiosyncrasies rather than improving genuine generalisation. The primary objective of this study is to isolate the contribution of different feature sets — holding model configuration constant across all comparisons ensures that observed performance differences are attributable to features rather than tuning artefacts.

### 6.3 Feature Scaling

Features are standardised (Z-score normalisation) using `StandardScaler`:

```
X_scaled = (X - μ_train) / σ_train
```

Scaling parameters are fitted **exclusively on the training set** and then applied to both the training and test sets. This prevents any information from the test period leaking into feature normalisation.

Separate scalers are fitted for each of the three feature configurations.

---

## 7. Evaluation Strategy

### 7.0 Primary vs. Robustness Evaluation

Final performance comparisons are based on the **chronological holdout test set**, which serves as the primary out-of-sample evaluation. Cross-validation is used exclusively as a robustness check to verify that holdout results are not artifacts of a single particular train/test boundary. Where the two diverge, both are reported and discussed, with the holdout result treated as the definitive performance estimate.

### 7.1 Time-Based Train/Test Split

```
Train: first 70% of observations (chronologically)  →  ~Jan–Aug 2024 (100 samples)
Test:  last  30% of observations (chronologically)  →  ~Sep–Dec 2024 (43–44 samples)
```

No random shuffling is applied. All training data precedes all test data in calendar time, mirroring realistic forward-looking deployment.

### 7.2 5-Fold Time-Series Cross-Validation

Cross-validation is performed using `TimeSeriesSplit` with 5 folds and an **expanding training window**:

```
Fold 1: Train [────────]           Test [──]
Fold 2: Train [─────────────]      Test [──]
Fold 3: Train [──────────────────] Test [──]
Fold 4: Train [───────────────────────] Test [──]
Fold 5: Train [────────────────────────────] Test [──]
```

Performance metrics (accuracy, precision, recall, F1) are reported as mean ± standard deviation across all 5 folds. Cross-validation provides a more robust estimate of generalisation than a single holdout split, and the standard deviation indicates stability across different temporal market conditions.

### 7.3 Evaluation Metrics

| Metric | Formula | Interpretation |
|---|---|---|
| **Accuracy** | (TP + TN) / N | Overall fraction of correct predictions |
| **Precision (Up)** | TP / (TP + FP) | Of predicted "Up" days, how many were correct |
| **Recall (Up)** | TP / (TP + FN) | Of actual "Up" days, how many were caught |
| **F1-Score (Up)** | 2 × (P × R) / (P + R) | Harmonic mean of precision and recall |

Where: TP = True Positive, TN = True Negative, FP = False Positive, FN = False Negative.

Metrics are reported for the "Up" class (stock goes up), as this is the primary class of interest.

### 7.4 Majority Class Baseline

Because the test set is not perfectly balanced (more "Up" days than "Down" days in both experiments), a naïve majority-class baseline — always predicting "Up" — provides an important reference point alongside the 50% coin-toss baseline:

| Experiment | Coin Toss | Majority Class Baseline |
|---|---|---|
| Next-Day | 50.00% | 61.36% (27 Up / 44 total) |
| Intraday | 50.00% | 67.44% (29 Up / 43 total) |

Results should be interpreted in the context of both baselines.

### 7.5 Statistical Significance — McNemar's Test

Because all three models are evaluated on the same test set, McNemar's exact binomial test is used to assess whether differences in accuracy are statistically significant or attributable to chance.

**Statistical power caveat**: With a holdout test set of 43–44 observations, only large performance differences are likely to reach statistical significance under McNemar's test. Specifically, the number of discordant pairs (cases where one model is correct and the other is not) must be substantial to achieve p < 0.05. In practice, this means the test is powered to detect only sizeable systematic differences in model behaviour; moderate improvements may go undetected. Non-significant results are therefore interpreted conservatively — they indicate that differences cannot be confirmed as statistically reliable, not that no difference exists.

```
H₀: The two models have the same error rate
H₁: The two models have different error rates

Test statistic based on discordant pairs:
  b = cases where Model A correct, Model B wrong
  c = cases where Model A wrong, Model B correct

p-value = 2 × Binomial_CDF(min(b,c); b+c; 0.5)
```

Three comparisons are made per experiment:
1. Technical Only vs. Combined
2. Sentiment Only vs. Combined
3. **Technical Only vs. Sentiment Only** (direct comparison)

A p-value < 0.05 is required to reject the null hypothesis. Given the small test set size (43–44 samples), statistical power is limited and non-significant results are interpreted conservatively.

---

## 8. Data Leakage Safeguards

| Safeguard | Implementation |
|---|---|
| Target variable only | `Close(t+1)` is used exclusively for label construction, never as a feature |
| Feature timing | All features use information available at or before the prediction time |
| Technical lags on full series | Shifts computed before inner join to prevent news-gap misalignment |
| Scaling | `StandardScaler` fitted on training data only, applied to test data |
| Chronological split | Training always precedes test data in calendar time |
| Cross-validation | `TimeSeriesSplit` ensures no future data appears in any training fold |

---

## 9. Pipeline Implementation

| Component | Tool / Library |
|---|---|
| Language | Python 3.x |
| Stock data | `yfinance` |
| Sentiment model | `transformers` (`ProsusAI/finbert`) |
| Data manipulation | `pandas`, `numpy` |
| Machine learning | `scikit-learn` (LogisticRegression, StandardScaler, TimeSeriesSplit) |
| Statistical testing | `scipy.stats.binom` (exact McNemar test) |
| Visualisation | `matplotlib` |
| Entry point | `scripts/main.py` |

FinBERT sentiment scores are cached to `results/historical_sentiment_analysis.csv` after the first run. Subsequent executions load from cache if the file exists and is at least as recent as the source headlines file, avoiding redundant GPU/CPU computation.

---

## 10. Key Numbers for Thesis Writing

| Parameter | Experiment 1 (Next-Day) | Experiment 2 (Intraday) |
|---|---|---|
| Asset | AAPL | AAPL |
| Period | Jan–Dec 2024 | Jan–Dec 2024 |
| Data source | WSJ via ProQuest | WSJ via ProQuest |
| Total observations | 159 (pre-NaN) → **144** | 143 |
| Train samples | 100 | 100 |
| Test samples | 44 | 43 |
| CV folds | 5 | 5 |
| Sentiment features | 3 (`avg_positive`, `avg_negative`, `avg_neutral`) | 3 (same) |
| Technical features | 3 (`return_1d`, `price_vs_sma20`, `rsi_change`) | 3 (`overnight_gap`, `open_vs_sma20`, `rsi_change_lag1`) |
| Model | Logistic Regression | Logistic Regression |
| Target | Close(t+1) > Close(t) | Close(t) > Open(t) |
| Significance level | α = 0.05 | α = 0.05 |

---

*Generated from pipeline `scripts/main.py` — reflects current implementation as of February 2026.*
