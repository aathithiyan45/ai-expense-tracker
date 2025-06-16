# ml_model/train_model.py

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

# 1. Sample training data (you can expand later)
data = {
    'description': [
        'pizza', 'burger', 'restaurant', 
        'uber', 'bus ticket', 'train fare',
        'electricity bill', 'internet', 'mobile recharge',
        'movie', 'netflix', 'cinema',
        'salary', 'freelance', 'refund'
    ],
    'category': [
        'Food', 'Food', 'Food', 
        'Transport', 'Transport', 'Transport',
        'Utilities', 'Utilities', 'Utilities',
        'Entertainment', 'Entertainment', 'Entertainment',
        'Income', 'Income', 'Income'
    ]
}

df = pd.DataFrame(data)

# 2. Feature extraction
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['description'])
y = df['category']

# 3. Train the model
model = MultinomialNB()
model.fit(X, y)

# 4. Save model and vectorizer
os.makedirs("ml_model", exist_ok=True)
joblib.dump(model, "ml_model/model.pkl")
joblib.dump(vectorizer, "ml_model/vectorizer.pkl")

print("✅ Model and vectorizer trained & saved!")
