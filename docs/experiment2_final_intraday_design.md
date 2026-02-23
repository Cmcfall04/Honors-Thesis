# Experiment 2: Pre-Market Intraday Prediction Design
## (News on Day t → Predict Open(t) to Close(t))

This document formally defines the final setup for Experiment 2, based on the following assumptions:

- Financial news dated day t is assumed to be available before market open or very early in the trading session.
- A trader can act at or near the market open.
- Technical indicators must reflect information available no later than the close of day t−1.

This experiment isolates the intraday reaction to news while avoiding look-ahead bias.

---

# 1. Objective

To test whether same-day financial news sentiment (assumed pre-market) improves prediction of intraday stock movement, defined as the direction from Open(t) to Close(t).

This experiment differs from Experiment 1, which predicts next-day close-to-close movement.

---

# 2. Target Variable (Intraday Direction)

For each trading day t, define:

y_t = 1 if Close_t > Open_t, else 0

Where:
- 1 = stock closes above its opening price (positive intraday return)
- 0 = stock closes below its opening price

This target reflects a strategy of entering at the open and exiting at the close.

---

# 3. Information Set Definition

The information set available before or at market open on day t is:

I_t = {Technicals at t−1, Sentiment at t}

This ensures no forward-looking bias.

---

# 4. Feature Construction

## 4.1 Sentiment Features (Same-Day)

Sentiment is aggregated from headlines dated day t using FinBERT probabilities:

- sent_pos_t
- sent_neg_t
- sent_neu_t
- (optional) n_headlines_t

These represent pre-market tone under the timing assumption.

---

## 4.2 Technical Indicators (Lagged by 1 Trading Day)

Use the exact same technical indicators as Experiment 1:

1. 1-day return
2. Distance from 20-day SMA
3. Change in 14-day RSI

These are computed exactly as before, but shifted one trading day backward:

- ret_lag1 = ret.shift(1)
- dist_sma20_lag1 = dist_sma20.shift(1)
- delta_rsi_lag1 = delta_rsi.shift(1)

This ensures that only information known by Close(t−1) is used.

---

# 5. Dataset Construction Steps

Step 1 – Start with trading-day price dataframe including:
- Date
- Open
- Close
- Technical indicators

Step 2 – Create intraday target:
y_intraday = (Close > Open).astype(int)

Step 3 – Merge sentiment on same calendar day:
Merge price Date with sentiment pub_date.

You may use:
- Inner join (predict only on news days)
- Left join with neutral fill (predict every trading day)

Be consistent with Experiment 1 for comparability.

Step 4 – Lag technical indicators:
ret_lag1 = ret.shift(1)
dist_sma20_lag1 = dist_sma20.shift(1)
delta_rsi_lag1 = delta_rsi.shift(1)

Step 5 – Drop invalid rows:
Remove:
- First row (no t−1 data)
- Rolling window NaNs
- Rows missing sentiment (if inner join)

Final dataset contains:
- Intraday target
- Same-day sentiment
- Lagged technicals

---

# 6. Model Configurations

Train the same three models as Experiment 1:

Model 1 – Sentiment Only
- sent_pos_t
- sent_neg_t
- sent_neu_t

Model 2 – Technical Only
- ret_lag1
- dist_sma20_lag1
- delta_rsi_lag1

Model 3 – Combined
- All sentiment + lagged technical features

Use identical:
- Chronological train/test split
- Z-score scaling (fit on training only)
- Logistic regression setup
- Evaluation metrics (accuracy, precision, recall, F1)
- McNemar test (Combined vs Technical)

---

# 7. Why Open-to-Close Is Preferred Here

Using Open(t) → Close(t):

- Matches the pre-market news availability assumption
- Avoids contamination from overnight gap effects
- Reflects a realistic intraday trading strategy
- Provides a clean test of immediate market reaction

Close-to-close would include overnight movement that may already incorporate news before the trading session.

---

# 8. Methodology Paragraph (Thesis-Ready)

To approximate a pre-market information setting, a second experiment was conducted in which same-day financial news sentiment was used to predict intraday stock movement. Because publication timestamps were not consistently available, headlines dated day t were treated as available prior to or near the market open. The target variable was defined as the sign of the return from Open(t) to Close(t), reflecting an intraday trading strategy. Technical indicators were computed using data through Close(t−1) and lagged one trading day to ensure that all features were observable prior to the start of trading on day t. This design isolates the intraday reaction to news while preventing look-ahead bias.

---

# 9. Final Experimental Summary

Experiment 1:
- News(t) → Predict Close(t+1) vs Close(t)

Experiment 2 (This Design):
- News(t) + Technicals(t−1) → Predict Close(t) vs Open(t)

Together, these experiments compare:
- Next-day persistence
- Same-day intraday reaction

Both use identical technical indicators and modeling procedures to isolate timing effects.

---

End of Experiment 2 Final Design
