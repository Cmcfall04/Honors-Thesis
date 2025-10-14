# 📌 ProQuest Search Guide for WSJ Headlines

This guide explains how to efficiently search and export **Wall Street Journal (WSJ)** articles from **ProQuest** for use in the stock market prediction project.

---

## 1. Accessing WSJ in ProQuest
1. Go to your **university library website**.  
2. Navigate to **Databases A–Z** or the library’s journal search tool.  
3. Search for **ProQuest** and open it.  
4. Confirm you have access to **Wall Street Journal (Publication title)** through ProQuest.

---

## 2. Using Advanced Search
1. Click on **Advanced Search** in ProQuest.  
2. In the **search bar**, enter the following Boolean query for Apple-related content:
   ```
   Apple OR AAPL OR iPhone OR Mac OR iPad OR "Tim Cook" OR Cupertino
   ```
3. Under **Publication Title**, type:
   ```
   Wall Street Journal
   ```
   and select it.  
4. Set the **date range** (e.g., last 12 months, or Jan 2023 – present).  
5. (Optional) Apply filters for **Document Type** → News Article.  

---

## 3. Reviewing Search Results
- Verify that headlines are relevant to **Apple and its stock**.  
- Remove unrelated articles if necessary.  
- Ensure results contain **Date** and **Title (headline)** fields.

---

## 4. Exporting Data
1. From the results page, select **all articles** you want to export.  
2. Click **Export/Save** → choose **CSV/Excel**.  
3. Select the following fields for export:
   - **Publication Date**  
   - **Title** (headline)  
   - (Optional) Abstract or Full Text if you want to test article-level sentiment later  
4. Export and download the file.  
5. Save the file as:
   ```
   wsj_apple_proquest.csv
   ```

⚠️ **Note**: ProQuest may limit exports (e.g., 100–500 records at a time). If so, export in multiple batches and later merge files into a single dataset.

---

## 5. Dataset Format
Your exported file should look like this (example):

```
Date        | Headline
2023-05-15  | Apple Unveils New MacBook Pro with M2 Chip
2023-05-16  | iPhone Sales Surge in Asia, Boosting AAPL Stock
2023-05-17  | Tim Cook Meets Lawmakers on Supply Chain Concerns
```

---

## 6. Next Steps After Export
1. Place the exported CSV into your project’s `data/` folder.  
2. Use it as input to the **WSJ pipeline** (see `WSJ_Data_Pipeline.md`).  
3. Run sentiment analysis (FinBERT) → aggregate daily scores → merge with stock data → build classification model.  

---

## 7. Tips for Best Results
- Run searches for **different time ranges** (e.g., 1-year chunks) and merge datasets to avoid export limits.  
- Use **consistent Boolean queries** so data is comparable across time ranges.  
- Keep a record of your search queries and export dates — this helps with reproducibility in your thesis.  

---
