# Model Comparison: Technical vs Sentiment vs Combined (Next-Day Prediction)

## Experimental Design

- **Prediction Target**: Next-Day price movement
- **Split Method**: Time-based (first 70% train, last 30% test)
- **Feature Scaling**: StandardScaler (mean=0, std=1) applied to all features
- **Train Period**: 2024-01-30 to 2024-08-28
- **Test Period**: 2024-08-29 to 2024-12-23
- **Train Samples**: 100
- **Test Samples**: 44
- **Technical Features**: return_1d, price_vs_sma20, rsi_change
- **Sentiment Features**: avg_positive, avg_negative, avg_neutral

## Results Summary

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Train Size | Test Size |
|-------|----------|----------------|-------------|---------------|------------|-----------|
| Technical Only | 50.00% | 59.26% | 59.26% | 59.26% | 100 | 44 |
| Sentiment Only | 43.18% | 53.33% | 59.26% | 56.14% | 100 | 44 |
| Technical + Sentiment | 45.45% | 55.17% | 59.26% | 57.14% | 100 | 44 |

## Cross-Validation Results

**5-Fold Time-Series Cross-Validation** (mean ± std across folds):

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Folds |
|-------|----------|----------------|-------------|---------------|-------|
| Technical Only | 45.83% ± 10.54% | 43.71% ± 27.67% | 40.09% ± 24.04% | 41.65% ± 25.42% | 5 |
| Sentiment Only | 46.67% ± 8.50% | 59.18% ± 12.77% | 41.60% ± 13.40% | 47.01% ± 9.79% | 5 |
| Technical + Sentiment | 45.00% ± 10.99% | 54.95% ± 13.68% | 42.83% ± 20.84% | 45.18% ± 17.68% | 5 |

**Note**: Cross-validation provides a more robust estimate of model performance by testing on multiple time-based splits. The standard deviation indicates stability across different time periods.


## Analysis

### Key Findings

1. **Technical-only model accuracy**: 50.00%
2. **Sentiment-only model accuracy**: 43.18%
3. **Combined model accuracy**: 45.45%

- Technical indicators **outperform** sentiment alone by 6.82 percentage points
- Combining features does **not improve** over the best individual model

### Marginal Contribution of Sentiment

Adding sentiment to technical indicators **decreases** performance by 4.55pp.

## Statistical Significance

**McNemar's Test** (tests if model differences are statistically significant):

### Technical Only vs Combined

- Technical correct, Combined wrong: 6 cases
- Technical wrong, Combined correct: 4 cases
- **p-value: 0.7539**
- **Result**: No significant difference (p >= 0.05)

### Sentiment Only vs Combined

- Sentiment correct, Combined wrong: 1 cases
- Sentiment wrong, Combined correct: 2 cases
- **p-value: 1.0000**
- **Result**: No significant difference (p >= 0.05)

### Technical Only vs Sentiment Only

- Technical correct, Sentiment wrong: 8 cases
- Technical wrong, Sentiment correct: 5 cases
- **p-value: 0.5811**
- **Result**: No significant difference (p >= 0.05)

**Interpretation**: McNemar's test compares two models on the same test cases. A p-value < 0.05 means the performance difference is statistically significant (not due to chance).

## Detailed Classification Reports

### Technical Only

```
precision    recall  f1-score   support

   Down/Flat       0.35      0.35      0.35        17
          Up       0.59      0.59      0.59        27

    accuracy                           0.50        44
   macro avg       0.47      0.47      0.47        44
weighted avg       0.50      0.50      0.50        44
```

### Sentiment Only

```
precision    recall  f1-score   support

   Down/Flat       0.21      0.18      0.19        17
          Up       0.53      0.59      0.56        27

    accuracy                           0.43        44
   macro avg       0.37      0.38      0.38        44
weighted avg       0.41      0.43      0.42        44
```

### Technical + Sentiment

```
precision    recall  f1-score   support

   Down/Flat       0.27      0.24      0.25        17
          Up       0.55      0.59      0.57        27

    accuracy                           0.45        44
   macro avg       0.41      0.41      0.41        44
weighted avg       0.44      0.45      0.45        44
```

## Confusion Matrices

- Technical Only: `confusion_matrix_technical_nextday.png`
- Sentiment Only: `confusion_matrix_sentiment_nextday.png`
- Technical + Sentiment: `confusion_matrix_combined_nextday.png`

---

**Generated**: 2026-02-22 16:31:02