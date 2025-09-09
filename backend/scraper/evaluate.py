import json
import os

def quality_check(article):
    title = article.get("title", "")
    body = article.get("body", "")

    title_ok = title and len(title) > 15
    body_ok = body and len(body.split()) > 100

    return int(title_ok) + int(body_ok)  # 0=fail, 1=partial, 2=good

def evaluate(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    total = len(articles)
    results = {"good": 0, "partial": 0, "fail": 0}

    for art in articles:
        score = quality_check(art)
        if score == 2:
            results["good"] += 1
        elif score == 1:
            results["partial"] += 1
        else:
            results["fail"] += 1

    print(f"\n📊 Evaluation for {file_path}")
    print(f"Total: {total}")
    print(f"Good: {results['good']} ({results['good']/total:.1%})")
    print(f"Partial: {results['partial']} ({results['partial']/total:.1%})")
    print(f"Fail: {results['fail']} ({results['fail']/total:.1%})")

if __name__ == "__main__":
    base = os.path.join("data", "preprocessed")
    evaluate(os.path.join(base, "training_articles.json"))
    evaluate(os.path.join(base, "testing_articles.json"))
