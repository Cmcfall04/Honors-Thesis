# Apple Stock Sentiment Analysis Tool

## Overview
This project implements an end-to-end pipeline for analyzing the relationship between Wall Street Journal headlines about Apple and next-day stock price movements. Using 361 WSJ articles from 2024, the pipeline applies FinBERT sentiment analysis, aggregates daily sentiment features, and trains a baseline logistic regression model. This work supports an honors thesis investigating whether financial news sentiment can predict short-term equity performance.

**Key Finding**: The baseline model achieved **35.4% accuracy** (below random chance), suggesting that headline sentiment alone is insufficient for predicting next-day stock movements. See `docs/FINDINGS.md` for comprehensive analysis.

## Pipeline Summary
1. **Data Collection**
   - Downloads AAPL price history for 2024 (Jan 1 - Dec 31) using `yfinance`
   - Processes Wall Street Journal headlines exported from ProQuest (361 articles)
   - Optionally scrapes current Yahoo Finance headlines for live analysis
   
2. **Sentiment Analysis**
   - Applies `yiyanghkust/finbert-tone` (FinBERT) via Hugging Face Transformers
   - Generates positive, negative, and neutral probability scores for each headline
   - Handles 361 headlines across 158 unique trading days
   
3. **Feature Engineering**
   - Aggregates sentiment scores by trading day (average probabilities + headline count)
   - Merges sentiment features with AAPL closing prices
   - Creates binary label: `stock_move = 1` if next-day close > current close
   
4. **Modeling & Evaluation**
   - Trains baseline `LogisticRegression` on three sentiment features
   - 70/30 train-test split: 110 training samples, 48 test samples
   - Generates performance metrics and confusion matrix visualization

## Repository Layout
```
Honors-Thesis/
|- README.md                            # Project documentation (this file)
|- TODO.md                              # Roadmap tracking future thesis tasks
|
|- scripts/                             # Python scripts
|  |- main.py                           # Main pipeline: scrape → sentiment → model
|  |- proquest_preprocessor.py          # ProQuest CSV preprocessing and merging
|  |- historical_data.py                # Kaggle dataset downloader script
|
|- docs/                                # Documentation and guides
|  |- FINDINGS.md                       # Comprehensive analysis of results
|  |- PROQUEST_QUICKSTART.md            # Step-by-step ProQuest integration guide
|  |- ProQuest_SearchGuide.md           # ProQuest search strategy for WSJ data
|  |- Historical_data_proquest_pipeline.md # Technical pipeline documentation
|
|- data/
|  |- raw/                              # Original/raw data files
|  |  |- WSJ_Apple_2024.csv             # Original ProQuest export
|  |  |- historical_headlines.csv       # Sample headlines (fallback)
|  |
|  |- processed/                        # Cleaned/processed data
|     |- wsj_apple_proquest.csv         # Processed ProQuest/WSJ headlines (generated)
|     |- aapl_headlines.csv             # Additional scraped headlines
|
|- results/                             # Model outputs and results
   |- apple_sentiment_analysis.csv      # Live headlines scored by FinBERT
   |- historical_sentiment_analysis.csv # Historical headlines scored by FinBERT
   |- sentiment_stock_dataset.csv       # Daily features merged with stock labels
   |- model_results.md                  # Baseline model performance metrics
   |- confusion_matrix.png              # Visual confusion matrix for thesis
   |- stock_data.csv                    # Downloaded AAPL stock prices
```

## Environment Setup
1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. **Install project dependencies inside the environment**
   ```bash
   pip install \
       yfinance requests beautifulsoup4 pandas torch transformers \
       scikit-learn matplotlib
   ```
   > The first FinBERT run downloads several hundred megabytes of model weights; allow extra time and disk space.

## Running the Pipeline

### Option A: Using ProQuest/WSJ Data (Recommended for Thesis)
1. Activate the virtual environment (`.venv`)
2. Export WSJ headlines from ProQuest (see `docs/PROQUEST_QUICKSTART.md`)
3. Place ProQuest CSV export(s) in `data/raw/` directory
4. Preprocess the data:
   ```bash
   python scripts/proquest_preprocessor.py
   ```
5. Run the full pipeline:
   ```bash
   python scripts/main.py
   ```

### Option B: Using Sample Data (Testing Only)
1. Activate the virtual environment (`.venv`)
2. The repository includes sample headlines at `data/raw/historical_headlines.csv`
3. Execute the script:
   ```bash
   python scripts/main.py
   ```
   Note: Sample data is too small for meaningful thesis results.

### Generated Artifacts
After running the pipeline, inspect these files in the `results/` directory:
- `results/apple_sentiment_analysis.csv` - Live headlines with sentiment scores
- `results/historical_sentiment_analysis.csv` - FinBERT scores for historical dataset
- `results/sentiment_stock_dataset.csv` - Daily features merged with stock labels
- `results/model_results.md` - Model performance metrics
- `results/confusion_matrix.png` - Confusion matrix visualization

### CLI Output Highlights
During execution the script prints:
- Live and historical headline lists with per-headline sentiment probabilities.
- Daily sentiment aggregation previews.
- Merge previews showing the resulting features (`avg_positive`, `avg_negative`, `avg_neutral`, `headline_count`, `close`, `next_close`, `stock_move`).
- Modeling metrics and file save confirmations.

## Data Sources
- **Yahoo Finance** via `yfinance`: historical OHLCV data for Apple.
- **Yahoo Finance web page**: live headlines scraped with `BeautifulSoup`.
- **ProQuest/Wall Street Journal** (Primary): Historical WSJ headlines exported from ProQuest database.
  - See `docs/PROQUEST_QUICKSTART.md` for step-by-step integration guide
  - Raw exports placed in `data/raw/`, processed to `data/processed/wsj_apple_proquest.csv`
  - Use `scripts/proquest_preprocessor.py` to prepare ProQuest exports
- **Fallback sample data**: `data/raw/historical_headlines.csv` (12 sample headlines for testing)

## Current Results

### Performance Summary
- **Dataset**: 361 WSJ headlines from 2024, covering 158 trading days
- **Train/Test Split**: 110 training samples, 48 test samples (70/30)
- **Accuracy**: 35.42% (below 50% random baseline)
- **Precision (Up)**: 41.94%
- **Recall (Up)**: 50.00%
- **F1-Score (Up)**: 45.61%

### Key Insights
The model's below-random performance indicates that **headline sentiment alone is insufficient** for predicting next-day stock movements. This finding supports the efficient market hypothesis—public news is quickly incorporated into stock prices. See `docs/FINDINGS.md` for detailed analysis, literature comparison, and future research directions.

### Implications
- Market efficiency: Information in headlines is already priced in
- Need for multimodal features: Technical indicators, full article text, multiple news sources
- Alternative approaches: Different time horizons, advanced models (LSTM, Random Forest)
- Academic contribution: Well-documented negative result valuable for research

## Customization & Extensibility

### Configuration Options
- **Date range**: Modify `START_DATE` and `END_DATE` in `scripts/main.py` (currently set to 2024)
- **Stock symbol**: Change `STOCK_SYMBOL` to analyze different companies (MSFT, GOOGL, etc.)
- **Headline filters**: Adjust `APPLE_KEYWORDS` list to refine scraping criteria
- **Model parameters**: Experiment with different `test_size` ratios or regularization in LogisticRegression

### Extending the Pipeline
- **Additional data sources**: Integrate Bloomberg, Reuters, Financial Times via ProQuest
- **Technical indicators**: Add RSI, MACD, moving averages (see `docs/FINDINGS.md` for implementation suggestions)
- **Advanced models**: Replace LogisticRegression with Random Forest, XGBoost, or LSTM networks
- **Feature engineering**: Include trading volume, sector trends, competitor news
- **Time horizons**: Test same-day, 3-day, or weekly predictions instead of next-day
- **Multi-company analysis**: Extend to predict sector-wide movements or relative performance

## Troubleshooting
- **FinBERT download issues**: verify internet access; rerun after transient failures. Hugging Face may warn about disabled symlinks on Windows -- this only affects cache efficiency.
- **No headlines returned**: Yahoo frequently adjusts page markup; update `HEADLINE_SELECTORS` or consider using the Yahoo Finance API / RSS feeds as fallback.
- **Empty merged dataset**: confirm that headline dates overlap the stock date range and that the historical CSV uses normalized dates (YYYY-MM-DD).
- **Class imbalance warnings**: small datasets can lead to single-class splits; the code detects this and skips training until more balanced data is supplied.

## Future Work

Based on current findings, promising research directions include:

1. **Multimodal Feature Integration**
   - Combine sentiment with technical indicators (moving averages, RSI, volume)
   - Expected improvement: 55-65% accuracy range

2. **Alternative Time Horizons**
   - Test same-day, 3-day, and weekly predictions
   - Longer windows may show stronger sentiment correlations

3. **Advanced Machine Learning**
   - Random Forest, XGBoost for non-linear relationships
   - LSTM/GRU for temporal sequence modeling
   - Transformer architectures for attention mechanisms

4. **Enhanced Data Collection**
   - Full article text analysis (not just headlines)
   - Multi-source sentiment (Bloomberg, Reuters, social media)
   - Event classification (earnings, product launches, regulatory)

5. **Extended Analysis**
   - Multi-company comparison (Apple vs. tech sector)
   - Relative performance prediction (Apple vs. S&P 500)
   - Sector-wide sentiment impact

See `TODO.md` for detailed implementation roadmap and `docs/FINDINGS.md` for academic justification of each direction.

## Documentation

- **`README.md`** - Project overview and quickstart (this file)
- **`docs/FINDINGS.md`** - Comprehensive analysis of results and implications
- **`docs/PROQUEST_QUICKSTART.md`** - Step-by-step WSJ data integration guide
- **`docs/ProQuest_SearchGuide.md`** - ProQuest search strategies
- **`docs/Historical_data_proquest_pipeline.md`** - Technical pipeline documentation
- **`TODO.md`** - Development roadmap and task tracking

## Citation & Acknowledgements

This project was developed for honors thesis research investigating the relationship between financial news sentiment and Apple stock price movements. 

**Key Technologies:**
- **FinBERT** (yiyanghkust/finbert-tone) - Financial sentiment analysis
- **scikit-learn** - Machine learning framework
- **Hugging Face Transformers** - Model implementation
- **yfinance** - Stock market data
- **ProQuest/Wall Street Journal** - High-quality financial news corpus

Built on open-source tooling from the Python, Hugging Face, and scikit-learn communities.
