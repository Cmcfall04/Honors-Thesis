# Critical Bug Fix: FinBERT Label Mapping Error

**Date Discovered:** October 22, 2025  
**Severity:** Critical - Affected all sentiment analysis and model training  
**Status:** Fixed

---

## Executive Summary

A critical bug was discovered in the sentiment analysis pipeline where FinBERT's output labels were incorrectly mapped, resulting in **inverted sentiment predictions**. Positive headlines were classified as negative, and vice versa. This bug explains the model's below-random 35.4% accuracy and affected all historical results prior to this fix.

---

## The Problem

### Incorrect Label Mapping

The code assumed FinBERT's output followed this order:
```python
# INCORRECT ASSUMPTION
LABELS = ["positive", "negative", "neutral"]
# Position [0] = positive
# Position [1] = negative  
# Position [2] = neutral
```

However, FinBERT (`yiyanghkust/finbert-tone`) actually outputs labels in this order:
```python
# ACTUAL FinBERT OUTPUT ORDER
LABELS = ["neutral", "positive", "negative"]
# Position [0] = neutral
# Position [1] = positive
# Position [2] = negative
```

### Incorrect Probability Mapping

Additionally, the probability scores were mapped incorrectly:

```python
# INCORRECT CODE (before fix)
return {
    "sentiment": LABELS[predicted_class],
    "positive": probabilities[0][0].item(),  # Actually neutral!
    "negative": probabilities[0][1].item(),  # Actually positive!
    "neutral": probabilities[0][2].item(),   # Actually negative!
}
```

---

## Discovery Process

### 1. Initial Validation Attempt
Created `validate_sentiment.py` to spot-check sentiment predictions on sample headlines.

### 2. Anomalous Results
The validation revealed nonsensical predictions:

| Headline | Expected | Predicted (Incorrect) |
|----------|----------|----------------------|
| "Apple Reports Record-Breaking Quarterly Revenue and Earnings" | POSITIVE | **NEGATIVE** ❌ |
| "Apple Stock Plunges After iPhone Sales Miss Estimates" | NEGATIVE | **NEUTRAL** ❌ |
| "Apple's AI Investment Boosts Investor Confidence" | POSITIVE | **NEGATIVE** ❌ |
| "Analysts Upgrade Apple Stock Rating on Strong Services Growth" | POSITIVE | **NEGATIVE** ❌ |
| "Apple Sued for Patent Infringement, Stock Drops" | NEGATIVE | **NEUTRAL** ❌ |

### 3. Root Cause Investigation
Created `debug_finbert.py` to inspect the model's actual configuration:

```python
model.config.id2label
# Output: {0: 'Neutral', 1: 'Positive', 2: 'Negative'}

model.config.label2id  
# Output: {'Neutral': 0, 'Positive': 1, 'Negative': 2}
```

This revealed the true label order, confirming our mapping was inverted.

### 4. Testing with Obvious Examples
The debug script tested clear-cut examples:

**Test:** "The company reported record profits and exceeded all expectations"  
- Expected: POSITIVE  
- Raw logits: `[-7.57, 11.77, -5.53]`  
- Probabilities: `[0.000, 1.000, 0.000]`  
- Predicted class index: **1**  
- Model config says index 1 = **Positive** ✅  
- But our code said index 1 = **Negative** ❌

---

## Impact Assessment

### Affected Components
1. ✅ **`scripts/main.py`** - Primary analysis pipeline
2. ✅ **`scripts/validate_sentiment.py`** - Validation script
3. ❌ **`scripts/proquest_preprocessor.py`** - Not affected (no sentiment analysis)
4. ❌ **`scripts/historical_data.py`** - Not affected (data download only)

### Affected Data Files
All files generated before October 22, 2025 contain inverted sentiment:

- ❌ `results/historical_sentiment_analysis.csv` - **Must regenerate**
- ❌ `results/apple_sentiment_analysis.csv` - **Must regenerate**
- ❌ `results/sentiment_stock_dataset.csv` - **Must regenerate**
- ❌ `results/model_results.md` - **Must regenerate**
- ❌ `results/confusion_matrix.png` - **Must regenerate**

### Impact on Model Performance

**Before Fix (with inverted labels):**
- Accuracy: **35.4%** (worse than random 50%)
- The model was trying to learn from backwards data
- Positive sentiment was actually predicting stock decreases
- Negative sentiment was actually predicting stock increases

**Expected After Fix:**
- Accuracy should improve significantly (potentially 50%+ baseline)
- Sentiment features should have correct directional relationship with stock movements
- Model coefficients will reverse sign

---

## The Fix

### Changes to `scripts/main.py`

#### Change 1: Correct Label Order
```python
# BEFORE (Line 85)
LABELS = ["positive", "negative", "neutral"]

# AFTER (Lines 84-85)
# NOTE: FinBERT uses [neutral, positive, negative] order, not [positive, negative, neutral]!
LABELS = ["neutral", "positive", "negative"]
```

#### Change 2: Correct Probability Mapping
```python
# BEFORE (Lines 264-276)
def predict_sentiment(text: str, tokenizer, model) -> Dict[str, float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class = torch.argmax(logits, dim=1).item()
    return {
        "sentiment": LABELS[predicted_class],
        "positive": probabilities[0][0].item(),
        "negative": probabilities[0][1].item(),
        "neutral": probabilities[0][2].item(),
    }

# AFTER (Lines 264-277)
def predict_sentiment(text: str, tokenizer, model) -> Dict[str, float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class = torch.argmax(logits, dim=1).item()
    # FinBERT outputs: [neutral, positive, negative]
    return {
        "sentiment": LABELS[predicted_class],
        "neutral": probabilities[0][0].item(),
        "positive": probabilities[0][1].item(),
        "negative": probabilities[0][2].item(),
    }
```

### Changes to `scripts/validate_sentiment.py`

Same corrections applied to maintain consistency:
```python
# Line 20: Fixed label order
LABELS = ["neutral", "positive", "negative"]

# Lines 45-48: Fixed probability extraction
neu_score = probabilities[0][0].item()
pos_score = probabilities[0][1].item()
neg_score = probabilities[0][2].item()
```

---

## Verification

After applying the fix, validation results became sensible:

| Headline | Expected | Predicted (Fixed) | Confidence |
|----------|----------|------------------|------------|
| "Apple Reports Record-Breaking Quarterly Revenue and Earnings" | POSITIVE | **POSITIVE** ✅ | 100% |
| "Apple Stock Plunges After iPhone Sales Miss Estimates" | NEGATIVE | **NEGATIVE** ✅ | 100% |
| "Apple's AI Investment Boosts Investor Confidence" | POSITIVE | **POSITIVE** ✅ | 100% |
| "Analysts Upgrade Apple Stock Rating on Strong Services Growth" | POSITIVE | **POSITIVE** ✅ | 100% |
| "Apple Sued for Patent Infringement, Stock Drops" | NEGATIVE | **NEGATIVE** ✅ | 99.7% |
| "Apple Announces New Product Launch Event for Next Month" | NEUTRAL | **NEUTRAL** ✅ | 99.5% |

All predictions now match human judgment, confirming the fix.

---

## Required Actions

### ✅ Completed
- [x] Fixed label order in `scripts/main.py`
- [x] Fixed probability mapping in `scripts/main.py`
- [x] Fixed label order in `scripts/validate_sentiment.py`
- [x] Fixed probability mapping in `scripts/validate_sentiment.py`
- [x] Verified fix with sample headlines
- [x] Created documentation

### 🔄 In Progress
- [ ] Re-run full pipeline: `python scripts/main.py`
- [ ] Verify all output files are regenerated
- [ ] Document new model performance metrics

### 📊 Next Steps
- [ ] Compare before/after model performance
- [ ] Update thesis documentation with corrected results
- [ ] Analyze feature importance with correct sentiment
- [ ] Consider adding this as a methodology lesson in thesis
- [ ] Implement technical indicators for enhanced model

---

## Lessons Learned

### 1. Always Validate Model Outputs
The bug was discovered through systematic validation using sample headlines with obvious expected sentiments. This emphasizes the importance of:
- Sanity checks on model predictions
- Testing with clear-cut examples
- Manual inspection before trusting automated results

### 2. Don't Assume Label Orders
Different pre-trained models may use different label orderings. Always:
- Check `model.config.id2label` for the actual mapping
- Verify with the model card/documentation
- Test with known examples before production use

### 3. Document Surprising Findings
While this bug delayed results, it demonstrates:
- Rigorous research methodology
- Problem-solving process
- Importance of validation in ML pipelines
- Can be included in thesis as a methodological consideration

### 4. Negative Results Are Valuable
The initial 35.4% accuracy was suspicious and led to investigation. Below-random performance often indicates:
- Inverted labels (as in this case)
- Incorrect feature engineering
- Data leakage
- Fundamental signal weakness

---

## References

- **FinBERT Model:** [yiyanghkust/finbert-tone](https://huggingface.co/yiyanghkust/finbert-tone)
- **Model Card Label Order:** The model uses `[Neutral, Positive, Negative]` as confirmed by `model.config.id2label`
- **Validation Scripts:** `scripts/validate_sentiment.py`, `scripts/debug_finbert.py`

---

## Appendix: How to Avoid This Bug

If using FinBERT (or any pre-trained model) in future work:

```python
# STEP 1: Load the model
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

# STEP 2: Check the actual label mapping
print("Label mapping:", model.config.id2label)
# Output: {0: 'Neutral', 1: 'Positive', 2: 'Negative'}

# STEP 3: Use the model's labels directly
LABELS = [model.config.id2label[i] for i in range(len(model.config.id2label))]
# This ensures your code adapts to the model's actual order

# STEP 4: Test with obvious examples before deploying
test_positive = "Company reports record profits and strong growth"
test_negative = "Stock crashes after terrible earnings miss"
# Verify predictions match expectations
```

---

**Document Version:** 1.0  
**Last Updated:** October 22, 2025  
**Author:** Honors Thesis Research Team

