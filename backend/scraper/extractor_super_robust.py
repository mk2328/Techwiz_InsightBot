# extractor_multilang.py
import json
import os
import re
import unicodedata
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory, LangDetectException

# ---------------- Paths ----------------
PREPROCESSED_DIR = 'data/preprocessed/'
OUTPUT_DIR = 'data/extracted_multilang/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

PREPROCESSED_TRAIN = os.path.join(PREPROCESSED_DIR, 'training_articles.json')
PREPROCESSED_TEST = os.path.join(PREPROCESSED_DIR, 'testing_articles.json')

# ---------------- Helpers ----------------
DetectorFactory.seed = 0  # for consistent langdetect results

def clean_text(text):
    """Normalize text without breaking non-Latin scripts"""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def extract_title(soup):
    """Extract headline with multiple strategies for multi-language"""
    # 1. <h1>/<h2>
    candidates = [t.get_text(strip=True) for t in soup.find_all(['h1','h2']) if t.get_text(strip=True)]
    if candidates:
        return max(candidates, key=len)

    # 2. <title> tag
    title_tag = soup.find('title')
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)

    # 3. Meta tags
    meta_desc = soup.find('meta', {'name':'description'}) or soup.find('meta', {'property':'og:title'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc.get('content').strip()

    return ""

def extract_body(soup):
    """Extract main article body for multi-language content"""
    candidates = []

    # 1. <article> tags
    for article_tag in soup.find_all('article'):
        text = article_tag.get_text(separator=' ', strip=True)
        if text:
            candidates.append(text)

    # 2. All <p> tags
    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
    candidates.extend(paragraphs)

    # 3. Large <div> blocks
    divs = [div.get_text(separator=' ', strip=True) for div in soup.find_all('div') if div.get_text(strip=True)]
    candidates.extend(divs)

    # 4. Fallback: meta description
    if not candidates:
        meta_desc = soup.find('meta', {'name':'description'}) or soup.find('meta', {'property':'og:description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        return ""

    # Return the largest block
    return max(candidates, key=len)

def extract_article(article):
    html_content = article.get('html', '')
    if not html_content.strip():
        print(f"⚠️ Empty HTML, skipping {article.get('url')}")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    title = clean_text(extract_title(soup))
    body = clean_text(extract_body(soup))

    if not title or not body or len(body.split()) < 50:
        print(f"⚠️ Could not extract properly: {article.get('url')}")
        return None

    language = detect_language(body)

    return {
        'url': article.get('url'),
        'source': article.get('source'),
        'type': article.get('type', 'unknown'),
        'language': language,
        'title': title,
        'body': body
    }

# ---------------- Extraction ----------------
def extract_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    extracted_articles = []
    skipped_count = 0

    for article in articles:
        extracted = extract_article(article)
        if extracted:
            extracted_articles.append(extracted)
        else:
            skipped_count += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_articles, f, ensure_ascii=False, indent=4)

    print(f"✅ Extracted {len(extracted_articles)} articles -> {output_path}")
    if skipped_count > 0:
        print(f"⚠️ Skipped {skipped_count} articles due to missing title/body or too short content")

# ---------------- Run ----------------
if __name__ == "__main__":
    extract_json(PREPROCESSED_TRAIN, os.path.join(OUTPUT_DIR, 'training_articles.json'))
    extract_json(PREPROCESSED_TEST, os.path.join(OUTPUT_DIR, 'testing_articles.json'))
