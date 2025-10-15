# Baseline Logistic Regression Results

- Train samples: 110
- Test samples: 48
- Feature columns: avg_positive, avg_negative, avg_neutral
- Accuracy: 0.3542
- Precision (Up): 0.4194
- Recall (Up): 0.5000
- F1-score (Up): 0.4561

## Classification Report
```
precision    recall  f1-score   support

   Down/Flat       0.24      0.18      0.21        22
          Up       0.42      0.50      0.46        26

    accuracy                           0.35        48
   macro avg       0.33      0.34      0.33        48
weighted avg       0.33      0.35      0.34        48
```

Confusion matrix saved to `confusion_matrix.png`.