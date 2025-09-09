# preprocess.py
import json
import os
import re
import unicodedata
from bs4 import BeautifulSoup

# Paths
RAW_TRAINING_PATH = 'data/training_articles.json'
RAW_TESTING_PATH = 'data/testing_articles.json'
PREPROCESSED_DIR = 'data/preprocessed/'

# Ensure preprocessed folder exists
os.makedirs(PREPROCESSED_DIR, exist_ok=True)

# Function to clean HTML and remove unwanted tags
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        tag.extract()
    text = soup.get_text(separator=' ', strip=True)
    return text

# Normalize text (Unicode, whitespace)
def normalize_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    return text

# Preprocess function for a JSON file
def preprocess_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    preprocessed_articles = []
    for article in articles:
        html_content = article.get('html', '')  # Keep raw HTML for extraction
        clean_text = normalize_text(clean_html(html_content))

        preprocessed_articles.append({
            'url': article.get('url'),
            'source': article.get('source') or article.get('url'),
            'html': html_content,       # RAW HTML kept for rule-based extraction
            'clean_text': clean_text    # Cleaned text for later NLP or display
        })

    # Save preprocessed JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(preprocessed_articles, f, ensure_ascii=False, indent=4)

    print(f"Preprocessed {len(preprocessed_articles)} articles and saved to {output_path}")


if __name__ == "__main__":
    # Preprocess training articles
    preprocess_json(RAW_TRAINING_PATH, os.path.join(PREPROCESSED_DIR, 'training_articles.json'))
    # Preprocess testing articles
    preprocess_json(RAW_TESTING_PATH, os.path.join(PREPROCESSED_DIR, 'testing_articles.json'))
