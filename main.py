# import the necessary libraries
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# define the stock symbol
stock_symbol = "AAPL"

# get the stock data
stock_data = yf.download(stock_symbol, start="2025-01-01", end="2025-09-01")

# print the stock data
#print(stock_data.head())

#create csv file to see whats in it
#stock_data.to_csv("stock_data.csv")

# Scrape from yahoo finance
url = "https://finance.yahoo.com/quote/AAPL/"

# Add headers to make request look like a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try multiple selectors that Yahoo Finance might use for headlines
    headlines = []
    
    # Look for various headline selectors specifically for news
    selectors = [
        'h3[data-testid="clamp-container"]',
        '[data-testid="title"]',
        'div[data-testid="news-stream"] h3',
        '.js-content-viewer h3',
        'a[data-testid="title-link"]',
        '.news-item h3',
        '.stream-item h3'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            headlines.extend([elem.get_text().strip() for elem in elements])
            break  # Stop after finding headlines with the first working selector
    
    if headlines:
        # Filter headlines to only include Apple-related news
        apple_keywords = ['apple', 'aapl', 'iphone', 'ipad', 'mac', 'tim cook', 'cupertino']
        apple_headlines = []
        
        for headline in headlines:
            if any(keyword.lower() in headline.lower() for keyword in apple_keywords):
                apple_headlines.append(headline)
        
        if apple_headlines:
            print(f"Found {len(apple_headlines)} Apple-related headlines:")
            for i, headline in enumerate(apple_headlines, 1):
                print(f"{i}. {headline}")
        else:
            print("No Apple-specific headlines found in the scraped data.")
            print(f"Total headlines found: {len(headlines)}")
    else:
        print("No headlines found. The page structure might have changed.")
        # Debug: Let's see what we actually got
        print("Page title:", soup.title.text if soup.title else "No title found")
        print("First few div elements:")
        divs = soup.find_all('div')[:5]
        for div in divs:
            if div.get_text().strip():
                print(f"- {div.get_text().strip()[:100]}...")

except requests.RequestException as e:
    print(f"Error fetching the page: {e}")
    apple_headlines = []  # Initialize empty list if scraping fails
except Exception as e:
    print(f"Error parsing the page: {e}")
    apple_headlines = []  # Initialize empty list if scraping fails

# Load FinBERT model for sentiment analysis
print("\nLoading FinBERT model for sentiment analysis...")
try:
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    print("FinBERT model loaded successfully!")
    
    # Labels for output
    labels = ["positive", "negative", "neutral"]
    
    # Function to predict the sentiment of the text
    def predict_sentiment(text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_class = torch.argmax(logits, dim=1).item()
        
        return {
            "sentiment": labels[predicted_class],
            "positive": probabilities[0][0].item(),
            "negative": probabilities[0][1].item(),
            "neutral": probabilities[0][2].item()
        }
    
    # Perform sentiment analysis on Apple headlines
    if apple_headlines:
        print(f"\nAnalyzing sentiment for {len(apple_headlines)} Apple headlines...")
        results = []
        
        for i, headline in enumerate(apple_headlines, 1):
            sentiment_scores = predict_sentiment(headline)
            results.append({
                "headline": headline,
                "sentiment": sentiment_scores["sentiment"],
                "positive": round(sentiment_scores["positive"], 4),
                "negative": round(sentiment_scores["negative"], 4),
                "neutral": round(sentiment_scores["neutral"], 4)
            })
            print(f"{i}. {headline}")
            print(f"   Sentiment: {sentiment_scores['sentiment']} (Pos: {sentiment_scores['positive']:.2f}, Neg: {sentiment_scores['negative']:.2f}, Neu: {sentiment_scores['neutral']:.2f})")
        
        # Convert to DataFrame and display
        sentiment_df = pd.DataFrame(results)
        print(f"\nSentiment Analysis Summary:")
        print(sentiment_df[['headline', 'sentiment', 'positive', 'negative', 'neutral']])
        
        # Save results to CSV
        sentiment_df.to_csv("apple_sentiment_analysis.csv", index=False)
        print(f"\nResults saved to 'apple_sentiment_analysis.csv'")
    else:
        print("\nNo Apple headlines found for sentiment analysis.")

except Exception as e:
    print(f"Error loading FinBERT model: {e}")
    print("Make sure you have installed the required packages:")
    print("pip install transformers torch")