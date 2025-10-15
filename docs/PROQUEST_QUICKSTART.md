# 🚀 ProQuest Integration Quick Start

This guide will help you quickly integrate Wall Street Journal headlines from ProQuest into your sentiment analysis pipeline.

---

## ✅ Prerequisites

1. University access to **ProQuest** database
2. Python environment set up (see README.md)
3. Virtual environment activated (`.venv`)

---

## 📖 Step-by-Step Instructions

### Step 1: Export Data from ProQuest

1. **Access ProQuest** through your university library
2. Navigate to **Advanced Search**
3. Configure your search:
   ```
   Publication Title: Wall Street Journal
   Search Terms: Apple OR AAPL OR iPhone OR Mac OR iPad OR "Tim Cook" OR Cupertino
   Date Range: 2024-01-01 to 2024-12-31
   Document Type: News Article (optional filter)
   ```
4. **Export Results**:
   - Click "Export/Save" → Choose **CSV** or **Excel**
   - Select fields: **Publication Date** and **Title**
   - Download the file

⚠️ **ProQuest Export Limits**: If you have more than 500 results, export in multiple batches:
   - Batch 1: Jan-Apr 2024
   - Batch 2: May-Aug 2024
   - Batch 3: Sep-Dec 2024

5. **Save to Project**: Place your exported CSV file(s) in the `data/` directory
   - Acceptable filenames: `proquest_export.csv`, `wsj_apple.csv`, `export_batch1.csv`, etc.

---

### Step 2: Preprocess ProQuest Data

Run the preprocessing script:

```bash
python proquest_preprocessor.py
```

**What it does:**
- 🔍 Automatically finds all ProQuest exports in `data/`
- 🔗 Merges multiple batches if needed
- 🧹 Cleans and standardizes data
- ✅ Validates date formats
- 🗑️ Removes duplicates
- 💾 Outputs: `data/wsj_apple_proquest.csv`

**Expected Output:**
```
Found 2 ProQuest export file(s):
  - proquest_export_part1.csv
  - proquest_export_part2.csv

Loading proquest_export_part1.csv...
  Original columns: ['Publication Date', 'Title', 'Abstract']
  Mapped 'Publication Date' → 'date', 'Title' → 'headline'
  Loaded 250 records

Loading proquest_export_part2.csv...
  Original columns: ['Publication Date', 'Title']
  Mapped 'Publication Date' → 'date', 'Title' → 'headline'
  Loaded 200 records

Combined 450 total records from 2 file(s)

Cleaning data...
  Removed 0 rows with missing headlines
  Warning: 2 rows have invalid dates, removing them
  Removed 8 duplicate headlines
  Final cleaned dataset: 440 records

======================================================================
DATASET SUMMARY
======================================================================
Total headlines: 440
Date range: 2024-01-02 to 2024-12-30
Unique dates: 248
Average headlines per day: 1.77

✅ Processed data saved to: data/wsj_apple_proquest.csv

You can now run 'python main.py' to analyze this dataset!
```

---

### Step 3: Run Full Pipeline

Execute the main sentiment analysis pipeline:

```bash
python main.py
```

**What happens:**
1. ✅ Downloads AAPL stock prices for 2024
2. ✅ Scrapes live headlines from Yahoo Finance (optional)
3. ✅ Loads your ProQuest/WSJ headlines
4. ✅ Runs FinBERT sentiment analysis on all headlines
5. ✅ Aggregates daily sentiment scores
6. ✅ Merges sentiment with stock price data
7. ✅ Trains baseline Logistic Regression model
8. ✅ Generates results and visualizations

**Generated Files:**
- `historical_sentiment_analysis.csv` - Sentiment scores for WSJ headlines
- `sentiment_stock_dataset.csv` - Daily features + stock labels
- `model_results.md` - Model performance metrics
- `confusion_matrix.png` - Confusion matrix visualization

---

## 📊 Expected Results

With **200-400 WSJ headlines** covering 2024, you should see:

- **Training samples**: ~150-180
- **Test samples**: ~60-80
- **Much more reliable metrics** than the 12-sample demo dataset
- **Statistically meaningful** accuracy, precision, recall, and F1 scores

---

## 🔧 Troubleshooting

### Issue: "No ProQuest export files found"
**Solution**: Make sure your CSV files are in the `data/` directory and match these patterns:
- `proquest*.csv`
- `wsj*.csv`
- `export*.csv`

### Issue: "Could not identify date column"
**Solution**: Check that your ProQuest export includes a date field. Common names:
- "Publication Date" ✅
- "Date" ✅
- "Pub Date" ✅
- "Published" ✅

If your column has a different name, edit `proquest_preprocessor.py` line 21 to add it.

### Issue: "Could not identify headline/title column"
**Solution**: Check that your export includes a title field. Common names:
- "Title" ✅
- "Headline" ✅
- "Article Title" ✅

If your column has a different name, edit `proquest_preprocessor.py` line 26 to add it.

### Issue: Pipeline uses old sample data instead of ProQuest data
**Solution**: Verify that `data/wsj_apple_proquest.csv` exists after running the preprocessor. The pipeline prioritizes this file over the sample data.

---

## 📝 Template File

A template showing the expected ProQuest export format is available at:
```
data/proquest_template.csv
```

Your ProQuest export should look similar to this format (column names may vary).

---

## 🎯 Next Steps After Initial Run

1. **Review Results**: Check `model_results.md` and `confusion_matrix.png`
2. **Analyze Performance**: Compare against random baseline (50% accuracy)
3. **Iterate**:
   - Try different date ranges
   - Expand to other companies (MSFT, GOOGL, etc.)
   - Add technical indicators (see TODO.md)
4. **Document Findings**: Record methodology and results for thesis

---

## 📚 Additional Resources

- **Detailed ProQuest Search Guide**: `ProQuest_SearchGuide.md`
- **Pipeline Architecture**: `Historical_data_proquest_pipeline.md`
- **Project README**: `README.md`
- **Future Enhancements**: `TODO.md`

---

## ❓ Need Help?

Common questions:
- **How many headlines do I need?** Aim for 200-400 to get meaningful results
- **What date range should I use?** 2024 full year is recommended
- **Can I use multiple batches?** Yes! The preprocessor automatically merges them
- **What if I want 2023 data too?** Update `START_DATE` and `END_DATE` in `main.py` lines 33-34

---

**You're all set! 🎉**

Once you've exported your WSJ data from ProQuest, just run:
1. `python proquest_preprocessor.py`
2. `python main.py`

And your complete pipeline will execute automatically.

