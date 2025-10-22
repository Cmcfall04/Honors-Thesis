# Thesis Project To-Do List

This document tracks the development roadmap for the Apple Stock Sentiment Analysis project. The baseline pipeline is complete with 361 WSJ headlines from 2024 analyzed using FinBERT. Current focus is on extending the model with additional features and advanced techniques.

**Current Status**: ✅ Baseline model complete | 📊 Results documented | 🔬 Ready for extensions

---

## ✅ Completed

### Phase 1: Core Pipeline (Complete)
- [x] ProQuest/WSJ data integration
  - [x] Created `proquest_preprocessor.py` for automated CSV processing
  - [x] Exported 361 WSJ headlines from ProQuest (Jan-Dec 2024)
  - [x] Implemented encoding detection and column mapping
  - [x] Added duplicate removal and date normalization
- [x] Stock data collection
  - [x] Downloaded AAPL prices for 2024 using `yfinance`
  - [x] Aligned stock dates with headline dates (158 matching days)
- [x] Sentiment analysis
  - [x] Integrated FinBERT (yiyanghkust/finbert-tone) via Hugging Face
  - [x] Processed all 361 headlines with sentiment scoring
  - [x] Generated positive/negative/neutral probabilities
- [x] Feature engineering
  - [x] Daily sentiment aggregation (average scores + headline count)
  - [x] Stock data merge with next-day movement labels
  - [x] Created `sentiment_stock_dataset.csv` (158 rows × 8 features)
- [x] Baseline modeling
  - [x] Trained Logistic Regression classifier
  - [x] 70/30 train-test split (110 train, 48 test samples)
  - [x] Generated performance metrics and confusion matrix

### Phase 2: Analysis & Documentation (Complete)
- [x] Results analysis
  - [x] Documented 35.4% accuracy (below random baseline)
  - [x] Analyzed confusion matrix and class predictions
  - [x] Identified model bias toward "Up" predictions
- [x] Comprehensive documentation
  - [x] Created `docs/FINDINGS.md` with detailed analysis
  - [x] Explained metrics (accuracy, precision, recall, F1)
  - [x] Compared to existing literature
  - [x] Proposed 7 future research directions
- [x] Project organization
  - [x] Restructured into `scripts/`, `docs/`, `data/`, `results/`
  - [x] Updated all file paths in scripts
  - [x] Created clear documentation hierarchy
- [x] Repository documentation
  - [x] Updated `README.md` with current results
  - [x] Created `docs/PROQUEST_QUICKSTART.md` guide
  - [x] Updated `TODO.md` with realistic roadmap

---

## 🔄 In Progress

### Phase 3: Immediate Extensions
- [ ] **Add technical indicators** (Priority: HIGH)
  - [ ] Implement moving averages (50-day, 200-day SMA)
  - [ ] Add RSI (Relative Strength Index)
  - [ ] Include trading volume features
  - [ ] Calculate volatility metrics (Bollinger Bands)
  - [ ] Expected improvement: 55-65% accuracy range
  
- [ ] **Test alternative time horizons** (Priority: MEDIUM)
  - [ ] Same-day prediction (headline → same-day close)
  - [ ] 3-day cumulative movement
  - [ ] Weekly aggregation to reduce noise
  - [ ] Compare predictive power across horizons

---

## 📋 Planned (Next Steps)

### Phase 4: Advanced Modeling
- [ ] **Implement non-linear models** (Priority: HIGH)
  - [ ] Random Forest classifier
    - Better handles feature interactions
    - Can capture non-linear sentiment patterns
  - [ ] Gradient Boosting (XGBoost/LightGBM)
    - Strong performance on tabular data
    - Built-in feature importance
  - [ ] Compare performance against baseline
  
- [ ] **Temporal sequence modeling** (Priority: MEDIUM)
  - [ ] LSTM/GRU for sentiment time series
  - [ ] Model multi-day sentiment trends
  - [ ] Capture momentum in sentiment shifts
  
- [ ] **Model evaluation enhancements**
  - [ ] Implement k-fold cross-validation
  - [ ] Add precision-recall curves
  - [ ] Calculate ROC-AUC scores
  - [ ] Perform statistical significance testing

### Phase 5: Data Enhancement
- [ ] **Multi-source sentiment** (Priority: HIGH)
  - [ ] Add Bloomberg headlines via ProQuest
  - [ ] Integrate Reuters news
  - [ ] Include Financial Times coverage
  - [ ] Combine into ensemble sentiment score
  
- [ ] **Full article analysis** (Priority: MEDIUM)
  - [ ] Extract full article text from ProQuest
  - [ ] Apply FinBERT to complete articles (not just headlines)
  - [ ] Compare headline-only vs. full-text sentiment
  
- [ ] **Event classification** (Priority: LOW)
  - [ ] Categorize headlines: earnings, product launch, regulatory, legal
  - [ ] Test if different event types have different predictive power
  - [ ] Weight sentiment by event importance

### Phase 6: Extended Analysis
- [ ] **Multi-company comparison**
  - [ ] Apply pipeline to MSFT, GOOGL, AMZN
  - [ ] Compare sentiment-prediction relationships across companies
  - [ ] Test if smaller-cap stocks show stronger sentiment effects
  
- [ ] **Sector-wide analysis**
  - [ ] Aggregate sentiment for entire tech sector
  - [ ] Predict relative performance (Apple vs. NASDAQ)
  - [ ] Test sector momentum strategies
  
- [ ] **Intraday analysis** (Priority: LOW)
  - [ ] Collect intraday price data
  - [ ] Match headlines to precise publication times
  - [ ] Test immediate price impact (minutes/hours after publication)

---

## 🔬 Research & Experimentation

### Thesis-Specific Tasks
- [ ] **Literature review refinement**
  - [ ] Deep dive into papers with similar findings (35-45% accuracy range)
  - [ ] Document why sentiment-only approaches struggle
  - [ ] Identify successful multimodal approaches
  
- [ ] **Statistical analysis**
  - [ ] Perform hypothesis testing on sentiment-return correlation
  - [ ] Calculate statistical significance of results
  - [ ] Test for autocorrelation in sentiment scores
  
- [ ] **Visualization enhancements**
  - [ ] Create time series plots: sentiment vs. stock price
  - [ ] Visualize feature importance (if using tree-based models)
  - [ ] Generate correlation heatmaps
  - [ ] Plot cumulative returns for sentiment-based strategy

### Documentation for Thesis
- [ ] **Methods section**
  - [ ] Detailed FinBERT methodology
  - [ ] Feature engineering justification
  - [ ] Model selection rationale
  
- [ ] **Results section**
  - [ ] Comprehensive tables of all experiments
  - [ ] Statistical significance reporting
  - [ ] Error analysis and failure cases
  
- [ ] **Discussion section**
  - [ ] Market efficiency implications
  - [ ] Comparison to existing literature
  - [ ] Limitations and threats to validity
  - [ ] Future work recommendations

---

## 🚫 Deprioritized / Out of Scope

- [ ] ~~Real-time trading system~~ (Not thesis objective)
- [ ] ~~Options pricing prediction~~ (Too complex for baseline)
- [ ] ~~Cryptocurrency sentiment analysis~~ (Different market dynamics)
- [ ] ~~Social media sentiment (Twitter/Reddit)~~ (Data quality concerns)
- [ ] ~~International markets~~ (Language barriers, different news sources)

---

## 📊 Success Metrics

### Model Performance Targets
- **Baseline** (Current): 35.4% accuracy
- **With Technical Indicators**: 55-65% accuracy target
- **With Advanced Models**: 60-70% accuracy target
- **Multi-Source Sentiment**: 65-75% accuracy target

*Note: Even 55-60% accuracy would represent significant improvement and valuable thesis contribution*

### Academic Milestones
- [x] Complete functional pipeline
- [x] Document negative result professionally
- [ ] Implement 2-3 extensions showing improvement
- [ ] Compare against benchmark papers
- [ ] Complete thesis draft with results

---

## 🛠️ Technical Debt & Maintenance

- [ ] Add comprehensive unit tests for pipeline components
- [ ] Implement logging framework (replace print statements)
- [ ] Add configuration file (YAML/JSON) for parameters
- [ ] Create requirements.txt with pinned versions
- [ ] Add error handling for edge cases
- [ ] Optimize FinBERT batch processing (currently sequential)
- [ ] Add progress bars for long-running operations

---

## 📝 Notes

### Key Insights from Initial Results
1. **Market Efficiency**: WSJ headlines already priced in by next day
2. **Feature Insufficiency**: Sentiment alone captures only one signal dimension
3. **Class Imbalance**: Model bias toward "Up" predictions due to general market trend
4. **Temporal Lag**: Next-day prediction may be wrong timeframe

### Recommended Priority Order
1. **Add technical indicators** (quick win, likely to improve results)
2. **Test alternative time horizons** (may find better prediction window)
3. **Implement Random Forest** (non-linear relationships)
4. **Add multi-source sentiment** (more comprehensive signal)
5. **Full article analysis** (richer context)

### Timeline Estimates
- **Technical indicators**: 1-2 days
- **Alternative time horizons**: 1 day
- **Random Forest implementation**: 2-3 days
- **Multi-source data collection**: 3-5 days
- **Full article analysis**: 5-7 days (depends on ProQuest extraction)

---

## 🎯 Thesis Defense Preparation

- [ ] Prepare presentation slides
- [ ] Practice explaining negative result positively
- [ ] Prepare responses to common questions:
  - "Why not just use random guessing?"
  - "What would make this model profitable?"
  - "How does this compare to industry practice?"
- [ ] Create compelling visualizations
- [ ] Rehearse 10-minute presentation
- [ ] Prepare detailed appendix with all experiments

---

**Last Updated**: October 15, 2024  
**Project Status**: Baseline complete, ready for extensions  
**Next Action**: Implement technical indicators (moving averages + RSI)

- Also check that the Sentiment analysis is actually reading healine right and not lying about sentiment
- Change sentiment from 1,0,-1 to mores specific values, add range for slightly positive, slightly negative for more range
- Add additional information(Fnacial information), make two models, with all the info and one w all the info and w the sentiment analysis
