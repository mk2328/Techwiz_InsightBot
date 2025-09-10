# evaluate_extractor.py
import sys
import json
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from extractor_super_robust import extract_article, clean_text

# ---------------- Paths ----------------
PREPROCESSED_DIR = 'data/preprocessed/'
EXTRACTED_DIR = 'data/extracted_multilang/'

PREPROCESSED_TEST = os.path.join(PREPROCESSED_DIR, 'testing_articles.json')
TESTING_GOLD = os.path.join(PREPROCESSED_DIR, 'testing_gold.json')
EXTRACTED_REPORT = os.path.join(EXTRACTED_DIR, 'evaluation_report.json')

# ---------------- Helpers ----------------
def jaccard_similarity(text1, text2):
    """Compute Jaccard similarity between two texts"""
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

# ---------------- Evaluation ----------------
def evaluate_extractor(input_path, gold_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    with open(gold_path, 'r', encoding='utf-8') as f:
        gold_articles = json.load(f)

    total = len(gold_articles)
    successful = 0
    failed_urls = []

    # Create dict for quick lookup
    gold_dict = {a['url']: a for a in gold_articles}

    for article in articles:
        url = article.get('url')
        gold = gold_dict.get(url)
        if not gold:
            failed_urls.append(url)
            continue

        extracted = extract_article(article)
        if not extracted:
            failed_urls.append(url)
            continue

        # Compute similarity
        title_sim = jaccard_similarity(extracted['title'], gold['headline'])
        body_sim = jaccard_similarity(extracted['body'], gold['body'])

        if title_sim >= 0.7 and body_sim >= 0.7:
            successful += 1
        else:
            failed_urls.append(url)

    accuracy = (successful / total) * 100 if total > 0 else 0

    report = {
        'total_test_articles': total,
        'successfully_extracted': successful,
        'failed_extractions': len(failed_urls),
        'accuracy_percent': round(accuracy, 2),
        'failed_urls': failed_urls
    }

    os.makedirs(EXTRACTED_DIR, exist_ok=True)
    with open(EXTRACTED_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    print(f"✅ Evaluation complete! Accuracy: {report['accuracy_percent']}%")
    print(f"⚠️ Failed URLs ({len(failed_urls)}):")
    for url in failed_urls:
        print(f"  - {url}")

    return report

# ---------------- Run ----------------
if __name__ == "__main__":
    evaluate_extractor(PREPROCESSED_TEST, TESTING_GOLD)
