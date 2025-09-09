# extractor.py
import os
import json
import re
from bs4 import BeautifulSoup
import dateparser

# ---------------- Paths ----------------
PREPROCESSED_DIR = 'data/preprocessed/'
EXTRACTED_DIR = 'data/extracted/'

os.makedirs(EXTRACTED_DIR, exist_ok=True)

# ---------------- Headline Extraction ----------------
def extract_headline(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Try <h1>
    h1_tags = soup.find_all('h1')
    if h1_tags:
        return max(h1_tags, key=lambda x: len(x.get_text(strip=True))).get_text(strip=True)

    # 2. Try <h2>
    h2_tags = soup.find_all('h2')
    if h2_tags:
        return max(h2_tags, key=lambda x: len(x.get_text(strip=True))).get_text(strip=True)

    # 3. Open Graph meta
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        return og_title['content'].strip()

    # 4. Fallback to <title>
    if soup.title:
        return soup.title.get_text(strip=True)

    return None

# ---------------- Body Extraction ----------------
def extract_body(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Longest <article>
    articles = soup.find_all('article')
    if articles:
        article_texts = [a.get_text(separator=' ', strip=True) for a in articles]
        largest_article = max(article_texts, key=len)
        if len(largest_article) > 100:
            return largest_article

    # 2. Longest <div> with mostly <p>
    divs = soup.find_all('div')
    max_text = ''
    for div in divs:
        p_tags = div.find_all('p')
        if p_tags:
            div_text = ' '.join([p.get_text(strip=True) for p in p_tags])
            if len(div_text) > len(max_text):
                max_text = div_text
    if len(max_text) > 100:
        return max_text

    # 3. Join all <p> tags with >50 chars
    paragraphs = soup.find_all('p')
    if paragraphs:
        body = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        if body:
            return body

    return None

# ---------------- Publication Date Extraction ----------------
def extract_date(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 1. <time> tag
    time_tag = soup.find('time')
    if time_tag and time_tag.get_text(strip=True):
        dt = dateparser.parse(time_tag.get_text(strip=True))
        if dt:
            return str(dt)

    # 2. Open Graph meta
    meta_time = soup.find('meta', property='article:published_time')
    if meta_time and meta_time.get('content'):
        dt = dateparser.parse(meta_time['content'])
        if dt:
            return str(dt)

    # 3. Regex fallback
    date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', html)
    if date_match:
        dt = dateparser.parse(date_match.group(1))
        if dt:
            return str(dt)

    return None

# ---------------- Main Extraction Function ----------------
def extract_from_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    extracted_articles = []
    for article in articles:
        html_content = article.get('html', '')
        if not html_content.strip():
            continue

        headline = extract_headline(html_content)
        body = extract_body(html_content)
        pub_date = extract_date(html_content)

        extracted_articles.append({
            'url': article.get('url'),
            'source': article.get('source'),
            'headline': headline,
            'body': body,
            'publication_date': pub_date
        })

    # Save extracted JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_articles, f, ensure_ascii=False, indent=4)

    print(f"Extracted {len(extracted_articles)} articles -> {output_path}")
    return extracted_articles

# ---------------- Run Extraction Only ----------------
if __name__ == "__main__":
    # --- Training Extraction ---
    extract_from_json(
        os.path.join(PREPROCESSED_DIR, 'training_articles.json'),
        os.path.join(EXTRACTED_DIR, 'training_articles.json')
    )

    # --- Testing Extraction ---
    extract_from_json(
        os.path.join(PREPROCESSED_DIR, 'testing_articles.json'),
        os.path.join(EXTRACTED_DIR, 'testing_articles.json')
    )

    print("\nExtraction done! You can now run 'accuracy_checker.py' anytime to evaluate accuracy.")
