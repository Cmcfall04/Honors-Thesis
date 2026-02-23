# Model Comparison: Technical vs Sentiment vs Combined (Intraday Prediction)

## Experimental Design

- **Prediction Target**: Intraday price movement
- **Split Method**: Time-based (first 70% train, last 30% test)
- **Feature Scaling**: StandardScaler (mean=0, std=1) applied to all features
- **Train Period**: 2024-02-01 to 2024-08-29
- **Test Period**: 2024-08-30 to 2024-12-23
- **Train Samples**: 100
- **Test Samples**: 43
- **Technical Features**: overnight_gap, open_vs_sma20, rsi_change_lag1
- **Sentiment Features**: avg_positive, avg_negative, avg_neutral

## Results Summary

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Train Size | Test Size |
|-------|----------|----------------|-------------|---------------|------------|-----------|
| Technical Only | 48.84% | 68.42% | 44.83% | 54.17% | 100 | 43 |
| Sentiment Only | 62.79% | 78.26% | 62.07% | 69.23% | 100 | 43 |
| Technical + Sentiment | 55.81% | 70.83% | 58.62% | 64.15% | 100 | 43 |

## Cross-Validation Results

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Folds |
|-------|----------|----------------|-------------|---------------|-------|
| Technical Only | 45.22% ± 12.48% | 44.30% ± 29.43% | 37.50% ± 19.88% | 38.91% ± 23.40% | 5 |
| Sentiment Only | 47.83% ± 13.75% | 55.87% ± 21.06% | 50.26% ± 11.96% | 50.80% ± 15.18% | 5 |
| Technical + Sentiment | 50.43% ± 10.86% | 64.15% ± 19.28% | 47.18% ± 18.48% | 48.63% ± 14.78% | 5 |

**Note**: Cross-validation provides a more robust estimate of model performance by testing on multiple time-based splits. The standard deviation indicates stability across different time periods.


## Analysis

### Key Findings

1. **Technical-only model accuracy**: 48.84%
2. **Sentiment-only model accuracy**: 62.79%
3. **Combined model accuracy**: 55.81%

- Sentiment features **outperform** technical indicators by 13.95 percentage points
- Combining features does **not improve** over the best individual model

### Marginal Contribution of Sentiment

Adding sentiment to technical indicators provides a **+6.98pp** improvement.

## Statistical Significance

**McNemar's Test** (tests if model differences are statistically significant):

### Technical Only vs Combined

- Technical correct, Combined wrong: 5 cases
- Technical wrong, Combined correct: 8 cases
- **p-value: 0.5811**
- **Result**: No significant difference (p >= 0.05)

### Sentiment Only vs Combined

- Sentiment correct, Combined wrong: 5 cases
- Sentiment wrong, Combined correct: 2 cases
- **p-value: 0.4531**
- **Result**: No significant difference (p >= 0.05)

### Technical Only vs Sentiment Only

- Technical correct, Sentiment wrong: 7 cases
- Technical wrong, Sentiment correct: 13 cases
- **p-value: 0.2632**
- **Result**: No significant difference (p >= 0.05)

**Interpretation**: McNemar's test compares two models on the same test cases. A p-value < 0.05 means the performance difference is statistically significant (not due to chance).

## Detailed Classification Reports

### Technical Only

```
precision    recall  f1-score   support

   Down/Flat       0.33      0.57      0.42        14
          Up       0.68      0.45      0.54        29

    accuracy                           0.49        43
   macro avg       0.51      0.51      0.48        43
weighted avg       0.57      0.49      0.50        43
```

### Sentiment Only

```
precision    recall  f1-score   support

   Down/Flat       0.45      0.64      0.53        14
          Up       0.78      0.62      0.69        29

    accuracy                           0.63        43
   macro avg       0.62      0.63      0.61        43
weighted avg       0.67      0.63      0.64        43
```

### Technical + Sentiment

```
precision    recall  f1-score   support

   Down/Flat       0.37      0.50      0.42        14
          Up       0.71      0.59      0.64        29

    accuracy                           0.56        43
   macro avg       0.54      0.54      0.53        43
weighted avg       0.60      0.56      0.57        43
```

## Confusion Matrices

- Technical Only: `confusion_matrix_technical_intraday.png`
- Sentiment Only: `confusion_matrix_sentiment_intraday.png`
- Technical + Sentiment: `confusion_matrix_combined_intraday.png`

---

**Generated**: 2026-02-22 16:31:03