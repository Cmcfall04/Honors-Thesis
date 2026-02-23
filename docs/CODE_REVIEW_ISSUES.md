# Code Review Issues — `scripts/main.py`

A record of the 8 issues identified during the post-implementation code review of both experiments. Each entry describes the problem, its impact, the resolution, and current status.

---

## Issue 1 — Incorrect `next_close` Target for Experiment 1

**Severity**: 🔴 Critical  
**Status**: ✅ Fixed

### Problem
`next_close` was computed by calling `.shift(-1)` on the **merged** DataFrame (i.e., after the inner join of stock data with sentiment). Because the inner join only retains days that have WSJ headlines, days without news are dropped. This meant that if no article appeared on, say, January 6, then January 7's `next_close` would shift back to January 5's close, silently skipping a trading day and creating a multi-day target.

### Impact
The target variable `stock_move_nextday` would sometimes represent a 2-, 3-, or even 4-day return rather than a true next-trading-day return, directly violating the experiment's stated objective.

### Fix
Moved the `next_close = stock_df["close"].shift(-1)` calculation onto the **full, consecutive stock DataFrame** *before* the merge with sentiment. This guarantees the shift always references the immediately following trading day regardless of sentiment coverage gaps.

---

## Issue 2 — No Class-Weight Balancing in Logistic Regression

**Severity**: 🟡 Moderate  
**Status**: ✅ Fixed

### Problem
All `LogisticRegression` instances were constructed without `class_weight='balanced'`. When one class (e.g., "Up" days) outnumbers the other, an unweighted classifier is incentivised to always predict the majority class and can still achieve deceptively high accuracy while providing zero useful signal.

### Impact
Models could appear to perform reasonably in accuracy terms while having near-zero recall for the minority class — a degenerate outcome that inflates reported metrics and undermines the experiment's validity.

### Fix
Added `class_weight='balanced'` to every `LogisticRegression(...)` call in both `evaluate_models_with_cv()` and `train_comparison_models()`. This causes scikit-learn to inversely weight each class by its frequency, penalising errors on the minority class proportionally more.

```python
# Before
model = LogisticRegression(max_iter=1000, random_state=42)

# After
model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
```

---

## Issue 3 — RSI Used Simple Rolling Mean Instead of Wilder's EMA

**Severity**: 🟡 Moderate  
**Status**: ✅ Fixed

### Problem
The `calculate_technical_indicators()` function computed the RSI average gain and loss using `.rolling(window=14).mean()`, which is a simple moving average (SMA). The standard RSI definition (Wilder, 1978) uses an exponential moving average with a smoothing factor of `α = 1/14`.

### Impact
The `RSI_14` values produced were systematically different from those reported by financial data platforms (Bloomberg, Yahoo Finance, etc.), making the feature inconsistent with the literature and reducing its comparability to other studies.

### Fix
Replaced the simple rolling mean with `.ewm(alpha=1/14, min_periods=14, adjust=False).mean()` for both `gain` and `loss`:

```python
# Before
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

# After (Wilder's EMA)
gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
```

---

## Issue 4 — No Majority-Class Baseline Reporter

**Severity**: 🟢 Minor  
**Status**: ⏳ Deferred

### Problem
Neither experiment reports a naïve majority-class baseline (i.e., "always predict Up"). Without it, there is no lower bound against which to compare the trained models, making it possible for a degenerate classifier to look competitive.

### Impact
Readers cannot immediately tell whether 54% accuracy is meaningfully better than simply guessing the most common class every time. Note: the CV results (~45–48%) are actually *below* the naive majority-class baseline (~54%), which is an important finding that should be explicitly stated in the thesis.

### Planned Fix
Add a `DummyClassifier(strategy='most_frequent')` result row to the results summary tables in both experiments. Deferred to a future iteration.

---

## Issue 5 — `headline_count` as a Feature

**Severity**: 🟢 Minor  
**Status**: ✅ Resolved (removed as feature)

### Problem
`n_headlines` (the daily headline count) was considered for inclusion as a model feature. While news volume can carry a signal (high volume may indicate heightened uncertainty), it is more naturally interpreted as metadata about data quality than as a directional price predictor.

### Resolution
`n_headlines` is retained in the merged datasets as a metadata/diagnostic column but is **not passed to any model** as an input feature. This keeps the feature sets clean and the experiments interpretable: Sentiment Only uses only FinBERT probabilities; Technical Only uses only price-derived indicators.

---

## Issue 6 — No Direct Technical vs. Sentiment McNemar Test

**Severity**: 🟢 Minor  
**Status**: ✅ Fixed

### Problem
The McNemar's test was run for:
- Technical Only vs. Combined
- Sentiment Only vs. Combined

But there was no direct head-to-head test between **Technical Only vs. Sentiment Only**, which is arguably the most theoretically interesting comparison in the context of the Efficient Market Hypothesis.

### Fix
Added a third McNemar test (Test 3) in `train_comparison_models()` comparing `predictions['Technical Only']` vs `predictions['Sentiment Only']` directly. Both `tech_correct` and `sent_correct` arrays are already computed by Tests 1 and 2, so Test 3 reuses them with no redundant model predictions. The result is rendered in both the console output and the markdown report under a new `### Technical Only vs Sentiment Only` section.

---

## Issue 7 — Intraday Report Referenced Wrong Confusion Matrix Filenames

**Severity**: 🔴 Critical  
**Status**: ✅ Fixed

### Problem
The `model_comparison_intraday.md` report was generated with hardcoded references to `confusion_matrix_technical_nextday.png`, `confusion_matrix_sentiment_nextday.png`, and `confusion_matrix_combined_nextday.png` — the **next-day** files — instead of the correct `_intraday` variants.

### Impact
Anyone reading the intraday report and opening the linked confusion matrices would see the wrong figures, silently misrepresenting the intraday model's prediction behaviour.

### Fix
Parameterised the filename suffix in `train_comparison_models()` using a `cm_suffix` argument (`'nextday'` or `'intraday'`). The markdown now dynamically builds the correct filenames:

```python
f"confusion_matrix_technical_{cm_suffix}.png"
f"confusion_matrix_sentiment_{cm_suffix}.png"
f"confusion_matrix_combined_{cm_suffix}.png"
```

---

## Issue 8 — Dead Code: `train_baseline_model()`

**Severity**: 🟢 Minor  
**Status**: ✅ Fixed

### Problem
A `train_baseline_model()` function existed in `main.py` but was never called anywhere in the pipeline. It also referenced a non-existent column name and used a random (non-chronological) train/test split — both methodologically incorrect for time-series data.

The associated `from sklearn.model_selection import train_test_split` import was also unused as a result.

### Impact
Dead code increases maintenance burden, creates confusion about the intended pipeline, and risks accidental future use of a broken, methodologically unsound function.

### Fix
Removed `train_baseline_model()` entirely and removed the now-unused `train_test_split` import from the top of `main.py`.

---

## Summary Table

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `next_close` computed on gapped merged DataFrame | 🔴 Critical | ✅ Fixed |
| 2 | No `class_weight='balanced'` in Logistic Regression | 🟡 Moderate | ✅ Fixed |
| 3 | RSI used simple rolling mean instead of Wilder's EMA | 🟡 Moderate | ✅ Fixed |
| 4 | No majority-class baseline reporter | 🟢 Minor | ⏳ Deferred |
| 5 | `headline_count` treatment as model feature | 🟢 Minor | ✅ Resolved |
| 6 | No direct Technical vs. Sentiment McNemar test | 🟢 Minor | ✅ Fixed |
| 7 | Intraday report linked wrong confusion matrix files | 🔴 Critical | ✅ Fixed |
| 8 | Dead code `train_baseline_model()` in `main.py` | 🟢 Minor | ✅ Fixed |

---

## Additional Changes (Post-Review)

| Change | Description | Status |
|--------|-------------|--------|
| A | Removed live Yahoo Finance scraping from `main()` — live headlines don't match the 2024 stock date range and added unreliable network I/O with no model impact | ✅ Done |
| B | Added FinBERT score caching — if `historical_sentiment_analysis.csv` is newer than the WSJ source CSV, scores are loaded from disk and FinBERT is skipped entirely (~5–10 min saved per run) | ✅ Done |
| C | `avg_neutral` multicollinearity — since pos+neg+neu=1.0 per day, the third sentiment feature is linearly redundant. Flagged; not yet implemented pending thesis methodology review | ⏳ Flagged |

---

*Reviewed: 2026-02-22 | Updated: 2026-02-22*
