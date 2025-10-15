# Temporal Alignment Considerations for Sentiment-Based Stock Prediction

**Date**: October 15, 2024  
**Status**: Methodological considerations for future implementation  
**Priority**: HIGH - Likely major contributor to current low accuracy

---

## Current Implementation

### What We're Doing Now

The baseline pipeline uses **same-day headlines to predict next-day movement**:

```
Timeline:
Day X (e.g., January 5, 2024)
├─ WSJ headlines published on Jan 5 → Sentiment analysis
├─ AAPL closing price on Jan 5 → $184.00
└─ AAPL closing price on Jan 8 (next trading day) → $179.66

Prediction Target: stock_move = 0 (down, because $179.66 < $184.00)
Features: Sentiment from Jan 5 headlines
```

### The Code
```python
# In merge_sentiment_with_stock() function (line 387-395 of scripts/main.py)

merged = pd.merge(daily_sentiment, stock_df, on="date", how="inner")
merged = merged.sort_values("date").reset_index(drop=True)
merged["next_close"] = merged["close"].shift(-1)  # Get next day's close
merged["stock_move"] = (merged["next_close"] > merged["close"]).astype(int)
```

**Result**: Using Day X sentiment to predict Day X+1 movement

---

## Why This Is Problematic

### 1. **Information Already Priced In**

If WSJ headlines are published during market hours (9:30 AM - 4:00 PM EST):
- Traders and algorithms read the news **immediately**
- Stock price adjusts **same day** to reflect the information
- By market close, the news is already "baked into" the closing price

**Example**:
```
10:00 AM: WSJ publishes "Apple Reports Strong iPhone Sales" (positive sentiment)
10:05 AM: Stock jumps $2.00 as traders react
4:00 PM: Market closes at $186.00 (already reflects the good news)
Next Day: Opens at $185.50 (news is old, no predictive power)
```

### 2. **Missing Critical Time Information**

Our ProQuest data includes publication **dates** but not exact **times**:
- We don't know if headline was published at 8:00 AM (before market open) or 5:00 PM (after close)
- Before-market headlines might predict same-day movement
- After-market headlines might predict next-day movement
- We're mixing both without distinction

### 3. **Market Efficiency Hypothesis**

The 35.4% accuracy (below random) suggests:
- Public information (like WSJ headlines) is **rapidly incorporated** into prices
- By next day, the sentiment signal has **zero predictive value**
- This validates the Efficient Market Hypothesis (EMH)

---

## Alternative Approaches

### Option 1: Use Previous Day's Headlines (RECOMMENDED)

**Rationale**: Headlines from Day X-1 might not have been fully priced in by Day X's open

```python
# Proposed modification to merge_sentiment_with_stock()

# Current approach (same day):
merged["stock_move"] = (merged["next_close"] > merged["close"]).astype(int)

# Alternative approach (previous day):
merged["prev_sentiment_positive"] = merged["avg_positive"].shift(1)
merged["prev_sentiment_negative"] = merged["avg_negative"].shift(1)
merged["prev_sentiment_neutral"] = merged["avg_neutral"].shift(1)
merged = merged.dropna()  # Remove first row (no previous day)
merged["stock_move"] = (merged["close"] > merged["prev_close"]).astype(int)

# Now using Day X-1 sentiment to predict Day X movement
```

**Expected Impact**: 
- May improve accuracy to 45-55% range
- Tests whether overnight information diffusion matters
- Better aligns with trading reality (you'd make decisions based on yesterday's news)

### Option 2: Filter for After-Hours Headlines Only

**Rationale**: Headlines published after market close (4:00 PM - 11:59 PM) couldn't have affected same-day price

**Requirements**:
1. Extract time information from ProQuest exports
2. Filter to only after-market headlines (4:00 PM - 11:59 PM)
3. Use these to predict next-day movement

**Pros**:
- Clean temporal separation
- Headlines genuinely couldn't affect same-day price

**Cons**:
- Reduces dataset size significantly (maybe 20-30% of headlines)
- ProQuest may not provide exact publication times
- After-hours news might already be priced into next-day opening price

### Option 3: Intraday Analysis

**Rationale**: Predict immediate price impact, not end-of-day

**Approach**:
```
Headline published: 10:15 AM
Current price: $184.50
Predict: Price change by 11:00 AM or 2:00 PM
```

**Requirements**:
- Intraday stock price data (Yahoo Finance provides this)
- Exact headline publication times
- Different model architecture (likely LSTM for time series)

**Pros**:
- Tests immediate market reaction
- More aligned with how news actually affects prices

**Cons**:
- Requires intraday data (more complex)
- Smaller time windows = more noise
- Outside typical thesis scope

### Option 4: Multi-Day Sentiment Accumulation

**Rationale**: Stock movements reflect cumulative sentiment over several days, not single-day news

**Approach**:
```python
# Use sentiment from past 3-5 days to predict next day
merged["sentiment_3day_avg"] = merged["avg_positive"].rolling(window=3).mean()
merged["sentiment_trend"] = merged["avg_positive"].diff()  # Increasing or decreasing?
```

**Pros**:
- Captures sentiment momentum
- Smooths out single-day noise
- May reveal longer-term patterns

**Cons**:
- Requires more historical data
- Loses samples at beginning of dataset
- More complex interpretation

---

## Recommended Implementation Priority

### Phase 1: Quick Test (1-2 hours)
**Implement Option 1: Previous Day Headlines**

This is the easiest to implement and most likely to show improvement:

```python
# In merge_sentiment_with_stock() function:
# Add after line 395

# Shift sentiment features back by 1 day
for col in ["avg_positive", "avg_negative", "avg_neutral"]:
    merged[f"prev_{col}"] = merged[col].shift(1)

# Drop the first row (no previous day)
merged = merged.dropna(subset=["prev_avg_positive"])

# Retrain model using prev_avg_positive, prev_avg_negative, prev_avg_neutral
```

**Expected Outcome**: 
- If accuracy improves to 45-55%, validates temporal misalignment hypothesis
- If still ~35%, suggests sentiment itself is the issue (not timing)

### Phase 2: Enhanced Analysis (1 day)
**Test Multiple Time Lags**

Try 1-day, 2-day, and 3-day lags to find optimal prediction horizon:

```python
# Test lag = 1, 2, 3 days
for lag in [1, 2, 3]:
    merged[f"lag{lag}_positive"] = merged["avg_positive"].shift(lag)
    # ... train model, record accuracy
```

Find the lag that maximizes accuracy.

### Phase 3: Advanced (If time permits)
**Implement Option 4: Rolling Windows**

Combine multiple days of sentiment for richer features.

---

## Implementation Notes

### Current Code Location
File: `scripts/main.py`  
Function: `merge_sentiment_with_stock()` (lines 363-396)  
Modification Point: After line 395 (where stock_move is created)

### Testing Procedure
1. **Backup current results**: Copy `results/` to `results_baseline/`
2. **Modify code**: Implement previous-day shift
3. **Run pipeline**: `python scripts/main.py`
4. **Compare**: Check if accuracy improved
5. **Document**: Update `docs/FINDINGS.md` with new results

### Metrics to Compare
- **Accuracy**: Should improve from 35.4% (current) to ideally 45-55%
- **Precision**: Watch for changes in false positive rate
- **Recall**: Check if we're catching more actual "Up" days
- **Confusion Matrix**: See if bias toward "Up" decreases

---

## Academic Implications

### If Previous-Day Approach Improves Accuracy

**Thesis Contribution**:
- "Temporal alignment matters: Using Day T-1 sentiment to predict Day T improved accuracy by X%"
- Demonstrates importance of considering information diffusion timelines
- Validates partial market efficiency (same-day news is priced in, but overnight processing exists)

### If Previous-Day Approach Doesn't Help

**Still Valuable**:
- "We tested multiple temporal alignments (same-day, previous-day, 2-day lag)"
- "None improved accuracy, suggesting sentiment itself lacks predictive power"
- Strengthens market efficiency argument
- Shows thorough experimental methodology

---

## Questions for Further Investigation

1. **When are WSJ articles typically published?**
   - Morning (before market open): 20%?
   - During market hours: 60%?
   - After market close: 20%?

2. **How quickly does the market react to WSJ news?**
   - Instantaneous (algorithmic trading)?
   - Within minutes?
   - Hours later?

3. **Does it matter if the headline is about earnings vs. product launches?**
   - Earnings might have immediate price impact
   - Product speculation might take days to be priced in

4. **Weekend effect**:
   - Headlines published Friday evening → Priced in Monday morning?
   - Could create a special case worth testing

---

## Related Literature to Review

Papers to find:
1. Studies on **news propagation speed** in financial markets
2. **Intraday price impact** of news releases
3. **After-hours trading** and news incorporation
4. **Algorithmic trading** response times to text-based news

Look for phrases like:
- "information diffusion"
- "news-price discovery"
- "intraday market microstructure"
- "text-to-trade latency"

---

## Code Snippet: Quick Implementation

### Minimal Change to Test Previous-Day Hypothesis

```python
# Add to merge_sentiment_with_stock() after line 395

# === EXPERIMENTAL: Use previous day's sentiment ===
merged["prev_avg_positive"] = merged["avg_positive"].shift(1)
merged["prev_avg_negative"] = merged["avg_negative"].shift(1)
merged["prev_avg_neutral"] = merged["avg_neutral"].shift(1)

# Remove first row (no previous day available)
merged = merged.dropna(subset=["prev_avg_positive"])

print("\n⚠️  EXPERIMENTAL MODE: Using previous day's sentiment")
print(f"Reduced dataset size: {len(merged)} rows (from {len(merged)+1})")

# Note: Model training code in train_baseline_model() 
# needs to use prev_avg_* features instead of avg_* features
```

### Update Model Training (line 412 in main.py)

```python
# Change feature selection from:
features = dataset[["avg_positive", "avg_negative", "avg_neutral"]]

# To:
features = dataset[["prev_avg_positive", "prev_avg_negative", "prev_avg_neutral"]]
```

---

## Summary

**Current Problem**: Using Day X headlines to predict Day X+1 movement likely fails because Day X headlines are already reflected in Day X closing price.

**Proposed Solution**: Use Day X-1 headlines to predict Day X movement (previous-day lag).

**Expected Impact**: Modest improvement (10-20% accuracy gain) if temporal misalignment is a primary issue.

**Implementation Effort**: Low (1-2 hours for basic version).

**Academic Value**: High (demonstrates methodological rigor and understanding of market microstructure).

**Next Step**: Implement Option 1 (previous-day lag) and compare results to baseline.

---

**Status**: Ready to implement  
**Assigned Priority**: HIGH  
**Estimated Time**: 1-2 hours  
**Expected Accuracy Improvement**: +10-20% (to 45-55% range)

