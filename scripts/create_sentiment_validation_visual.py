"""Create a visualization of sentiment analysis validation tests for presentation."""

import torch
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np

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

LABELS = ["neutral", "positive", "negative"]  # Correct FinBERT label order

def analyze_headlines():
    """Analyze headlines and return results."""
    print("Loading FinBERT model...")
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    model.eval()
    print("FinBERT loaded!")
    
    results = []
    for headline in SAMPLE_HEADLINES:
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_class = torch.argmax(logits, dim=1).item()
        
        neu_score = probabilities[0][0].item()
        pos_score = probabilities[0][1].item()
        neg_score = probabilities[0][2].item()
        sentiment = LABELS[predicted_class]
        
        results.append({
            'headline': headline,
            'sentiment': sentiment,
            'positive': pos_score,
            'negative': neg_score,
            'neutral': neu_score,
            'confidence': max(pos_score, neg_score, neu_score)
        })
    
    return results

def create_visualization(results, output_path):
    """Create a cleaner, more intuitive visualization of sentiment validation results."""
    
    # Set up the figure with two subplots
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0.3)
    
    # Color scheme
    colors = {
        'positive': '#27ae60',  # Green
        'negative': '#c0392b',  # Red
        'neutral': '#7f8c8d'    # Gray
    }
    
    # Main plot (left side)
    ax_main = fig.add_subplot(gs[0])
    
    n_headlines = len(results)
    y_positions = np.arange(n_headlines)
    
    # Create horizontal bars showing the winning sentiment probability
    bar_heights = []
    bar_colors = []
    sentiment_labels = []
    confidence_values = []
    
    for result in results:
        sentiment = result['sentiment']
        confidence = result['confidence']
        bar_heights.append(confidence)
        bar_colors.append(colors[sentiment])
        sentiment_labels.append(sentiment.upper())
        confidence_values.append(confidence)
    
    # Create bars
    bars = ax_main.barh(y_positions, bar_heights, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add confidence value labels on bars
    for i, (bar, conf) in enumerate(zip(bars, confidence_values)):
        width = bar.get_width()
        ax_main.text(width/2, bar.get_y() + bar.get_height()/2, 
               f'{conf:.1%}', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='white')
    
    # Add sentiment label on the right side of bars
    for i, (sent, conf) in enumerate(zip(sentiment_labels, confidence_values)):
        ax_main.text(1.02, i, sent, va='center', ha='left', 
               fontsize=11, fontweight='bold', color=colors[results[i]['sentiment']])
    
    # Customize y-axis with shortened headlines
    shortened_headlines = []
    for i, result in enumerate(results, 1):
        headline = result['headline']
        # Truncate long headlines
        if len(headline) > 60:
            headline = headline[:57] + "..."
        shortened_headlines.append(f"{i}. {headline}")
    
    ax_main.set_yticks(y_positions)
    ax_main.set_yticklabels(shortened_headlines, fontsize=9)
    ax_main.invert_yaxis()  # Top to bottom
    
    # Customize x-axis
    ax_main.set_xlabel('Predicted Sentiment Confidence', fontsize=12, fontweight='bold')
    ax_main.set_xlim(0, 1.15)
    ax_main.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_main.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    ax_main.grid(axis='x', alpha=0.3, linestyle='--', zorder=0)
    
    # Title
    ax_main.set_title('FinBERT Sentiment Analysis Validation Test\n' + 
                 'Sample Headlines with Predicted Sentiment and Confidence', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor=colors['positive'], edgecolor='black', label='Positive', alpha=0.8),
        mpatches.Patch(facecolor=colors['negative'], edgecolor='black', label='Negative', alpha=0.8),
        mpatches.Patch(facecolor=colors['neutral'], edgecolor='black', label='Neutral', alpha=0.8)
    ]
    ax_main.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.9)
    
    # Summary bar graph (right side)
    ax_summary = fig.add_subplot(gs[1])
    
    # Count sentiments
    sentiment_counts = {}
    for r in results:
        sent = r['sentiment']
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
    
    # Prepare data for bar graph
    sentiments = ['Positive', 'Negative', 'Neutral']
    counts = [
        sentiment_counts.get('positive', 0),
        sentiment_counts.get('negative', 0),
        sentiment_counts.get('neutral', 0)
    ]
    bar_colors_summary = [colors['positive'], colors['negative'], colors['neutral']]
    
    # Create vertical bar graph
    bars_summary = ax_summary.bar(sentiments, counts, color=bar_colors_summary, 
                                   alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on top of bars
    for bar, count in zip(bars_summary, counts):
        height = bar.get_height()
        ax_summary.text(bar.get_x() + bar.get_width()/2., height,
                       f'{count}',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Customize summary plot
    ax_summary.set_ylabel('Number of Headlines', fontsize=11, fontweight='bold')
    ax_summary.set_title('Sentiment Distribution', fontsize=12, fontweight='bold', pad=15)
    ax_summary.set_ylim(0, max(counts) * 1.2)
    ax_summary.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)
    
    # Add total and average confidence text
    avg_confidence = np.mean(confidence_values)
    summary_text = (
        f"Total: {len(results)} headlines\n"
        f"Avg Confidence: {avg_confidence:.1%}\n"
        f"Model: FinBERT"
    )
    ax_summary.text(0.5, 0.95, summary_text, transform=ax_summary.transAxes,
                    ha='center', va='top', fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='black'),
                    family='monospace')
    
    plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.08, wspace=0.3)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to: {output_path}")
    
    return fig

if __name__ == "__main__":
    from pathlib import Path
    
    # Get results
    results = analyze_headlines()
    
    # Create output path
    output_path = Path(__file__).parent.parent / "results" / "sentiment_validation_test.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create visualization
    create_visualization(results, output_path)
    
    print("\nValidation Results:")
    print("=" * 80)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['headline']}")
        print(f"   Predicted: {result['sentiment'].upper()} ({result['confidence']:.1%} confidence)")
        print(f"   Probabilities - Positive: {result['positive']:.3f}, "
              f"Negative: {result['negative']:.3f}, "
              f"Neutral: {result['neutral']:.3f}")
