from flask import Blueprint, jsonify
from backend.scraper.extract_articles import extract_article
import json

articles_bp = Blueprint("articles_bp", __name__)

# Load preprocessed training articles
with open("data/preprocessed/training_articles.json", "r", encoding="utf-8") as f:
    training_articles = json.load(f)

@articles_bp.route("/", methods=["GET"])
def get_articles():
    # Example: first 5 URLs for demo
    urls = [a["url"] for a in training_articles[:5]]
    extracted_articles = []

    for url in urls:
        article = extract_article(url)
        if article and article["title"] and article["body"]:
            # Add language field from training_articles JSON
            lang = next((item["language"] for item in training_articles if item["url"] == url), "unknown")
            article["language"] = lang
            extracted_articles.append(article)

    return jsonify(extracted_articles)
