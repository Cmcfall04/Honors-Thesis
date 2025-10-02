# Apple Stock Sentiment Analysis Tool

## Overview
This project builds an end-to-end pipeline that connects real-time Apple (AAPL) news with historical pricing data. The script scrapes Yahoo Finance headlines, evaluates sentiment using the FinBERT transformer model, aggregates daily sentiment features, merges those features with AAPL closing prices, and trains a baseline logistic regression classifier to predict next-day stock movement. The workflow and generated artefacts are designed to support an academic thesis on the relationship between financial news sentiment and equity performance.

## Pipeline Summary
1. **Data collection**
   - Downloads AAPL price history between 2025-01-01 and 2025-09-01 using `yfinance`.
   - Scrapes the current Yahoo Finance quote page for Apple-related headlines, retrying on transient failures.
   - Loads additional historical headlines from `data/historical_headlines.csv` (seeded with sample rows; replace with your research dataset).
2. **Sentiment scoring**
   - Runs `yiyanghkust/finbert-tone` (FinBERT) through Hugging Face Transformers and PyTorch.
   - Captures raw sentiment labels plus Positive/Negative/Neutral probabilities for each headline.
3. **Feature engineering**
   - Aggregates sentiment scores by day, returning average probabilities and a headline count per trading date.
   - Merges the sentiment aggregates with AAPL close prices, computes the next-day close, and labels `stock_move` as 1 if the next close is higher.
4. **Modeling & evaluation**
   - Trains a baseline `LogisticRegression` classifier on the three sentiment features.
   - Outputs accuracy, precision, recall, and F1 score to `model_results.md` and plots a confusion matrix to `confusion_matrix.png`.

## Repository Layout
```
Honors-Thesis/
|- main.py                      # Orchestrates the full pipeline (extensively commented)
|- README.md                    # Project documentation (this file)
|- TODO.md                      # Roadmap tracking future thesis tasks
|- data/
|  |- historical_headlines.csv  # Placeholder Apple headlines; replace with long-horizon dataset
|- apple_sentiment_analysis.csv # Latest live headlines scored by FinBERT
|- historical_sentiment_analysis.csv
|                               # Historical headlines scored by FinBERT
|- sentiment_stock_dataset.csv  # Daily sentiment features merged with price data + labels
|- model_results.md             # Baseline model metrics
|- confusion_matrix.png         # Visual confusion matrix for thesis figures
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
1. Activate the virtual environment (`.venv`).
2. Ensure `data/historical_headlines.csv` contains the historical dataset you intend to study. The repository ships with a 2025 sample that keeps the pipeline runnable but is too small for serious modeling.
3. Execute the script:
   ```bash
   python main.py
   ```
4. Inspect generated artefacts:
   - `apple_sentiment_analysis.csv` - the most recent live scrape with sentiment scores.
   - `historical_sentiment_analysis.csv` - FinBERT scores for the historical dataset.
   - `sentiment_stock_dataset.csv` - daily averages, headline counts, closing prices, next-day closes, and binary labels.
   - `model_results.md` & `confusion_matrix.png` - baseline logistic regression evaluation.

### CLI Output Highlights
During execution the script prints:
- Live and historical headline lists with per-headline sentiment probabilities.
- Daily sentiment aggregation previews.
- Merge previews showing the resulting features (`avg_positive`, `avg_negative`, `avg_neutral`, `headline_count`, `close`, `next_close`, `stock_move`).
- Modeling metrics and file save confirmations.

## Data Sources
- **Yahoo Finance** via `yfinance`: historical OHLCV data for Apple.
- **Yahoo Finance web page**: live headlines scraped with `BeautifulSoup`.
- **Custom historical headlines**: CSV expected at `data/historical_headlines.csv` with columns `date` (ISO-8601) and `headline`.

## Modeling Notes for Thesis
- Baseline model: scikit-learn `LogisticRegression` with default regularization, 30-40% held-out test split (stratified when class counts permit).
- Features: average positive, negative, and neutral sentiment probabilities per day.
- Label: `stock_move = 1` if `next_close > close`, otherwise `0`.
- The supplied sample dataset produces high variance metrics because of limited observations; thesis experiments should replace it with a 6-12 month headline archive.

## Customization & Extensibility
- **Stock symbol / window**: update `STOCK_SYMBOL`, `START_DATE`, and `END_DATE` in `main.py`.
- **Headline filters**: adjust `APPLE_KEYWORDS` to refine the scraping mask.
- **Additional data sources**: replace or augment `data/historical_headlines.csv` with Kaggle datasets, NewsAPI pulls, Alpha Vantage news feeds, or institutional databases (Factiva, ProQuest, Bloomberg, WSJ).
- **Feature engineering**: extend `aggregate_daily_sentiment` or `merge_sentiment_with_stock` to inject technical indicators (moving averages, RSI, volume) or longer lookahead labels for ablation studies.
- **Modeling**: experiment with alternative classifiers (Random Forests, Gradient Boosting, neural networks) and cross-validation once a richer dataset is available.

## Troubleshooting
- **FinBERT download issues**: verify internet access; rerun after transient failures. Hugging Face may warn about disabled symlinks on Windows -- this only affects cache efficiency.
- **No headlines returned**: Yahoo frequently adjusts page markup; update `HEADLINE_SELECTORS` or consider using the Yahoo Finance API / RSS feeds as fallback.
- **Empty merged dataset**: confirm that headline dates overlap the stock date range and that the historical CSV uses normalized dates (YYYY-MM-DD).
- **Class imbalance warnings**: small datasets can lead to single-class splits; the code detects this and skips training until more balanced data is supplied.

## Future Work (Roadmap Excerpts)
Refer to `TODO.md` for the active roadmap. Key thesis-oriented next steps include sourcing an extended historical headline corpus, integrating multiple tickers, adding technical indicators, and conducting sentiment-versus-technical ablation experiments.

## Acknowledgements
Created for Honors Thesis research investigating links between financial news sentiment and AAPL price behaviour. Built on open-source tooling from the Python, Hugging Face, and scikit-learn communities.
