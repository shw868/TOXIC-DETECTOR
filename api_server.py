from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re

app = Flask(__name__)
CORS(app)  # This allows the HTML file to talk to this server

# ── Translation setup ──
# Install with: pip install deep-translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("[WARNING] deep-translator not installed. Run: pip install deep-translator")
    print("[WARNING] Translation feature will be disabled.")

def translate_to_english(text, source_lang):
    """Translate non-English text to English using Google Translate (free, no API key)."""
    if not TRANSLATION_AVAILABLE:
        return None
    # Only translate if not already English
    if source_lang in ("English",):
        return None
    try:
        lang_map = {
            "Hindi":    "hi",
            "Arabic":   "ar",
            "Tamil":    "ta",
            "Telugu":   "te",
            "Bengali":  "bn",
            "Hinglish": "hi",   # Google handles Hinglish best under Hindi
            "Spanish":  "es",
        }
        src = lang_map.get(source_lang, "auto")
        translated = GoogleTranslator(source=src, target="en").translate(text)
        if translated and translated.strip().lower() != text.strip().lower():
            return translated.strip()
        return None
    except Exception as e:
        print(f"[Translation error] {e}")
        return None

# ── Text cleaning ──
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ── Language detector ──
def detect_language(text):
    hindi_chars  = len(re.findall(r'[\u0900-\u097F]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    tamil_chars  = len(re.findall(r'[\u0B80-\u0BFF]', text))
    telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
    bengali_chars= len(re.findall(r'[\u0980-\u09FF]', text))
    total = len(text.strip())
    if total == 0:
        return "Unknown", False
    if hindi_chars  / total > 0.2: return "Hindi",   False
    if arabic_chars / total > 0.2: return "Arabic",  False
    if tamil_chars  / total > 0.2: return "Tamil",   False
    if telugu_chars / total > 0.2: return "Telugu",  False
    if bengali_chars/ total > 0.2: return "Bengali", False

    # Hinglish: Latin script with Indian word patterns
    hinglish_words = ['maa', 'bhai', 'yaar', 'sala', 'teri', 'tere', 'meri', 'kya',
                      'hai', 'nahi', 'acha', 'bol', 'chal', 'bata', 'kar', 'karo',
                      'bahut', 'bohot', 'zyada', 'bilkul', 'ekdum', 'seedha',
                      'tera', 'tujhe', 'usse', 'unhe', 'kyun', 'kaise', 'kaisa',
                      'dekh', 'sun', 'samajh', 'raha', 'rahi', 'gaya', 'gayi']
    lower = text.lower()
    if any(w in lower.split() for w in hinglish_words):
        return "Hinglish", True

    return "English", False

# ── Toxic keyword signals ──
TOXIC_KEYWORDS = ['idiot', 'stupid', 'fool', 'hate', 'kill', 'die', 'moron',
                  'shut up', 'get lost', 'loser', 'garbage', 'rubbish',
                  'sala', 'ganda', 'bakwas', 'bewakoof', 'chup', 'bura']

THREAT_KEYWORDS = ['kill', 'hurt', 'find you', 'make you pay', 'regret',
                   'come for you', 'destroy', 'end you']

INSULT_KEYWORDS = ['idiot', 'stupid', 'moron', 'fool', 'loser', 'ugly',
                   'bewakoof', 'pagal', 'gadha', 'nikamma']

OBSCENE_KEYWORDS = ['fuck', 'shit', 'bastard', 'damn', 'ass',
                    'bc', 'mc', 'bhosdike', 'madarchod', 'bhenchod']

def keyword_boost(text, keywords):
    lower = text.lower()
    return min(0.3 * sum(1 for k in keywords if k in lower), 0.4)

# ── Build detailed reasoning ──
def build_reasoning(scores, flagged, lang, translated):
    """Generate a human-readable explanation of why the comment was flagged."""
    parts = []

    # Language note
    if lang not in ("English", "Unknown"):
        lang_note = f"Detected as {lang}"
        if translated:
            lang_note += f' (translated: "{translated}")'
        parts.append(lang_note + ".")

    if scores['toxic'] < 0.25:
        parts.append("Comment appears non-toxic and neutral in tone.")
        return " ".join(parts)

    # What type of toxicity dominates?
    if scores['threat'] > 0.5:
        parts.append("Contains direct threatening language toward a person.")
    if scores['obscene'] > 0.5:
        parts.append("Contains obscene or profane language.")
    if scores['insult'] > 0.5:
        parts.append("Contains insulting language directed at a person.")
    if scores['severe_toxic'] > 0.5:
        parts.append("Severity level is high — language is extremely aggressive.")
    if scores['identity_hate'] > 0.3:
        parts.append("May target identity (religion, ethnicity, gender).")

    # Mention flagged phrases
    if flagged:
        phrase_list = ", ".join(f'"{p}"' for p in flagged[:3])
        parts.append(f"Flagged phrases: {phrase_list}.")

    # Fallback if nothing specific
    if not parts or (len(parts) == 1 and lang not in ("English", "Unknown")):
        parts.append(f"Toxicity score {scores['toxic']:.0%} — language patterns suggest hostility.")

    return " ".join(parts)

# ── Main predict route ──
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    comment = data.get('comment', '').strip()
    if not comment:
        return jsonify({'error': 'Empty comment'}), 400

    try:
       model = joblib.load(r'C:\datathon\toxic_model.pkl')
    except:
        return jsonify({'error': 'Model not found. Run toxic_model.py first.'}), 500

    cleaned    = clean_text(comment)
    label      = int(model.predict([cleaned])[0])
    probs      = model.predict_proba([cleaned])[0]
    toxic_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])

    # Build multi-label scores
    base = toxic_prob
    scores = {
        "toxic":         round(min(base + keyword_boost(comment, TOXIC_KEYWORDS),        1.0), 3),
        "severe_toxic":  round(min(base * 0.6,                                            1.0), 3),
        "obscene":       round(min(base * 0.5 + keyword_boost(comment, OBSCENE_KEYWORDS), 1.0), 3),
        "threat":        round(min(base * 0.3 + keyword_boost(comment, THREAT_KEYWORDS),  1.0), 3),
        "insult":        round(min(base * 0.7 + keyword_boost(comment, INSULT_KEYWORDS),  1.0), 3),
        "identity_hate": round(min(base * 0.2,                                            1.0), 3),
    }

    # Detect language
    lang, is_transliterated = detect_language(comment)

    # ── TRANSLATION (the key fix) ──
    translated = translate_to_english(comment, lang)

    # Flagged phrases
    lower  = comment.lower()
    flagged = [k for k in (TOXIC_KEYWORDS + THREAT_KEYWORDS + OBSCENE_KEYWORDS) if k in lower][:5]

    # Rich reasoning
    reasoning = build_reasoning(scores, flagged, lang, translated)

    return jsonify({
        "detected_language":  lang,
        "is_transliterated":  is_transliterated,
        "original_meaning":   translated,       # ← Now actually filled!
        "scores":             scores,
        "reasoning":          reasoning,
        "flagged_phrases":    flagged
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  NLP Toxic Detector API — running on port 5000")
    print("  Translation: " + ("ENABLED ✓" if TRANSLATION_AVAILABLE else "DISABLED — run: pip install deep-translator"))
    print("  Keep this window open while using the simulator")
    print("=" * 60)
    app.run(port=5000, debug=False)