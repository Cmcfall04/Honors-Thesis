# Sentiment Analysis & Stock Movement Prediction — Results Summary

**Assets analyzed:** Apple Inc. (AAPL) and S&P 500 Index (^GSPC)  
**Period:** January 1 – December 31, 2024  
**Model:** Logistic Regression with FinBERT sentiment features  

---

## Overview

This study tests whether Wall Street Journal headlines, scored for financial
sentiment using FinBERT, contain predictive signal for short-term stock
movements — beyond what technical price indicators alone provide.

Two experiments were run for each asset:

| Experiment | Prediction Target | Feature Timing |
|---|---|---|
| **Experiment 1 — Next-Day** | Will tomorrow's close > today's close? | Same-day sentiment + same-day technical indicators |
| **Experiment 2 — Intraday** | Will today's close > today's open? | Same-day sentiment + lagged (prior-day) at-open technical indicators |

Three models were compared in each experiment:

| Model | Features Used |
|---|---|
| **Technical Only (Model A)** | `return_1d`, `price_vs_sma20`, `rsi_change` |
| **Sentiment Only (Model B)** | `avg_positive`, `avg_negative`, `avg_neutral` |
| **Technical + Sentiment (Model C)** | All six features combined |

All models used logistic regression with `class_weight='balanced'` and
`StandardScaler` normalization. Statistical significance was tested using
McNemar's exact binomial test.

---

## Dataset Summary

### Apple (AAPL)

- **Headline source:** WSJ articles exported from ProQuest, 2024
- **Input file:** `data/processed/wsj_apple_proquest.csv` (361 headlines)
- **Note:** No leakage-filtering step was applied to the Apple dataset.
  A manual review identified ~15 headlines (~4%) with same-day market
  outcome language; these remain in the dataset and may slightly inflate
  sentiment model performance.
- **Stock data:** Downloaded via yfinance (`AAPL`, 2024-01-01 to 2024-12-31)

| Experiment | Train Period | Test Period | Train Samples | Test Samples |
|---|---|---|---|---|
| Next-Day | 2024-01-30 → 2024-08-28 | 2024-08-29 → 2024-12-23 | 100 | 44 |
| Intraday | 2024-02-01 → 2024-08-29 | 2024-08-30 → 2024-12-23 | 100 | 43 |

### S&P 500 (^GSPC)

- **Headline source:** WSJ articles exported from ProQuest in three batches
- **Raw input:** `data/raw/S&P_firstbatch.csv`, `S&P_secondbatch.csv`,
  `S&P_thirdbatch.csv` (984 headlines combined)
- **After leakage filtering:** 834 headlines retained across 214 unique dates
  (150 removed — daily market-recap prefixes and same-day outcome phrases)
- **Filtered file:** `data/processed/wsj_sp500_proquest_filtered.csv`
- **Stock data:** Downloaded via yfinance (`^GSPC`, 2024-01-01 to 2024-12-31)

| Experiment | Train Period | Test Period | Train Samples | Test Samples |
|---|---|---|---|---|
| Next-Day | 2024-01-30 → 2024-09-30 | 2024-10-01 → 2024-12-27 | 140 | 61 |
| Intraday | 2024-01-31 → 2024-10-01 | 2024-10-02 → 2024-12-30 | 140 | 61 |

---

## Experiment 1: Next-Day Prediction

**Target:** `stock_move_nextday` = 1 if Close(t+1) > Close(t), else 0

### Apple (AAPL) — Next-Day Results

**Hold-out test set (2024-08-29 to 2024-12-23, n=44):**

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| Technical Only | **50.00%** | 59.26% | 59.26% | 59.26% |
| Sentiment Only | 43.18% | 53.33% | 59.26% | 56.14% |
| Technical + Sentiment | 45.45% | 55.17% | 59.26% | 57.14% |

**5-Fold Time-Series Cross-Validation:**

| Model | Accuracy (mean ± std) | F1 (mean ± std) |
|---|---|---|
| Technical Only | 45.83% ± 10.54% | 41.65% ± 25.42% |
| Sentiment Only | 46.67% ± 8.50% | 47.01% ± 9.79% |
| Technical + Sentiment | 45.00% ± 10.99% | 45.18% ± 17.68% |

**Detailed classification report — Technical Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.35    0.35      0.35       17
         Up       0.59    0.59      0.59       27
   accuracy                         0.50       44
```

**Detailed classification report — Sentiment Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.21    0.18      0.19       17
         Up       0.53    0.59      0.56       27
   accuracy                         0.43       44
```

**Detailed classification report — Technical + Sentiment:**
```
              precision  recall  f1-score  support
  Down/Flat       0.27    0.24      0.25       17
         Up       0.55    0.59      0.57       27
   accuracy                         0.45       44
```

**McNemar's Test (pairwise significance):**

| Comparison | Discordant Pairs | p-value | Significant? |
|---|---|---|---|
| Technical vs Combined | b=6, c=4 | 0.7539 | No |
| Sentiment vs Combined | b=1, c=2 | 1.0000 | No |
| Technical vs Sentiment | b=8, c=5 | 0.5811 | No |

**Key finding:** Technical indicators outperform sentiment by **6.82 pp**.
Adding sentiment to technical indicators *decreases* accuracy by 4.55 pp.
No pairwise differences are statistically significant.

---

### S&P 500 (^GSPC) — Next-Day Results

**Hold-out test set (2024-10-01 to 2024-12-27, n=61):**

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| Technical Only | **47.54%** | 55.56% | 42.86% | 48.39% |
| Sentiment Only | 40.98% | 48.57% | 48.57% | 48.57% |
| Technical + Sentiment | 47.54% | 55.56% | 42.86% | 48.39% |

**5-Fold Time-Series Cross-Validation:**

| Model | Accuracy (mean ± std) | F1 (mean ± std) |
|---|---|---|
| Technical Only | 49.70% ± 3.09% | 51.51% ± 6.75% |
| Sentiment Only | 50.30% ± 11.27% | 54.87% ± 9.96% |
| Technical + Sentiment | 47.27% ± 4.54% | 50.88% ± 7.77% |

**Detailed classification report — Technical Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.41    0.54      0.47       26
         Up       0.56    0.43      0.48       35
   accuracy                         0.48       61
```

**Detailed classification report — Sentiment Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.31    0.31      0.31       26
         Up       0.49    0.49      0.49       35
   accuracy                         0.41       61
```

**Detailed classification report — Technical + Sentiment:**
```
              precision  recall  f1-score  support
  Down/Flat       0.41    0.54      0.47       26
         Up       0.56    0.43      0.48       35
   accuracy                         0.48       61
```

**McNemar's Test (pairwise significance):**

| Comparison | Discordant Pairs | p-value | Significant? |
|---|---|---|---|
| Technical vs Combined | b=2, c=2 | 1.0000 | No |
| Sentiment vs Combined | b=12, c=16 | 0.5716 | No |
| Technical vs Sentiment | b=18, c=14 | 0.5966 | No |

**Key finding:** Technical indicators outperform sentiment by **6.56 pp**.
Adding sentiment provides **no change** in accuracy. No pairwise differences
are statistically significant.

---

## Experiment 2: Intraday Prediction

**Target:** `stock_move_intraday` = 1 if Close(t) > Open(t), else 0

Technical features are lagged one trading day to ensure only pre-market
information is used:

| Feature | Definition |
|---|---|
| `overnight_gap` | (Open(t) − Close(t−1)) / Close(t−1) |
| `open_vs_sma20` | (Open(t) − SMA₂₀(t−1)) / SMA₂₀(t−1) |
| `rsi_change_lag1` | RSI change at day t−1 |

### Apple (AAPL) — Intraday Results

**Hold-out test set (2024-08-30 to 2024-12-23, n=43):**

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| Technical Only | 48.84% | 68.42% | 44.83% | 54.17% |
| **Sentiment Only** | **62.79%** | **78.26%** | **62.07%** | **69.23%** |
| Technical + Sentiment | 55.81% | 70.83% | 58.62% | 64.15% |

**5-Fold Time-Series Cross-Validation:**

| Model | Accuracy (mean ± std) | F1 (mean ± std) |
|---|---|---|
| Technical Only | 45.22% ± 12.48% | 38.91% ± 23.40% |
| Sentiment Only | 47.83% ± 13.75% | 50.80% ± 15.18% |
| Technical + Sentiment | 50.43% ± 10.86% | 48.63% ± 14.78% |

**Detailed classification report — Technical Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.33    0.57      0.42       14
         Up       0.68    0.45      0.54       29
   accuracy                         0.49       43
```

**Detailed classification report — Sentiment Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.45    0.64      0.53       14
         Up       0.78    0.62      0.69       29
   accuracy                         0.63       43
```

**Detailed classification report — Technical + Sentiment:**
```
              precision  recall  f1-score  support
  Down/Flat       0.37    0.50      0.42       14
         Up       0.71    0.59      0.64       29
   accuracy                         0.56       43
```

**McNemar's Test (pairwise significance):**

| Comparison | Discordant Pairs | p-value | Significant? |
|---|---|---|---|
| Technical vs Combined | b=5, c=8 | 0.5811 | No |
| Sentiment vs Combined | b=5, c=2 | 0.4531 | No |
| Technical vs Sentiment | b=7, c=13 | 0.2632 | No |

**Key finding:** Sentiment **outperforms** technical indicators by **13.95 pp**
for intraday Apple prediction — the strongest result in the study. Adding
sentiment to technical indicators improves accuracy by +6.98 pp. However, no
pairwise differences reach statistical significance, likely due to the small
test set (n=43).

---

### S&P 500 (^GSPC) — Intraday Results

**Hold-out test set (2024-10-02 to 2024-12-30, n=61):**

| Model | Accuracy | Precision (Up) | Recall (Up) | F1 (Up) |
|---|---|---|---|---|
| **Technical Only** | **52.46%** | 57.14% | 48.48% | 52.46% |
| Sentiment Only | 50.82% | 54.05% | 60.61% | 57.14% |
| Technical + Sentiment | 45.90% | 50.00% | 51.52% | 50.75% |

**5-Fold Time-Series Cross-Validation:**

| Model | Accuracy (mean ± std) | F1 (mean ± std) |
|---|---|---|
| Technical Only | 50.30% ± 4.54% | 50.99% ± 4.95% |
| Sentiment Only | 50.91% ± 5.21% | 55.86% ± 6.71% |
| Technical + Sentiment | 50.30% ± 8.70% | 54.37% ± 8.30% |

**Detailed classification report — Technical Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.48    0.57      0.52       28
         Up       0.57    0.48      0.52       33
   accuracy                         0.52       61
```

**Detailed classification report — Sentiment Only:**
```
              precision  recall  f1-score  support
  Down/Flat       0.46    0.39      0.42       28
         Up       0.54    0.61      0.57       33
   accuracy                         0.51       61
```

**Detailed classification report — Technical + Sentiment:**
```
              precision  recall  f1-score  support
  Down/Flat       0.41    0.39      0.40       28
         Up       0.50    0.52      0.51       33
   accuracy                         0.46       61
```

**McNemar's Test (pairwise significance):**

| Comparison | Discordant Pairs | p-value | Significant? |
|---|---|---|---|
| Technical vs Combined | b=10, c=6 | 0.4545 | No |
| Sentiment vs Combined | b=11, c=8 | 0.6476 | No |
| Technical vs Sentiment | b=18, c=17 | 1.0000 | No |

**Key finding:** Technical indicators edge out sentiment by **1.64 pp**.
Adding sentiment *decreases* accuracy by 6.56 pp. No pairwise differences
are statistically significant.

---

## Cross-Asset Comparison

### Experiment 1 — Next-Day Prediction

| Asset | Best Model | Best Accuracy | CV Accuracy (best model) |
|---|---|---|---|
| AAPL | Technical Only | 50.00% | 45.83% ± 10.54% |
| ^GSPC | Technical Only | 47.54% | 49.70% ± 3.09% |

Both assets show near-random next-day accuracy, consistent with the
semi-strong form of the Efficient Market Hypothesis (EMH): publicly available
sentiment information is already priced in.

### Experiment 2 — Intraday Prediction

| Asset | Best Model | Best Accuracy | Sentiment vs Technical |
|---|---|---|---|
| AAPL | Sentiment Only | **62.79%** | Sentiment better by +13.95 pp |
| ^GSPC | Technical Only | 52.46% | Technical better by +1.64 pp |

The Apple intraday result stands out. Sentiment-only accuracy of 62.79% is
well above chance and the largest margin in the study. The S&P 500 intraday
results show near-random performance across all models, suggesting that
broad-market sentiment from WSJ does not offer a consistent intraday edge.

### Statistical Significance

Across all 12 pairwise McNemar's tests (2 assets × 2 experiments × 3
comparisons), **no comparison reached p < 0.05**. This means that while
performance differences are observed, none can be confidently distinguished
from chance variation given the sample sizes available.

| Asset | Experiment | Most significant comparison | p-value |
|---|---|---|---|
| AAPL | Next-Day | Technical vs Sentiment | 0.5811 |
| AAPL | Intraday | Technical vs Sentiment | 0.2632 |
| ^GSPC | Next-Day | Sentiment vs Combined | 0.5716 |
| ^GSPC | Intraday | Technical vs Combined | 0.4545 |

The Apple intraday technical vs sentiment comparison (p=0.2632) is the closest
to significance, corresponding to the largest observed accuracy gap (13.95 pp).

---

## Confusion Matrices

All confusion matrix images are saved in `results/`:

| Asset | Experiment | Technical | Sentiment | Combined |
|---|---|---|---|---|
| AAPL | Next-Day | `confusion_matrix_technical_nextday.png` | `confusion_matrix_sentiment_nextday.png` | `confusion_matrix_combined_nextday.png` |
| AAPL | Intraday | `confusion_matrix_technical_intraday.png` | `confusion_matrix_sentiment_intraday.png` | `confusion_matrix_combined_intraday.png` |
| ^GSPC | Next-Day | `confusion_matrix_technical_sp500_nextday.png` | `confusion_matrix_sentiment_sp500_nextday.png` | `confusion_matrix_combined_sp500_nextday.png` |
| ^GSPC | Intraday | `confusion_matrix_technical_sp500_intraday.png` | `confusion_matrix_sentiment_sp500_intraday.png` | `confusion_matrix_combined_sp500_intraday.png` |

---

## Limitations

1. **Small test sets** — Apple test sets (n=43–44) are too small to reliably
   detect moderate effect sizes, limiting the power of McNemar's test.
2. **Apple leakage** — The Apple headline dataset was not passed through a
   formal leakage filter. Approximately 15 headlines (~4%) contain same-day
   market outcome language, which may inflate intraday sentiment performance.
3. **Single year** — All results are based on 2024 data. Market conditions in
   a single year may not generalize.
4. **Sparse coverage** — WSJ headlines are not published every trading day.
   Days without headlines are dropped from the merged dataset, reducing sample
   sizes and creating uneven temporal coverage.
5. **Linear model** — Logistic regression captures only linear relationships;
   a non-linear model might extract additional signal from the features.

---

*Generated: 2026-02-28*
