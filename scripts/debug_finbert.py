"""Debug FinBERT to check label mappings."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def debug_finbert():
    """Test FinBERT and show raw outputs."""
    
    print("Loading FinBERT...\n")
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    model.eval()
    
    # Check model configuration
    print("Model config:")
    print(f"id2label mapping: {model.config.id2label}")
    print(f"label2id mapping: {model.config.label2id}\n")
    
    # Test with your actual sample headlines
    test_cases = [
        ("Apple Reports Record-Breaking Quarterly Revenue and Earnings", "Should be POSITIVE"),
        ("Apple Stock Plunges After iPhone Sales Miss Estimates", "Should be NEGATIVE"),
        ("Apple Announces New Product Launch Event for Next Month", "Should be NEUTRAL/POSITIVE"),
        ("Tim Cook Faces Shareholder Lawsuit Over Market Performance", "Should be NEGATIVE"),
        ("Apple's AI Investment Boosts Investor Confidence", "Should be POSITIVE"),
        ("Apple Sued for Patent Infringement, Stock Drops", "Should be NEGATIVE"),
        ("Apple Maintains Market Position Despite Economic Uncertainty", "Should be NEUTRAL"),
        ("Analysts Upgrade Apple Stock Rating on Strong Services Growth", "Should be POSITIVE"),
        ("Apple Faces Regulatory Challenges in European Markets", "Should be NEGATIVE/NEUTRAL"),
        ("Apple's New iPhone Pre-Orders Exceed Expectations", "Should be POSITIVE"),
    ]
    
    print("=" * 80)
    print("TESTING OBVIOUS EXAMPLES")
    print("=" * 80)
    
    for headline, expected in test_cases:
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_class = torch.argmax(logits, dim=1).item()
        
        print(f"\nHeadline: {headline}")
        print(f"Expected: {expected}")
        print(f"Raw logits: {logits[0].tolist()}")
        print(f"Probabilities: {probabilities[0].tolist()}")
        print(f"Predicted class index: {predicted_class}")
        print(f"Model says: {model.config.id2label[predicted_class]}")
        print(f"Position 0 (positive?): {probabilities[0][0]:.3f}")
        print(f"Position 1 (negative?): {probabilities[0][1]:.3f}")
        print(f"Position 2 (neutral?): {probabilities[0][2]:.3f}")
        print("-" * 80)

if __name__ == "__main__":
    debug_finbert()

