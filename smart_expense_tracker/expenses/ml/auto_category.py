import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
model = joblib.load(BASE_DIR / 'ml_model' / 'model.pkl')
vectorizer = joblib.load(BASE_DIR / 'ml_model' / 'vectorizer.pkl')

def predict_category(description):
    return model.predict([description])[0]
