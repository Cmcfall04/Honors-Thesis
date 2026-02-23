# Results — Sentiment-Driven Stock Prediction
*Apple Inc. (AAPL) · Wall Street Journal Headlines · Full-Year 2024*
*Last Updated: February 2026*

---

## 1. Dataset Summary

### 1.1 Raw Data

| Item | Count |
|---|---|
| Raw WSJ headlines (AAPL, 2024) | ~361 individual scored headlines |
| Total AAPL trading days in 2024 | ~252 |
| Trading days with at least one WSJ headline | ~143–144 (~57%) |
| Trading days with **no** WSJ coverage | ~108–109 (~43%) |

The 43% of trading days with no headline coverage are excluded from both experiments via the inner join between sentiment and stock data. This is an important caveat: the sample is not representative of all trading days — it is representative of days for which the Wall Street Journal published Apple-related coverage.

### 1.2 Data Removed Due to Rolling Window Constraints

Technical indicators require a minimum history to compute:

| Indicator | Window Required |
|---|---|
| SMA_20 | 20 trading days |
| RSI_14 | 14 trading days |

The SMA_20 is the binding constraint. The first **19 trading days** of the stock series (approximately the first three weeks of January 2024) produce `NaN` values and are dropped during dataset construction. This is standard practice and is consistent with all technical analysis research that uses rolling windows.

> *"The first 19 trading days were excluded due to insufficient historical data for rolling-window calculations (SMA_20 requires 20 days, RSI_14 requires 14 days)."*

### 1.3 Final Dataset Sizes

| Item | Experiment 1 (Next-Day) | Experiment 2 (Intraday) |
|---|---|---|
| Rows before NaN removal | 159 | ~162 |
| **Final dataset (after NaN drop)** | **144** | **143** |
| Training samples (first 70%) | 100 | 100 |
| Test samples (last 30%) | 44 | 43 |

### 1.4 Class Distribution in Test Set

| Experiment | Up Days | Down/Flat Days | Majority-Class Baseline |
|---|---|---|---|
| Next-Day | 27 / 44 (61.4%) | 17 / 44 (38.6%) | **61.36%** |
| Intraday | 29 / 43 (67.4%) | 14 / 43 (32.6%) | **67.44%** |

The test set is not balanced — AAPL had a broadly bullish 2024, resulting in more "Up" days than "Down" days. All models are benchmarked against both the 50% coin-toss baseline and the majority-class baseline (always predicting "Up"). To account for this imbalance during training, `class_weight='balanced'` was applied to all logistic regression models.

---

## 2. Experiment 1 — Next-Day Price Direction Prediction

**Research Question**: Can same-day news sentiment and same-day technical indicators (based on closing prices) predict whether tomorrow's closing price will be higher than today's?

**Target Variable**: `stock_move_nextday(t) = 1 if Close(t+1) > Close(t) else 0`

### 2.1 Technical Features Used

| Feature | Description | Timing |
|---|---|---|
| `return_1d` | `(Close(t) - Close(t-1)) / Close(t-1)` | Close of day t |
| `price_vs_sma20` | `(Close(t) - SMA_20(t)) / SMA_20(t)` | Close of day t |
| `rsi_change` | `RSI_14(t) - RSI_14(t-1)` | Close of day t |

### 2.2 Holdout Test Results (Primary Evaluation)

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) |
|---|---|---|---|---|
| Technical Only | 50.00% | 59.26% | 59.26% | 59.26% |
| Sentiment Only | 43.18% | 53.33% | 59.26% | 56.14% |
| Technical + Sentiment | 45.45% | 55.17% | 59.26% | 57.14% |
| **Majority Class Baseline** | **61.36%** | — | — | — |
| **Coin Toss Baseline** | **50.00%** | — | — | — |

**Test Period**: 2024-08-29 to 2024-12-23 (44 observations)

### 2.3 Key Findings — Experiment 1

- The **Technical Only** model is the best-performing model at 50.00% accuracy, matching the coin-toss baseline.
- The **Sentiment Only** model (43.18%) underperforms the coin-toss — adding sentiment alone is not helpful for next-day prediction.
- The **Combined** model (45.45%) does not improve over Technical Only; it falls between the two individual models.
- Critically, **all three models fall below the majority-class baseline of 61.36%** — a naïve strategy of always predicting "Up" would have beaten all three models on the holdout test set.
- The marginal contribution of adding sentiment to technical features is **negative** (−4.55 percentage points).
- These results are broadly consistent with the **semi-strong form of the Efficient Market Hypothesis (EMH)**: publicly available news information does not appear to provide exploitable next-day predictive power.

### 2.4 Detailed Classification Report — Experiment 1

**Technical Only**
```
              precision    recall  f1-score   support

   Down/Flat       0.35      0.35      0.35        17
          Up       0.59      0.59      0.59        27

    accuracy                           0.50        44
   macro avg       0.47      0.47      0.47        44
weighted avg       0.50      0.50      0.50        44
```

**Sentiment Only**
```
              precision    recall  f1-score   support

   Down/Flat       0.21      0.18      0.19        17
          Up       0.53      0.59      0.56        27

    accuracy                           0.43        44
   macro avg       0.37      0.38      0.38        44
weighted avg       0.41      0.43      0.42        44
```

**Technical + Sentiment**
```
              precision    recall  f1-score   support

   Down/Flat       0.27      0.24      0.25        17
          Up       0.55      0.59      0.57        27

    accuracy                           0.45        44
   macro avg       0.41      0.41      0.41        44
weighted avg       0.44      0.45      0.45        44
```

### 2.5 Cross-Validation Results — Experiment 1

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) |
|---|---|---|---|---|
| Technical Only | 45.83% ± 10.54% | 43.71% ± 27.67% | 40.09% ± 24.04% | 41.65% ± 25.42% |
| Sentiment Only | 46.67% ± 8.50% | 59.18% ± 12.77% | 41.60% ± 13.40% | 47.01% ± 9.79% |
| Technical + Sentiment | 45.00% ± 10.99% | 54.95% ± 13.68% | 42.83% ± 20.84% | 45.18% ± 17.68% |

Cross-validation results are broadly consistent with holdout results — all models perform at or below the coin-toss level when averaged across multiple time-based windows. The high standard deviations (particularly for Technical Only) indicate considerable variability across folds, suggesting that performance is sensitive to which time period is used for evaluation. This instability is itself an informative finding: the models do not learn consistent, time-stable patterns.

### 2.6 Statistical Significance — Experiment 1 (McNemar's Test)

| Comparison | Discordant Pairs (b, c) | p-value | Significant? |
|---|---|---|---|
| Technical Only vs. Combined | (6, 4) | 0.7539 | ❌ No |
| Sentiment Only vs. Combined | (1, 2) | 1.0000 | ❌ No |
| **Technical Only vs. Sentiment Only** | **(8, 5)** | **0.5811** | **❌ No** |

No pairwise comparison reaches statistical significance (p < 0.05) in Experiment 1. This means we cannot confirm that any model is reliably better than any other. However, this is partly a consequence of limited statistical power — with only 44 test observations, McNemar's test can only detect large, systematic performance differences.

---

## 3. Experiment 2 — Intraday Price Direction Prediction

**Research Question**: Can same-day news sentiment and information available at market open predict whether today's closing price will be higher than today's opening price?

**Target Variable**: `stock_move_intraday(t) = 1 if Close(t) > Open(t) else 0`

### 3.1 Technical Features Used

All intraday technical features are computed using **only information available at market open** (9:30 AM), ensuring no look-ahead bias.

| Feature | Formula | Timing |
|---|---|---|
| `overnight_gap` | `(Open(t) - Close(t-1)) / Close(t-1)` | Known at market open |
| `open_vs_sma20` | `(Open(t) - SMA_20(t-1)) / SMA_20(t-1)` | Known at market open |
| `rsi_change_lag1` | `RSI_14(t-1) - RSI_14(t-2)` | Known at market open |

**Feature rationale:**
- **Overnight gap**: Captures pre-market activity, after-hours news reactions, and the emotional gap between yesterday's close and today's open. A positive gap (opening above yesterday's close) often signals bullish overnight sentiment.
- **Open vs SMA20**: Places today's opening price in context of the 20-day trend. Using `SMA_20(t-1)` (yesterday's SMA) ensures this is fully known at the time of prediction.
- **RSI change lag-1**: RSI is derived from closing prices, so the most recent RSI reading available at market open is yesterday's. The lag-1 change therefore correctly uses `RSI_14(t-1) - RSI_14(t-2)`.

**Important**: All features are computed on the **full consecutive trading-day series** before the inner join with sentiment data. This prevents news-coverage gaps from corrupting lag alignments.

### 3.2 Holdout Test Results (Primary Evaluation)

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) |
|---|---|---|---|---|
| Technical Only | 48.84% | 68.42% | 44.83% | 54.17% |
| Sentiment Only | **62.79%** | **78.26%** | **62.07%** | **69.23%** |
| Technical + Sentiment | 55.81% | 70.83% | 58.62% | 64.15% |
| **Majority Class Baseline** | **67.44%** | — | — | — |
| **Coin Toss Baseline** | **50.00%** | — | — | — |

**Test Period**: 2024-08-30 to 2024-12-23 (43 observations)

### 3.3 Key Findings — Experiment 2

- The **Sentiment Only** model (62.79%) is the best-performing model, outperforming Technical Only by **13.95 percentage points**.
- The **Sentiment Only** model approaches — but does not exceed — the majority-class baseline of 67.44%, meaning it still falls short of the naïve "always predict Up" strategy on raw accuracy.
- However, the **Sentiment Only** model correctly predicts 9 out of 14 Down/Flat days (64% recall for the minority class), whereas always predicting "Up" would catch 0. This is the key advantage — the model provides genuine signal, not just majority-class agreement.
- The **Combined** model (55.81%) does not improve over Sentiment Only; adding technical indicators to sentiment **reduces** performance by 6.98 percentage points on the holdout test.
- The **Technical Only** model (48.84%) performs below the coin-toss, suggesting that the chosen at-open technical features alone are not predictive of intraday direction.
- The **F1-Score** tells a stronger story: Sentiment Only (69.23%) substantially outperforms Technical Only (54.17%) and Combined (64.15%).
- These results suggest that news sentiment carries more information for intraday movement than the technical state of the market at open.

### 3.4 Detailed Classification Report — Experiment 2

**Technical Only**
```
              precision    recall  f1-score   support

   Down/Flat       0.33      0.57      0.42        14
          Up       0.68      0.45      0.54        29

    accuracy                           0.49        43
   macro avg       0.51      0.51      0.48        43
weighted avg       0.57      0.49      0.50        43
```

**Sentiment Only**
```
              precision    recall  f1-score   support

   Down/Flat       0.45      0.64      0.53        14
          Up       0.78      0.62      0.69        29

    accuracy                           0.63        43
   macro avg       0.62      0.63      0.61        43
weighted avg       0.67      0.63      0.64        43
```

**Technical + Sentiment**
```
              precision    recall  f1-score   support

   Down/Flat       0.37      0.50      0.42        14
          Up       0.71      0.59      0.64        29

    accuracy                           0.56        43
   macro avg       0.54      0.54      0.53        43
weighted avg       0.60      0.56      0.57        43
```

### 3.5 Cross-Validation Results — Experiment 2

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) |
|---|---|---|---|---|
| Technical Only | 45.22% ± 12.48% | 44.30% ± 29.43% | 37.50% ± 19.88% | 38.91% ± 23.40% |
| Sentiment Only | 47.83% ± 13.75% | 55.87% ± 21.06% | 50.26% ± 11.96% | 50.80% ± 15.18% |
| Technical + Sentiment | 50.43% ± 10.86% | 64.15% ± 19.28% | 47.18% ± 18.48% | 48.63% ± 14.78% |

**Important divergence**: Cross-validation results are considerably weaker than the holdout results for Experiment 2. While the holdout shows Sentiment Only at 62.79%, CV gives only 47.83% on average. This divergence indicates that the holdout test set may have fallen in a time period particularly favourable to sentiment-based prediction (e.g., concentrated news events in late 2024 with clear directional impact). This should be explicitly acknowledged in the thesis as a limitation.

### 3.6 Statistical Significance — Experiment 2 (McNemar's Test)

| Comparison | Discordant Pairs (b, c) | p-value | Significant? |
|---|---|---|---|
| Technical Only vs. Combined | (5, 8) | 0.5811 | ❌ No |
| Sentiment Only vs. Combined | (5, 2) | 0.4531 | ❌ No |
| **Technical Only vs. Sentiment Only** | **(7, 13)** | **0.2632** | **❌ No** |

Despite Sentiment Only outperforming Technical Only by nearly 14 percentage points on accuracy, no comparison reaches statistical significance (p < 0.05). This is a direct consequence of the small holdout sample size (43 observations) and the limited number of discordant pairs — the test does not have enough power to confirm this as a statistically reliable difference.

> *"Given the relatively small holdout sample size (43–44 observations), only large performance differences are likely to reach statistical significance under McNemar's test. Moderate improvements may go undetected. Non-significant results are therefore interpreted conservatively — they indicate that differences cannot be confirmed as statistically reliable, not that no difference exists."*

---

## 4. Cross-Experiment Summary

| | Exp. 1: Next-Day | Exp. 2: Intraday |
|---|---|---|
| Best performing model | Technical Only (50.00%) | Sentiment Only (62.79%) |
| Does sentiment help? | No (negative marginal contribution) | Partially (13.95pp improvement vs. technical) |
| Does combining help? | No | No |
| Beats coin-toss (50%)? | Technical Only ties; others below | Sentiment Only exceeds; others near or below |
| Beats majority baseline? | No model beats 61.36% | No model beats 67.44% |
| Statistically significant difference? | No (all p > 0.05) | No (all p > 0.05) |
| CV consistent with holdout? | Yes (broadly similar) | No (CV much weaker — potential holdout period bias) |

---

## 5. Interpretation and Thesis Implications

### 5.1 Sentiment and the Efficient Market Hypothesis

The results for **Experiment 1 (next-day prediction)** are consistent with the **semi-strong form of the EMH**. Publicly available news sentiment from the Wall Street Journal does not provide statistically significant predictive power for next-day closing prices. Even the best-performing model (Technical Only) only matches the coin-toss baseline and falls well short of the majority-class baseline.

### 5.2 Intraday Signal

**Experiment 2 (intraday)** provides more encouraging evidence for sentiment. The Sentiment Only model outperforms Technical Only by ~14 percentage points on the holdout test and correctly identifies a meaningful proportion of down days (which the majority-class baseline misses entirely). This suggests that news sentiment may be more informative for **intraday direction** (open-to-close) than for **overnight direction** (close-to-close). A possible explanation is that investor reaction to news plays out within the trading session, not necessarily overnight.

However, this finding is tempered by two caveats:
1. It does not reach statistical significance (p = 0.2632), likely due to small sample size.
2. Cross-validation results do not replicate this magnitude of improvement, suggesting some sensitivity to the specific test period chosen.

### 5.3 Adding Sentiment to Technical Indicators Does Not Help

In both experiments, combining sentiment with technical indicators **failed to improve** over the best individual model. In the next-day experiment, the combined model underperforms technical alone; in the intraday experiment, the combined model underperforms sentiment alone. This suggests that the features contain overlapping or conflicting information, and that combining them without further feature selection or dimensionality reduction does not add value in this setting.

### 5.4 Statistical Power Limitation

With 43–44 test observations, the study is substantially underpowered for McNemar's test. A sample of this size can reliably detect only very large, systematic differences in model error rates. The failure to reach significance should **not** be interpreted as evidence that the models are equivalent — it is more accurately described as inconclusive given the sample size. A longer analysis period, multiple assets, or additional years of data would substantially increase statistical power.

### 5.5 Sample Coverage Limitation

Only ~57% of trading days had matching WSJ headline coverage. This means the models are trained and evaluated only on "newsworthy" days — days when Apple attracted media attention. It is plausible that market dynamics differ between covered and uncovered days, introducing a selection bias that limits generalisability to all trading days.

---

## 6. Quick Reference Table

| Item | Value |
|---|---|
| Asset | AAPL |
| Period | January – December 2024 |
| Headline source | Wall Street Journal via ProQuest |
| Sentiment model | FinBERT (`ProsusAI/finbert`) |
| ML model | Logistic Regression (L2, C=1.0, balanced class weight) |
| Final dataset size (Exp. 1) | 144 observations |
| Final dataset size (Exp. 2) | 143 observations |
| Train / Test split | 70% / 30% chronological |
| Training samples | 100 (both experiments) |
| Test samples | 44 (Exp. 1), 43 (Exp. 2) |
| CV strategy | 5-fold TimeSeriesSplit |
| Best model — Next-Day | Technical Only: 50.00% accuracy |
| Best model — Intraday | Sentiment Only: 62.79% accuracy, 69.23% F1 |
| Majority-class baseline — Next-Day | 61.36% |
| Majority-class baseline — Intraday | 67.44% |
| Any statistically significant result? | No (all McNemar p > 0.05) |
| Rows dropped for rolling windows | ~19 (SMA_20 is binding constraint) |

---

*Generated from pipeline `scripts/main.py` — results reflect the run of 2026-02-22.*
