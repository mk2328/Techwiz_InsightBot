# scrape_training.py
import requests

def scrape_training_sites(df):
    articles = []
    for _, row in df.iterrows():
        url = row["url"]
        lang = row["language"] if "language" in row else "unknown"

        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            html_content = res.text

            articles.append({
                "url": url,
                "html": html_content,
                "language": lang,
                "type": "training"
            })
            print(f"✅ Scraped {url} successfully")

        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")

    return articles
