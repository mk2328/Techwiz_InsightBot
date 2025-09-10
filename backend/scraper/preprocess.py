# preprocess_updated.py
import json
import os
import re
import unicodedata
from bs4 import BeautifulSoup

# ---------------- Paths ----------------
RAW_TRAINING_PATH = 'data/training_articles.json'
RAW_TESTING_PATH = 'data/testing_articles.json'
PREPROCESSED_DIR = 'data/preprocessed/'
os.makedirs(PREPROCESSED_DIR, exist_ok=True)

# ---------------- Helpers ----------------
def clean_html(raw_html):
    """Remove unwanted tags and extract visible text"""
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    # Remove scripts, styles, ads, navs, footers
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'iframe']):
        tag.extract()
    
    # Remove elements with common ad classes
    ad_classes = ['ads', 'advertisement', 'promo', 'sponsor']
    for cls in ad_classes:
        for ad in soup.find_all(class_=re.compile(cls, re.I)):
            ad.extract()
    
    text = soup.get_text(separator=' ', strip=True)
    return text

def normalize_text(text):
    """Normalize spaces, Unicode, and special characters"""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces/newlines
    return text.strip()

# ---------------- Preprocess ----------------
def preprocess_json(input_path, output_path, min_words=50):
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    preprocessed_articles = []
    skipped_count = 0

    for article in articles:
        html_content = article.get('html', '')
        if not html_content.strip():
            print(f"⚠️ Empty HTML, skipping {article.get('url')}")
            skipped_count += 1
            continue

        clean_text = normalize_text(clean_html(html_content))
        word_count = len(clean_text.split())

        if word_count < min_words:
            print(f"⚠️ Short article (<{min_words} words), skipping {article.get('url')}")
            skipped_count += 1
            continue

        preprocessed_articles.append({
            'url': article.get('url'),
            'source': article.get('source') or article.get('url'),
            'html': html_content,
            'clean_text': clean_text,
            'type': article.get('type', 'unknown'),
            'language': article.get('language', 'unknown')
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(preprocessed_articles, f, ensure_ascii=False, indent=4)

    print(f"✅ Preprocessed {len(preprocessed_articles)} articles -> {output_path}")
    if skipped_count > 0:
        print(f"⚠️ Skipped {skipped_count} articles due to empty or short content")

# ---------------- Run ----------------
if __name__ == "__main__":
    preprocess_json(RAW_TRAINING_PATH, os.path.join(PREPROCESSED_DIR, 'training_articles.json'))
    preprocess_json(RAW_TESTING_PATH, os.path.join(PREPROCESSED_DIR, 'testing_articles.json'))
