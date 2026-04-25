import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess(df, text_col='comment'):
    df = df.copy()
    df[text_col] = df[text_col].apply(clean_text)
    return df

def build_pipeline():
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=50000,
            sublinear_tf=True
        )),
        ('clf', LogisticRegression(
            C=5.0,
            max_iter=1000,
            class_weight='balanced'
        ))
    ])

def train(csv_path, text_col='comment', label_col='label'):
    df = pd.read_excel(csv_path) if csv_path.endswith('.xlsx') else pd.read_csv(csv_path)
    df = preprocess(df, text_col)
    X = df[text_col]
    y = df[label_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = build_pipeline()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
    joblib.dump(model, r'C:\datathon\toxic_model.pkl')
    print("Model saved as toxic_model.pkl")
    return model

def predict(text, model_path=r'C:\datathon\toxic_model.pkl'):
    model = joblib.load(model_path)
    text_clean = clean_text(text)
    label = model.predict([text_clean])[0]
    prob  = model.predict_proba([text_clean])[0].max()
    return {"label": int(label), "confidence": round(float(prob), 3)}

if __name__ == "__main__":
    train(r"C:\datathon\toxic_labeled.xlsx", text_col='text', label_col='label')

