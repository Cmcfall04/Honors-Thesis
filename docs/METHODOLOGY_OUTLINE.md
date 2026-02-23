# Methodology Outline for Thesis

## Overview
This document provides a comprehensive outline for writing the Methodology section (Chapter 3) of your honors thesis. All technical details, formulas, and implementation specifics are included.

---

## 3.1 Research Design Overview

### Framework
- **Prediction Task**: Binary classification of next-day stock price movement
- **Target Variable**: Whether Close[t+1] > Close[t] (1 = up, 0 = down/flat)
- **Prediction Horizon**: One trading day ahead (t+1)
- **Asset**: Apple Inc. (AAPL) - S&P 500 component
- **Time Period**: January 2024 - December 2024 (1 year)
- **Approach**: Supervised machine learning with time-series cross-validation

### Rationale for Next-Day Prediction
Next-day prediction was chosen to test the Efficient Market Hypothesis (EMH) in its semi-strong form. According to EMH, publicly available information (including news headlines) should be immediately incorporated into stock prices, making next-day predictions unpredictable. This design allows us to directly test whether sentiment analysis provides any predictive advantage over technical indicators alone.

---

## 3.2 Data Collection

### 3.2.1 News Headlines Data
**Source**: Yahoo Finance Headlines
- **URL**: `https://finance.yahoo.com/quote/AAPL/news`
- **Method**: Web scraping using Python's `requests` and `BeautifulSoup` libraries
- **Frequency**: Daily aggregation
- **Content**: Financial news headlines specifically tagged to AAPL

**Data Fields Extracted**:
- Headline text (cleaned and preprocessed)
- Publication date (timestamp)
- Source attribution (news outlet)

**Preprocessing Steps**:
1. HTML parsing to extract `<h3>` tags containing headlines
2. Date extraction from `<time>` tags
3. Removal of duplicates
4. Filtering for date range (January - December 2024)

**Sample Size**: 158 headlines (after merging with trading days)

### 3.2.2 Stock Price Data
**Source**: Yahoo Finance via `yfinance` Python library
- **Ticker**: AAPL
- **Date Range**: January 2, 2024 - December 20, 2024
- **Frequency**: Daily (end-of-day data)

**OHLCV Fields**:
- **Open**: Opening price
- **High**: Intraday high price
- **Low**: Intraday low price
- **Close**: Closing price (adjusted for splits/dividends)
- **Volume**: Number of shares traded

**Sample Size**: 158 trading days (accounting for weekends and market holidays)

---

## 3.3 Sentiment Analysis

### 3.3.1 FinBERT Model
**Model**: FinBERT (Financial BERT) by Araci (2019)
- **Base Architecture**: BERT-base-uncased (12 layers, 110M parameters)
- **Fine-tuning Dataset**: Financial PhraseBank (4,840 sentences from financial news)
- **Task**: Three-class sentiment classification (positive, negative, neutral)
- **Implementation**: Hugging Face Transformers library (`ProsusAI/finbert`)

**Model Specifications**:
- **Input**: Tokenized headline text (max 512 tokens)
- **Output**: Softmax probability distribution over 3 classes
- **Label Order**: `["neutral", "positive", "negative"]` (index 0, 1, 2)
  - Index 0: Neutral
  - Index 1: Positive
  - Index 2: Negative

### 3.3.2 Sentiment Feature Engineering
For each trading day, multiple headlines were aggregated using **mean of probabilities**:

**Daily Sentiment Features**:
```
avg_positive = Σ(positive_probability_i) / n
avg_negative = Σ(negative_probability_i) / n
avg_neutral = Σ(neutral_probability_i) / n
```
where:
- `positive_probability_i` = FinBERT softmax probability for "positive" class
- `negative_probability_i` = FinBERT softmax probability for "negative" class
- `neutral_probability_i` = FinBERT softmax probability for "neutral" class
- `n` = number of headlines on that day

**Sentiment Features Used**:
- `avg_positive`: Mean probability of positive sentiment (0 to 1)
- `avg_negative`: Mean probability of negative sentiment (0 to 1)
- `avg_neutral`: Mean probability of neutral sentiment (0 to 1)

**Note**: This approach uses the raw probability scores from FinBERT rather than converting to discrete labels (-1/0/+1) first. This preserves the model's confidence information.

**Handling Missing Days**: Days without headlines are dropped during the inner join with stock data (only trading days with headlines are included).

---

## 3.4 Technical Indicators

Three momentum-based technical indicators were selected based on their relevance to short-term price prediction and low multicollinearity:

### 3.4.1 One-Day Return (`return_1d`)
**Formula**:
```
return_1d[t] = (Close[t] - Close[t-1]) / Close[t-1]
```

**Interpretation**: Percentage change in closing price from previous day

**Rationale**: Captures immediate price momentum; stocks with recent gains/losses may continue trending (momentum effect) or revert (mean reversion).

**Range**: Typically -0.10 to +0.10 (-10% to +10% daily change)

---

### 3.4.2 Relative Position to 20-Day SMA (`price_vs_sma20`)
**Formula**:
```
SMA_20[t] = (1/20) × Σ(Close[t-i]) for i=0 to 19

price_vs_sma20[t] = (Close[t] - SMA_20[t]) / SMA_20[t]
```

**Interpretation**: How far the current price deviates from its 20-day moving average

**Rationale**: 
- Positive values → Stock trading above trend (potential overbought)
- Negative values → Stock trading below trend (potential oversold)
- Captures mean reversion signals

**Range**: Typically -0.15 to +0.15 (-15% to +15% from 20-day average)

---

### 3.4.3 RSI Momentum Change (`rsi_change`)
**Formula**:
```
RSI_14[t] = 100 - (100 / (1 + RS[t]))

where:
RS[t] = AvgGain[t] / AvgLoss[t]
AvgGain[t] = (1/14) × Σ(positive_price_changes over 14 days)
AvgLoss[t] = (1/14) × Σ(absolute_negative_price_changes over 14 days)

rsi_change[t] = RSI_14[t] - RSI_14[t-1]
```

**Interpretation**: Daily change in Relative Strength Index

**Rationale**: 
- Positive values → Momentum accelerating upward
- Negative values → Momentum decelerating or reversing
- Captures momentum acceleration (not just level)

**Range**: -20 to +20 (RSI scale: 0-100, but daily changes are smaller)

---

### 3.4.4 Indicator Selection Rationale
These three indicators were chosen after iterative experimentation:

**Why Not More Indicators?**
- Initial experiments with 8 indicators (SMA_20, SMA_50, RSI_14, MACD line/signal/histogram, Bollinger Band width, volume ratio) showed:
  - High multicollinearity between level-based indicators
  - Absolute values (e.g., SMA_50) not suitable for next-day prediction
  - Poor generalization on test data

**Why These Three?**
1. ✅ **Low correlation**: Capture different aspects (momentum, mean reversion, acceleration)
2. ✅ **Short-term focus**: Relevant for one-day-ahead prediction
3. ✅ **Normalized scales**: All expressed as percentage changes or differences
4. ✅ **Literature support**: Widely used in quantitative finance

---

## 3.5 Feature Engineering and Data Merging

### 3.5.1 Time-Based Merging
Stock price data and sentiment data were merged on the `date` field using an **inner join** (`how="inner"`). This ensures that only trading days with both stock data AND sentiment data are included.

**Key Considerations**:
- **Non-trading days**: Headlines published on weekends/holidays are dropped (no corresponding stock data)
- **Look-ahead prevention**: News headlines published after market close on day `t` were aligned to day `t`, ensuring no look-ahead bias
- **Target variable**: Uses `Close[t+1]`, which is unavailable at prediction time

### 3.5.2 Feature Scaling
**Method**: Standardization (Z-score normalization) using `StandardScaler` from scikit-learn

**Formula**:
```
X_scaled = (X - μ) / σ

where:
μ = mean of feature in training set
σ = standard deviation of feature in training set
```

**Rationale**: 
- Logistic Regression is sensitive to feature scales
- Prevents large-scale features (e.g., technical indicators) from dominating small-scale features (e.g., sentiment scores)
- Fitted on training set only, then applied to test set (prevents data leakage)

**Application**:
- Separate scalers for each feature set (sentiment-only, technical-only, combined)
- Applied after train/test split

### 3.5.3 Handling Missing Values
- **Technical Indicators**: First 20 rows contain NaN due to rolling window calculations (SMA_20 requires 20 days, RSI_14 requires 14 days)
- **Sentiment Features**: Days without headlines are dropped during inner join with stock data
- **Final Dataset**: Only complete cases retained after dropping NaN rows from technical indicators

**Final Sample Size**: 143 trading days with complete feature sets (158 raw - 15 NaN = 143)

---

## 3.6 Target Variable Construction

### Next-Day Price Movement
**Binary Classification Target**:
```python
next_close[t] = Close[t+1]  # Shifted by -1 period
stock_move_nextday[t] = 1 if next_close[t] > Close[t] else 0
```

**Label Distribution**:
- Class 1 (Up): Stock closes higher tomorrow than today
- Class 0 (Down/Flat): Stock closes lower or unchanged tomorrow

**Data Leakage Prevention**:
- `Close[t+1]` is ONLY used for the target variable
- No `shift(-1)` operations on features
- All technical indicators calculated using data through `Close[t]` only

---

## 3.7 Model Architecture

### 3.7.1 Logistic Regression
**Algorithm**: Logistic Regression (binary classifier)
- **Implementation**: `LogisticRegression` from scikit-learn
- **Solver**: `lbfgs` (Limited-memory BFGS, default)
- **Max Iterations**: 1000 (ensures convergence)
- **Regularization**: L2 (default, C=1.0)
- **Random State**: 42 (reproducibility)

**Note**: Only Logistic Regression was used in this study. No other models (e.g., Random Forest, SVM) were evaluated, as the focus was on establishing a baseline comparison between feature sets rather than optimizing model architecture.

**Model Equation**:
```
P(Y=1|X) = 1 / (1 + e^(-z))

where:
z = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ

Decision Rule:
ŷ = 1 if P(Y=1|X) ≥ 0.5, else 0
```

**Rationale for Logistic Regression**:
- Interpretable coefficients (feature importance)
- Well-established baseline for binary classification
- Fast training and prediction
- Suitable for comparing feature sets directly

### 3.7.2 Feature Set Configurations
Three models were trained to isolate the contribution of each feature type:

1. **Sentiment-Only Model**
   - Features: `sentiment_avg`, `sentiment_positive`, `sentiment_negative`, `sentiment_neutral` (4 features)
   - Tests: Does news sentiment alone predict next-day movement?

2. **Technical-Only Model**
   - Features: `return_1d`, `price_vs_sma20`, `rsi_change` (3 features)
   - Tests: Does price history alone predict next-day movement?

3. **Combined Model**
   - Features: All sentiment + all technical features (7 features total)
   - Tests: Does adding sentiment improve technical predictions?

---

## 3.8 Evaluation Strategy

### 3.8.1 Train/Test Split
**Method**: Time-based split (chronological)
- **Training Set**: First 70% of data (~January - August 2024)
- **Test Set**: Last 30% of data (~August - December 2024)
- **Rationale**: Simulates realistic forward-looking prediction; avoids look-ahead bias

**Split Details**:
```
Total samples: N
Train: N × 0.7 (sorted by date, earliest 70%)
Test: N × 0.3 (sorted by date, most recent 30%)
```

**Why Not Random Split?**
Time-series data has temporal dependencies. Random splitting would leak future information into training (e.g., training on 2023, testing on 2020).

### 3.8.2 Cross-Validation
**Method**: Time-Series Cross-Validation (TimeSeriesSplit)
- **Number of Folds**: 5
- **Strategy**: Expanding window (train on increasing data, test on next chunk)

**Fold Structure**:
```
Fold 1: Train [──────────] Test [──]
Fold 2: Train [───────────────] Test [──]
Fold 3: Train [──────────────────────] Test [──]
Fold 4: Train [─────────────────────────────] Test [──]
Fold 5: Train [────────────────────────────────────] Test [──]
```

**Rationale**: 
- Provides robust performance estimates (mean ± std)
- Accounts for temporal variation in market conditions
- Mimics realistic forward-looking deployment

**Metrics Reported**:
- Mean accuracy/precision/recall/F1 across 5 folds
- Standard deviation (measure of consistency)

### 3.8.3 Evaluation Metrics

**1. Accuracy**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```
Overall correctness of predictions.

**2. Precision**
```
Precision = TP / (TP + FP)
```
Of predicted "up" days, how many were actually up?

**3. Recall (Sensitivity)**
```
Recall = TP / (TP + FN)
```
Of actual "up" days, how many did we catch?

**4. F1-Score**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
Harmonic mean of precision and recall (balanced metric).

**Confusion Matrix Terms**:
- **TP (True Positive)**: Predicted up, actually up
- **TN (True Negative)**: Predicted down, actually down
- **FP (False Positive)**: Predicted up, actually down (Type I error)
- **FN (False Negative)**: Predicted down, actually up (Type II error)

---

## 3.9 Statistical Significance Testing

### McNemar's Test
**Purpose**: Test whether two models' predictions differ significantly

**Null Hypothesis (H₀)**: The two models have the same error rate
**Alternative Hypothesis (H₁)**: The models have different error rates

**Test Statistic**:
```
Contingency Table:
                Model 2 Correct  |  Model 2 Wrong
Model 1 Correct       a          |       b
Model 1 Wrong         c          |       d

McNemar χ² = (|b - c| - 1)² / (b + c)

where b and c are discordant pairs (one correct, one wrong)
```

**Decision Rule**:
- If p-value < 0.05 → Reject H₀ (models significantly different)
- If p-value ≥ 0.05 → Fail to reject H₀ (no significant difference)

**Comparisons Made**:
1. Sentiment-Only vs. Technical-Only
2. Technical-Only vs. Combined
3. Sentiment-Only vs. Combined

**Rationale**: 
- More appropriate than accuracy difference for paired predictions
- Accounts for model agreement/disagreement on individual samples
- Standard test in machine learning model comparison

---

## 3.10 Implementation Details

### 3.10.1 Software and Libraries
**Programming Language**: Python 3.x

**Key Libraries**:
- `pandas`: Data manipulation and merging
- `numpy`: Numerical computations
- `yfinance`: Stock data retrieval
- `requests`, `BeautifulSoup`: Web scraping
- `transformers`: FinBERT sentiment analysis
- `scikit-learn`: Logistic Regression, StandardScaler, metrics
- `matplotlib`, `seaborn`: Visualization

### 3.10.2 Reproducibility
- **Random Seed**: 42 (used for train/test split and model initialization)
- **Version Control**: All code available in project repository
- **Environment**: Virtual environment with `requirements.txt`

---

## 3.11 Data Leakage Prevention Checklist

✅ **Target Variable**: `Close[t+1]` only used for label, never as feature
✅ **Feature Scaling**: Fitted on training data only, then applied to test data
✅ **Time-Based Split**: Training always precedes test data chronologically
✅ **No Forward-Looking Features**: Technical indicators use data through `t` only
✅ **Cross-Validation**: TimeSeriesSplit ensures no future data in training folds
✅ **Sentiment Alignment**: Headlines from day `t` predict movement at `t+1`

---

## 3.12 Limitations and Assumptions

### Assumptions
1. **Market Efficiency**: Tests semi-strong form EMH (public information)
2. **Single Asset**: Focuses on AAPL (highly liquid, widely covered)
3. **News Impact**: Assumes headlines contain relevant sentiment signals
4. **Linear Relationships**: Logistic Regression assumes linear decision boundaries
5. **Transaction Costs Ignored**: Does not account for trading fees or slippage

### Limitations
1. **Sample Size**: Limited to 1 year of data (158 trading days) - relatively small for robust ML training
2. **Time Period**: Single calendar year (2024) - may not capture diverse market conditions (bull/bear cycles)
3. **Class Imbalance**: Stock may have unequal up/down days
4. **External Factors**: Does not include macroeconomic indicators, earnings reports, or broader market sentiment
5. **Headline Selection**: Only Yahoo Finance headlines (potential selection bias)
6. **Model Complexity**: Simple baseline model (more complex architectures not explored)

---

## 3.13 Summary

This methodology implements a rigorous evaluation of sentiment analysis for next-day stock price prediction using:
- **7 features** (4 sentiment + 3 technical indicators)
- **1 machine learning model** (Logistic Regression)
- **Robust evaluation** (holdout test + 5-fold CV + McNemar's test)
- **Clear hypothesis**: Can news sentiment improve next-day predictions beyond technical indicators?

The design directly tests the Efficient Market Hypothesis by examining whether publicly available sentiment provides predictive power for next-day price movements.

---

## Quick Reference: Key Numbers for Writing

| Metric | Value |
|--------|-------|
| Time Period | January - December 2024 (1 year) |
| Asset | AAPL |
| Raw Trading Days | 158 |
| Final Sample Size (after dropping NaN) | 143 |
| Train/Test Split | 70% / 30% |
| Train Samples | 100 |
| Test Samples | 43 |
| Train/Test Split | 80% / 20% |
| CV Folds | 5 |
| Sentiment Features | 4 |
| Technical Features | 3 |
| Total Features (Combined) | 7 |
| Model | Logistic Regression |
| Target | Next-day price movement (binary) |
| Significance Level | α = 0.05 |

---

## Notes for Thesis Writing

1. **Cite FinBERT**: Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. arXiv:1908.10063.

2. **Justify Choices**: For each methodological decision, explain WHY (e.g., "Logistic Regression was chosen as a baseline due to its interpretability and established use in financial prediction tasks").

3. **Be Specific**: Use exact formulas, parameter values, and library versions where possible.

4. **Link to EMH**: Throughout, connect your choices back to testing the Efficient Market Hypothesis.

5. **Acknowledge Limitations**: Show you understand the constraints of your approach.

Good luck with your writing! 📚✨
