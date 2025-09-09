import json
import re
from rapidfuzz import fuzz, process

# ---------------- Paths ----------------
EXTRACTED_DIR = 'data/extracted/'
PREPROCESSED_DIR = 'data/preprocessed/'
TESTING_EXTRACTED_PATH = EXTRACTED_DIR + 'testing_articles.json'
GOLD_STANDARD_PATH = PREPROCESSED_DIR + 'testing_gold.json'

# ---------------- Normalization ----------------
def normalize_text(text):
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # normalize spaces
    text = text.strip()
    text = text.replace('\xa0', ' ')
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ascii chars
    return text

# ---------------- Accuracy Calculation ----------------
def calculate_accuracy(extracted, gold_standard, fuzzy_threshold=90):
    if not gold_standard:
        return {"headline": 0, "body": 0, "publication_date": 0}

    headline_correct = 0
    body_correct = 0
    date_correct = 0

    # Create lookup dictionary of gold articles by normalized headline
    gold_lookup = {normalize_text(article.get('headline')): article for article in gold_standard}

    for ext in extracted:
        ext_headline_norm = normalize_text(ext.get('headline'))

        # Find the closest matching gold headline
        best_match, score, _ = process.extractOne(
            ext_headline_norm, list(gold_lookup.keys()), scorer=fuzz.ratio
        )

        if score >= fuzzy_threshold:
            headline_correct += 1
            gold_article = gold_lookup[best_match]

            # Body comparison
            body_score = fuzz.ratio(
                normalize_text(ext.get('body')), normalize_text(gold_article.get('body'))
            )
            if body_score >= fuzzy_threshold:
                body_correct += 1

            # Publication date comparison (YYYY-MM-DD)
            ext_date = ext.get('publication_date')
            gold_date = gold_article.get('publication_date')
            if ext_date:
                ext_date = ext_date.split(' ')[0]
            if ext_date == gold_date:
                date_correct += 1

    total = len(gold_standard)
    return {
        "headline": round(headline_correct / total * 100, 2),
        "body": round(body_correct / total * 100, 2),
        "publication_date": round(date_correct / total * 100, 2)
    }

# ---------------- Run Accuracy Check ----------------
if __name__ == "__main__":
    # Load extracted articles
    with open(TESTING_EXTRACTED_PATH, 'r', encoding='utf-8') as f:
        extracted = json.load(f)

    # Load gold standard
    with open(GOLD_STANDARD_PATH, 'r', encoding='utf-8') as f:
        gold_standard = json.load(f)

    accuracy = calculate_accuracy(extracted, gold_standard)
    print("\n=== Testing Accuracy ===")
    print(f"Headline Accuracy: {accuracy['headline']}%")
    print(f"Body Accuracy: {accuracy['body']}%")
    print(f"Publication Date Accuracy: {accuracy['publication_date']}%")
