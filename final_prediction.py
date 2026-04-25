import pandas as pd
import joblib
import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

model = joblib.load(r'C:\datathon\toxic_model.pkl')

df = pd.read_excel(r'C:\datathon\toxic_no_label_evaluation.xlsx')

df['label'] = model.predict(df['text'].apply(clean_text)).astype(int)

df.to_excel(r'C:\Users\ASUS\Downloads\toxic_no_label_evaluation.xlsx', index=False)
print("Done!")
print(df['label'].value_counts())