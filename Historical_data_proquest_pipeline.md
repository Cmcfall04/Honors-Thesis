# 📌 WSJ Data Pipeline for Thesis Project

This document explains how to collect, process, and analyze **Wall Street Journal (WSJ)** data (via ProQuest) for predicting short-term stock market movements using sentiment analysis and stock price data.

---

## 1. Why WSJ via ProQuest?

- ✅ High-quality, business-focused publication.  
- ✅ Historical depth back to 1984 through ProQuest.  
- ✅ Easy export in CSV/Excel format → structured, reproducible dataset.  
- ✅ Strong academic credibility (widely respected and citable).  

For this project, **WSJ via ProQuest** will serve as the **sole primary dataset**.

---

## 2. Collecting WSJ Data from ProQuest

### Step 1: Search
1. Open **ProQuest** and go to **Advanced Search**.  
2. Select **Wall Street Journal (Publication title)** as the source.  
3. Use Boolean queries for Apple-related content:  
4. Apply a **date range** (e.g., last 12 months).  

### Step 2: Export
1. Export search results in **CSV/Excel** format.  
2. Include fields:  


⚠️ ProQuest may limit bulk exports (e.g., 100–500 records per batch). Export multiple batches and merge them if needed.

---

## 3. Pipeline Implementation (Conceptual)

The pipeline has five main stages:

### Stage 1: Load Data
- Input: `wsj_apple_proquest.csv` file.  
- Extract fields: **Date** and **Headline**.  
- Standardize column names and ensure all dates are converted to a consistent format.  

---

### Stage 2: Sentiment Analysis
- Apply **FinBERT** model to each headline.  
- Output sentiment scores: **positive, negative, neutral**.  
- Append sentiment scores to the dataset.  

---

### Stage 3: Aggregate Daily Sentiment
- Group headlines by **Date**.  
- Compute **average positive, negative, and neutral sentiment** for each day.  
- Output a daily sentiment table:  


---

### Stage 4: Merge with Stock Price Data
- Collect Apple stock daily close prices for the same time period (via Yahoo Finance or other financial database).  
- Merge with sentiment data on **Date**.  
- Create classification label:  
- `1` if the next day’s closing price is higher than today’s.  
- `0` otherwise.  
- Output merged dataset:  



---

### Stage 5: Build Baseline Model
- Use a classification model (e.g., Logistic Regression).  
- Input features: **Avg_Positive, Avg_Negative, Avg_Neutral**.  
- Target label: **Stock_Move**.  
- Train model on a portion of the data.  
- Test model on the remaining data.  
- Evaluate with: **Accuracy, Precision, Recall, F1-score, Confusion Matrix**.  

---

## 4. Extensions (Future Work)

- Expand analysis to other companies (e.g., Microsoft, Amazon).  
- Add **technical indicators** (moving averages, RSI, volume) alongside sentiment features.  
- Experiment with additional models (e.g., Random Forest, XGBoost).  
- Test different lookahead windows (same-day vs. next-day vs. two-day movements).  
- Compare different time ranges (short-term vs. long-term).  

---
