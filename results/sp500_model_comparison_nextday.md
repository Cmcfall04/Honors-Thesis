# Model Comparison: Technical vs Sentiment vs Combined (Next-Day (S&P 500) Prediction)

## Experimental Design

- **Prediction Target**: Next-Day (S&P 500) price movement
- **Split Method**: Time-based (first 70% train, last 30% test)
- **Feature Scaling**: StandardScaler (mean=0, std=1) applied to all features
- **Train Period**: 2024-01-30 to 2024-09-30
- **Test Period**: 2024-10-01 to 2024-12-27
- **Train Samples**: 140
- **Test Samples**: 61
- **Technical Features**: return_1d, price_vs_sma20, rsi_change
- **Sentiment Features**: avg_positive, avg_negative, avg_neutral

## Results Summary

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Train Size | Test Size |
|-------|----------|----------------|-------------|---------------|------------|-----------|
| Technical Only | 47.54% | 55.56% | 42.86% | 48.39% | 140 | 61 |
| Sentiment Only | 40.98% | 48.57% | 48.57% | 48.57% | 140 | 61 |
| Technical + Sentiment | 47.54% | 55.56% | 42.86% | 48.39% | 140 | 61 |

## Cross-Validation Results

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Folds |
|-------|----------|----------------|-------------|---------------|-------|
| Technical Only | 49.70% ± 3.09% | 59.99% ± 8.60% | 45.77% ± 7.84% | 51.51% ± 6.75% | 5 |
| Sentiment Only | 50.30% ± 11.27% | 60.19% ± 13.30% | 50.67% ± 7.92% | 54.87% ± 9.96% | 5 |
| Technical + Sentiment | 47.27% ± 4.54% | 56.51% ± 8.59% | 46.88% ± 9.39% | 50.88% ± 7.77% | 5 |

**Note**: Cross-validation provides a more robust estimate of model performance by testing on multiple time-based splits. The standard deviation indicates stability across different time periods.


## Analysis

### Key Findings

1. **Technical-only model accuracy**: 47.54%
2. **Sentiment-only model accuracy**: 40.98%
3. **Combined model accuracy**: 47.54%

- Technical indicators **outperform** sentiment alone by 6.56 percentage points
- Combining features does **not improve** over the best individual model

### Marginal Contribution of Sentiment

Adding sentiment to technical indicators provides **no change** in accuracy.

## Statistical Significance

**McNemar's Test** (tests if model differences are statistically significant):

### Technical Only vs Combined

- Technical correct, Combined wrong: 2 cases
- Technical wrong, Combined correct: 2 cases
- **p-value: 1.0000**
- **Result**: No significant difference (p >= 0.05)

### Sentiment Only vs Combined

- Sentiment correct, Combined wrong: 12 cases
- Sentiment wrong, Combined correct: 16 cases
- **p-value: 0.5716**
- **Result**: No significant difference (p >= 0.05)

### Technical Only vs Sentiment Only

- Technical correct, Sentiment wrong: 18 cases
- Technical wrong, Sentiment correct: 14 cases
- **p-value: 0.5966**
- **Result**: No significant difference (p >= 0.05)

**Interpretation**: McNemar's test compares two models on the same test cases. A p-value < 0.05 means the performance difference is statistically significant (not due to chance).

## Detailed Classification Reports

### Technical Only

```
precision    recall  f1-score   support

   Down/Flat       0.41      0.54      0.47        26
          Up       0.56      0.43      0.48        35

    accuracy                           0.48        61
   macro avg       0.48      0.48      0.48        61
weighted avg       0.49      0.48      0.48        61
```

### Sentiment Only

```
precision    recall  f1-score   support

   Down/Flat       0.31      0.31      0.31        26
          Up       0.49      0.49      0.49        35

    accuracy                           0.41        61
   macro avg       0.40      0.40      0.40        61
weighted avg       0.41      0.41      0.41        61
```

### Technical + Sentiment

```
precision    recall  f1-score   support

   Down/Flat       0.41      0.54      0.47        26
          Up       0.56      0.43      0.48        35

    accuracy                           0.48        61
   macro avg       0.48      0.48      0.48        61
weighted avg       0.49      0.48      0.48        61
```

## Confusion Matrices

- Technical Only: `confusion_matrix_technical_sp500_nextday.png`
- Sentiment Only: `confusion_matrix_sentiment_sp500_nextday.png`
- Technical + Sentiment: `confusion_matrix_combined_sp500_nextday.png`

---

**Generated**: 2026-02-23 18:17:18