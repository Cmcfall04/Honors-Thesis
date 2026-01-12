# Experimental Design: Technical Indicators + Sentiment Analysis

**Date:** January 12, 2026  
**Status:** 📋 Planning Phase  
**Objective:** Compare three models to evaluate if sentiment adds incremental signal beyond technical indicators

---

## Goal

Run three comparable models on the same date range and split:

1. **Technical indicators only** → predict next-day Up/Down
2. **Sentiment features only** → you already have this baseline
3. **Technical + sentiment** → see if sentiment adds incremental signal

Keep everything else identical (same labels, same train/test split, same metrics).

---

## Technical Indicators to Add

### Selection Criteria

Use indicators that are:
- Common in finance research
- Easy to compute
- Unlikely to explode your scope

### Recommended Feature Set

#### Price/Trend
- **Return (1-day)**: today's close vs yesterday's close
- **SMA 5, SMA 10**: short-term trend
- **EMA 5, EMA 10**: trend with more weight on recent days

#### Momentum
- **RSI (14)**: overbought/oversold (classic)

#### Volatility
- **Rolling std of returns (10)**: short-term realized volatility

#### Volume
- **Volume change (1-day)** or **Volume SMA (10)** (if you have volume in your yfinance pull)

That's enough to make your experiment meaningful without becoming a full quant project.

---

## Sentiment Features (What You Already Have)

From your pipeline summary, you currently have:
- `avg_positive`
- `avg_negative`
- `avg_neutral`
- `headline_count`

**Keep these exactly as-is for the combined model.**

---

## Experimental Design (Keep It Clean)

### Target Label

Same as before: `Stock_Move = 1` if next-day Close > today's Close else `0`

### Split

Use **time-based split**, not random (avoid leakage):
- **Train**: first ~70%
- **Test**: last ~30%

### Models (Start Simple)

Use 1–2 models max so the thesis stays tight:
- **Logistic Regression** (best baseline, interpretable)
- **Optional**: Random Forest as a nonlinear comparison

---

## What You Should Expect

- **Technical-only** might land around ~50–58% depending on year and market regime.
- **Technical + sentiment** might improve slightly, or not at all.
- Even "no improvement" is still a valid result, as long as your method is sound.

---

## Concrete Next Steps Checklist

### 1. Compute Technical Features from OHLCV
- [ ] Returns (1-day)
- [ ] SMA 5, SMA 10
- [ ] EMA 5, EMA 10
- [ ] RSI (14)
- [ ] Rolling std of returns (10)
- [ ] Volume change (1-day) or Volume SMA (10)

### 2. Data Preparation
- [ ] Align features to dates
- [ ] Drop rows with NaNs from rolling windows

### 3. Build Datasets
- [ ] `X_tech` (technical indicators only)
- [ ] `X_sent` (sentiment features only - already exists)
- [ ] `X_tech_sent` (technical + sentiment combined)
- [ ] Same `y` (target labels) for all three

### 4. Model Training & Evaluation
- [ ] Train/evaluate each model with the same split
- [ ] Use identical train/test split for all three models
- [ ] Calculate same metrics for all models

### 5. Results Comparison
- [ ] Create comparison table with:
  - Accuracy
  - Precision
  - Recall
  - F1-Score
- [ ] Add one short analysis paragraph:
  - Did sentiment add marginal value beyond technicals?

---

## Expected Output Structure

### Results Table Format

| Model | Accuracy | Precision (Up) | Recall (Up) | F1-Score (Up) | Notes |
|-------|----------|----------------|-------------|---------------|-------|
| Technical Only | TBD | TBD | TBD | TBD | Baseline with market indicators |
| Sentiment Only | 35.42% | 41.94% | 50.00% | 45.61% | Current baseline (from bug fix) |
| Technical + Sentiment | TBD | TBD | TBD | TBD | Combined features |

### Analysis Questions

1. Does technical-only outperform sentiment-only?
2. Does adding sentiment to technical indicators improve performance?
3. What is the marginal contribution of sentiment features?
4. Are the improvements statistically significant?

---

## Implementation Notes

### Technical Indicator Calculations

All indicators should be calculated from the stock data already available in the pipeline:
- Use `yfinance` data (OHLCV) that's already being downloaded
- Calculate indicators using `pandas` and `ta-lib` (if needed) or manual calculations
- Ensure all indicators are aligned to the same date index

### Feature Alignment

- Technical indicators: calculated from stock price data
- Sentiment features: already aggregated by date
- Merge on date to create combined dataset
- Handle missing values appropriately (drop NaNs from rolling windows)

### Model Consistency

- Same random seed for reproducibility
- Same train/test split (time-based, not random)
- Same evaluation metrics
- Same preprocessing steps (scaling, if needed)

---

## Success Criteria

### Minimum Viable Experiment

✅ Three models trained and evaluated  
✅ Results table comparing all three approaches  
✅ Clear answer to: "Does sentiment add value beyond technical indicators?"

### Thesis Value

- **If sentiment adds value**: Demonstrates multimodal approach is beneficial
- **If sentiment doesn't add value**: Validates that technical indicators capture most signal, sentiment is redundant
- **Either outcome is valuable** for thesis discussion

---

## References

### Technical Indicators Literature

- RSI (Relative Strength Index): Classic momentum oscillator
- SMA/EMA: Standard trend-following indicators
- Rolling volatility: Common risk measure
- Volume indicators: Market participation metrics

### Related Work

- Many studies find technical indicators achieve 50-60% accuracy
- Sentiment-only models often struggle (35-45% range)
- Combined approaches show mixed results depending on market conditions

---

**Document Version:** 1.0  
**Last Updated:** January 12, 2026  
**Status:** Planning - Ready for Implementation
