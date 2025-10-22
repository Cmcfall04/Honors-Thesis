"""Quick sentiment validation script - tests FinBERT on sample headlines."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Sample headlines to test (mix of positive, negative, and neutral)
SAMPLE_HEADLINES = [
    "Apple Reports Record-Breaking Quarterly Revenue and Earnings",
    "Apple Stock Plunges After iPhone Sales Miss Estimates",
    "Apple Announces New Product Launch Event for Next Month",
    "Tim Cook Faces Shareholder Lawsuit Over Market Performance",
    "Apple's AI Investment Boosts Investor Confidence",
    "Apple Sued for Patent Infringement, Stock Drops",
    "Apple Maintains Market Position Despite Economic Uncertainty",
    "Analysts Upgrade Apple Stock Rating on Strong Services Growth",
    "Apple Faces Regulatory Challenges in European Markets",
    "Apple's New iPhone Pre-Orders Exceed Expectations",
]

LABELS = ["neutral", "positive", "negative"]  # Fixed: Correct FinBERT label order

def analyze_sample_headlines():
    """Load FinBERT and analyze sample headlines."""
    
    print("Loading FinBERT model...\n")
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    model.eval()
    print("FinBERT loaded!\n")
    
    print("=" * 80)
    print("SENTIMENT ANALYSIS TEST - SAMPLE HEADLINES")
    print("=" * 80)
    
    for i, headline in enumerate(SAMPLE_HEADLINES, 1):
        # Get sentiment prediction
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_class = torch.argmax(logits, dim=1).item()
        
        # FinBERT outputs: [neutral, positive, negative]
        neu_score = probabilities[0][0].item()
        pos_score = probabilities[0][1].item()
        neg_score = probabilities[0][2].item()
        sentiment = LABELS[predicted_class]
        
        print(f"\n{i}. {headline}")
        print(f"   >>> {sentiment.upper()} <<<")
        print(f"   Positive: {pos_score:.3f} | Negative: {neg_score:.3f} | Neutral: {neu_score:.3f}")
        print("   " + "-" * 75)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print("\nDo the sentiment predictions match your expectations?")
    print("If they seem off, FinBERT may not be suitable for your headlines.")

if __name__ == "__main__":
    analyze_sample_headlines()

