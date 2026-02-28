# Model Comparison: Technical vs Sentiment vs Combined (Intraday (S&P 500) Prediction)

## Experimental Design

- **Prediction Target**: Intraday (S&P 500) price movement
- **Split Method**: Time-based (first 70% train, last 30% test)
- **Feature Scaling**: StandardScaler (mean=0, std=1) applied to all features
- **Train Period**: 2024-01-31 to 2024-10-01
- **Test Period**: 2024-10-02 to 2024-12-30
- **Train Samples**: 140
- **Test Samples**: 61
- **Technical Features**: overnight_gap, open_vs_sma20, rsi_change_lag1
- **Sentiment Features**: avg_positive, avg_negative, avg_neutral

## Results Summary

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Train Size | Test Size |
|-------|----------|----------------|-------------|---------------|------------|-----------|
| Technical Only | 52.46% | 57.14% | 48.48% | 52.46% | 140 | 61 |
| Sentiment Only | 50.82% | 54.05% | 60.61% | 57.14% | 140 | 61 |
| Technical + Sentiment | 45.90% | 50.00% | 51.52% | 50.75% | 140 | 61 |

## Cross-Validation Results

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Folds |
|-------|----------|----------------|-------------|---------------|-------|
| Technical Only | 50.30% ± 4.54% | 53.38% ± 7.50% | 49.37% ± 5.08% | 50.99% ± 4.95% | 5 |
| Sentiment Only | 50.91% ± 5.21% | 52.82% ± 6.64% | 59.88% ± 9.67% | 55.86% ± 6.71% | 5 |
| Technical + Sentiment | 50.30% ± 8.70% | 52.89% ± 9.27% | 56.65% ± 9.96% | 54.37% ± 8.30% | 5 |

**Note**: Cross-validation provides a more robust estimate of model performance by testing on multiple time-based splits. The standard deviation indicates stability across different time periods.


## Analysis

### Key Findings

1. **Technical-only model accuracy**: 52.46%
2. **Sentiment-only model accuracy**: 50.82%
3. **Combined model accuracy**: 45.90%

- Technical indicators **outperform** sentiment alone by 1.64 percentage points
- Combining features does **not improve** over the best individual model

### Marginal Contribution of Sentiment

Adding sentiment to technical indicators **decreases** performance by 6.56pp.

## Statistical Significance

**McNemar's Test** (tests if model differences are statistically significant):

### Technical Only vs Combined

- Technical correct, Combined wrong: 10 cases
- Technical wrong, Combined correct: 6 cases
- **p-value: 0.4545**
- **Result**: No significant difference (p >= 0.05)

### Sentiment Only vs Combined

- Sentiment correct, Combined wrong: 11 cases
- Sentiment wrong, Combined correct: 8 cases
- **p-value: 0.6476**
- **Result**: No significant difference (p >= 0.05)

### Technical Only vs Sentiment Only

- Technical correct, Sentiment wrong: 18 cases
- Technical wrong, Sentiment correct: 17 cases
- **p-value: 1.0000**
- **Result**: No significant difference (p >= 0.05)

**Interpretation**: McNemar's test compares two models on the same test cases. A p-value < 0.05 means the performance difference is statistically significant (not due to chance).

## Detailed Classification Reports

### Technical Only

```
precision    recall  f1-score   support

   Down/Flat       0.48      0.57      0.52        28
          Up       0.57      0.48      0.52        33

    accuracy                           0.52        61
   macro avg       0.53      0.53      0.52        61
weighted avg       0.53      0.52      0.52        61
```

### Sentiment Only

```
precision    recall  f1-score   support

   Down/Flat       0.46      0.39      0.42        28
          Up       0.54      0.61      0.57        33

    accuracy                           0.51        61
   macro avg       0.50      0.50      0.50        61
weighted avg       0.50      0.51      0.50        61
```

### Technical + Sentiment

```
precision    recall  f1-score   support

   Down/Flat       0.41      0.39      0.40        28
          Up       0.50      0.52      0.51        33

    accuracy                           0.46        61
   macro avg       0.45      0.45      0.45        61
weighted avg       0.46      0.46      0.46        61
```

## Confusion Matrices

- Technical Only: `confusion_matrix_technical_sp500_intraday.png`
- Sentiment Only: `confusion_matrix_sentiment_sp500_intraday.png`
- Technical + Sentiment: `confusion_matrix_combined_sp500_intraday.png`

---

**Generated**: 2026-02-23 18:17:19