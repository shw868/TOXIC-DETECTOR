## Project Name
## **MULTILINGUAL TOXIC COMMENT CLASSIFCATION**
## Description

**A multi-label identification model capable of identifying multiple forms of toxicity (such as threats, obscenity, insults, and identity-based hate) across multilingual text data, using the provided dataset.
The system detects and classifies toxic content across 22 languages and scripts using a trained ML classifier served through a live REST API and visualized in a custom simulator UI.**


## Table of Contents
- [Project Summary](#Project-Summary) 
- [Quick Start](#Quick-Start) 
- [System Architecture](#System-Architecture) 
- [File Overview](#File-Overview)
- [Requirements](#Requirements) 
- [Approach and Methodology](#Approach-and-Methodology) 
- [Supported Languages](#Supported-Languages) 
- [Toxicity Labels & Scoring](#Toxicity-Labels-&-Scoring)
- [Simulator Features](#Simulator-Features) 
- [API Reference](#API-Reference)  
- [Team](#Team) 
## Project Summary
A fully functional multilingual toxic comment detection system built end-to-end for the 
hackathon. The system detects and classifies toxic content across 22 languages including international and indian languages and scripts 
using a trained ML classifier served through a live REST API and visualized in a custom 
simulator UI. 
What makes it complete: 
● ✅ Trained ML model (toxic_model.pkl) — scikit-learn pipeline 

● ✅ Live REST API (api.py) — Flask, CORS-enabled,r

● ✅ Real-time simulator UI (simulator.html) — zero install, open in any browser 

● ✅ Single-comment and bulk analysis modes 

● ✅ Multi-label scoring with keyword boosting

## Quick Start 
3 commands to run the full system: 
1. Install dependencies 
pip install flask flask-cors joblib scikit-learn 
2. Train the model
python toxic_model.py
3. Start the API server
python api_server.py
4. Open the simulator (Windows)
start nlp_simulator_connected.html
OR on Mac
open nlp_simulator_connected.html
5. Paste these commands on CMD/POWERSHELL/TERMINAL
**NOTE-**
Keep the api_server.py terminal window open while using the simulator — closing it will break the connection.
## System Architecture

![System Architecture](architecture%20diagram.jpeg)

## 📁 File Overview

| File | Description |
|------|-------------|
| `toxic_model.py` | Trains and saves the scikit-learn toxic comment classifier as `toxic_model.pkl` |
| `api_server.py` | Flask API that loads the model and returns toxicity scores for any submitted comment |
| `nlp_simulator_connected.html` | Browser dashboard UI that sends comments to the API and visualizes the results |
| `toxic_model.pkl` | Serialized trained model loaded by the API at inference time | 

## Reqirements
Python 3.8+ 
flask 
flask-cors 
joblib 
scikit-learn 
Install everything: 
pip install flask flask-cors joblib scikit-learn 

## 🚀 Instructions to reproduce

### Step 1 — Train the Model
```bash
python toxic_model.py
```
Reads the training CSV, fits the TF-IDF + classifier pipeline, and saves `toxic_model.pkl` in the project root.

### Step 2 — Start the API Server
```bash
python api_server.py
```
Expected output:
 
================================================== 

NLP Toxic Detector API — running on port 5000 
Keep this window open while using the simulator

================================================== 

⚠️ Keep this terminal open. The simulator stops working if you close it.

### Step 3 — Open the Simulator

Open `nlp_simulator_connected.html` directly in your browser — no extra server needed.
## ⚙️ Approach and Methodology
### 1. Dataset — `toxic_no_label_evaluation.xlsx`
The evaluation dataset contains **1,000 multilingual comments** with binary labels:

| Label | Count | Meaning |
|-------|-------|---------|
| `0` | 501 | Non-toxic |
| `1` | 499 | Toxic |

Comments are in multiple languages including Hindi, English, and Hinglish.

he evaluation dataset contains **1,000 multilingual comments** with binary labels:

| Label | Count | Meaning |
|-------|-------|---------|
| `0` | 501 | Non-toxic |
| `1` | 499 | Toxic |

Comments are in multiple languages including Hindi, English, and Hinglish.


### 2. Text Cleaning — `clean_text()`
Every comment is normalized before prediction — lowercased, URLs removed, punctuation stripped, and whitespace collapsed.

### 3. Language Detection — `detect_language()`
Detects language via Unicode range matching (>20% character threshold) for Hindi, Arabic, Tamil, Telugu, and Bengali. Hinglish is detected using a curated 26-word Latin-script list. Returns `(language, is_transliterated)`.
## Models
### 1. ML Prediction — `toxic_model.pkl`
Cleaned text is passed through a scikit-learn TF-IDF + classifier pipeline returning a binary label and a toxic probability score (`probs[1]`) used as the base score.

### 2. Multi-Label Scoring
Six dimensions are derived from the base s(CENE_KEYWORDS)` |
| `threat` | `base × 0.3 + boost(THREAT_KEYWORDS)` |
| `insult` | `base × 0.7 + boost(INSUL
| `severe_toxic` | `base × 0.6` |
| `obscene` | `base × 0.5 + boost(OBST_KEYWORDS)` |
| `identity_hate` | `base × 0.2` |

> `keyword_boost` = `0.3 × matched keywords`, capped at `0.4`

## Supported Languages
Hindi ,English,Tamil,Telegu,Bengali,Arabic,Hinglish,Spanish and many more


## 🎯 Toxicity Labels & Scoring

### Labels
| Label | Formula |
|-------|---------|
| `toxic` | `base + boost(TOXIC_KEYWORDS)` |
| `severe_toxic` | `base × 0.6` |
| `obscene` | `base × 0.5 + boost(OBSCENE_KEYWORDS)` |
| `threat` | `base × 0.3 + boost(THREAT_KEYWORDS)` |
| `insult` | `base × 0.7 + boost(INSULT_KEYWORDS)` |
| `identity_hate` | `base × 0.2` |

> `base` = `probs[1]` from `model.predict_proba()` · `keyword_boost` = `0.3 × matched keywords`, capped at `0.4` · All scores capped at `1.0`, rounded to 3 decimal places

### Keyword Lists
| List | Sample Keywords |
|------|----------------|
| `TOXIC_KEYWORDS` | `idiot, stupid, fool, hate, kill, sala, bakwas, bewakoof` |
| `THREAT_KEYWORDS` | `kill, hurt, find you, destroy, make you pay, end you` |
| `INSULT_KEYWORDS` | `idiot, moron, loser, ugly, pagal, gadha, nikamma` |
| `OBSCENE_KEYWORDS` | `fuck, shit, bastard, bc, mc, madarchod, bhenchod` |
## Verdict
| Max Score | Verdict |
|-----------|---------|
| ≥ 0.6 | 🔴 TOXIC |
| ≥ 0.25 | 🟡 CAUTION |
| < 0.25 | 🟢 SAFE |

## 🖥️ Simulator Features

### 1. Live Predictor
- Type any comment and get instant toxicity analysis
- Displays verdict (🔴 TOXIC / 🟡 CAUTION / 🟢 SAFE) with reasoning
- Shows all 6 label scores with visual progress bars
- Highlights flagged phrases detected in the comment
- Displays detected language and transliteration status

### 2. Model Selector
- Choose between 3 model variants (UI-level selection)
- Each card shows model name, description, and AUC score

### 3. Prediction History
- Logs every analysed comment in the session
- Shows text preview, detected language, and verdict per entrycore with keyword boosting (capped at 1.0):

| Label | Formula |
|-------|---------|
| `toxic` | `base + boost(TOXIC_KEYWORDS)` |

### 4. Training Simulator
- Fake terminal that simulates model training with live logs
- Animated progress bar with epoch-by-epoch output
- Displays accuracy metrics and confusion matrix after training

### 5. Model Comparison Table
- Side-by-side comparison of all 3 models
- Columns: Accuracy, AUC, Precision, Recall, F1, Speed

### 6. UI Highlights
- Dark terminal-style theme (`#0a0b0f` background)
- Sidebar navigation with section switching
- Animated blinking cursor in terminal view
- Fully responsive — works in any modern browser with no install
  
## 📡 API Reference

**Base URL:** `http://localhost:5000`



### `POST /predict`

Analyzes a comment and returns toxicity scores.

**Request**
```json
{
  "comment": "your text here"
}
```

**Response**
```json
{
  "detected_language": "Hindi",
  "is_transliterated": false,
  "original_meaning": null,
  "scores": {
    "toxic": 0.85,
    "severe_toxic": 0.51,
    "obscene": 0.42,
    "threat": 0.25,
    "insult": 0.59,
    "identity_hate": 0.17
  },
  "reasoning": "Comment contains insulting language directed at a person.",
  "flagged_phrases": ["idiot", "stupid"]
}
```

**Error Responses**
| Status | Reason |
|--------|--------|
| `400` | Empty comment submitted |
| `500` | `toxic_model.pkl` not found — run `toxic_model.py` first |

**Reasoning Values**
| Condition | Reasoning |
|-----------|-----------|
| `toxic < 0.25` | Comment appears non-toxic and neutral in tone. |
| `threat > 0.5` | Comment contains threatening language. |
| `obscene > 0.5` | Comment contains obscene or profane language. |
| `insult > 0.5` | Comment contains insulting language directed at a person. |
| Otherwise | Comment shows signs of toxicity (score: X%). |
## 📊 Results 

### 📁 Dataset Sample
![Dataset Sample](prediction%20output.png)

> Dataset contains multilingual comments (Hindi, English, Hinglish) with binary labels:
> - `0` — Non-toxic
> - `1` — Toxic

---

### 🏋️ Model Training Lab
![Model Training Lab](model%20training.png)

---

### 📈 Accuracy Report
![Accuracy Report](accuracy%20report.png)

> **Best ROC-AUC:** 0.984 (DistilBERT) · **Baseline AUC:** 0.940 (TF-IDF + LR) · **Gain vs Baseline:** +4.4%

**Per-label performance (DistilBERT):**
| Label | Score |
|-------|-------|
| toxic | 0.97 |
| obscene | 0.985 |
| insult | 0.978 |
| severe_toxic | 0.96 |
| identity_hate | 0.93 |
| threat | 0.91 |

**Confusion Matrix (toxic label):**
| | Predicted Safe | Predicted Toxic |
|--|---------------|-----------------|
| **Actually Safe** | 14,230 ✅ | 287 ❌ |
| **Actually Toxic** | 142 ❌ | 1,568 ✅ |

> Precision: 0.845 · Recall: 0.917 · F1: 0.888

---

### 🔍 Live Prediction
![Live Prediction](live%20prediction.png)

---

### 🔄 Model Comparison
![Model Comparison](model%20comparing.png)
## 👥 Team Members
  
- Sai Shweta Rao
- Saumya Koshta
- Rida Ali Ansari
- Yashasvi Agrawal
