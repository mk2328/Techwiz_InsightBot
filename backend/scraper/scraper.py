# scraper_requests_playwright.py
import pandas as pd
import json
import os
import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# ---------------- Paths ----------------
RAW_TRAINING_PATH = "data/training_articles.json"
RAW_TESTING_PATH = "data/testing_articles.json"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- Functions ----------------
def scrape_requests(url, timeout=15):
    """Try to scrape page using requests + BS4"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            return str(soup)
        else:
            return ""
    except Exception as e:
        return ""

async def scrape_playwright(url):
    """Scrape page using Playwright (JS-rendered pages)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(url, timeout=120000)
            await page.wait_for_load_state("networkidle", timeout=120000)
            html = await page.content()
        except Exception as e:
            html = ""
        await browser.close()
    return html

async def scrape_sites(df, type_):
    articles = []
    for _, row in df.iterrows():
        url = row["url"]
        # Step 1: Try requests first
        html = scrape_requests(url)
        if html:
            print(f"✅ Requests scraped {url}")
        else:
            # Step 2: Fallback to Playwright
            print(f"🔄 Requests failed, using Playwright for {url}")
            html = await scrape_playwright(url)
            if html:
                print(f"✅ Playwright scraped {url}")
            else:
                print(f"❌ Could not scrape {url}")
        articles.append({
            "url": url,
            "source": url.split("//")[-1].split("/")[0],
            "html": html,
            "type": type_
        })
    return articles

# ---------------- Main ----------------
async def main():
    df = pd.read_csv("data/websites.csv")
    training_df = df[df["type"] == "training"]
    testing_df = df[df["type"] == "testing"]

    print("Scraping training sites...")
    training_articles = await scrape_sites(training_df, "training")
    with open(RAW_TRAINING_PATH, "w", encoding="utf-8") as f:
        json.dump(training_articles, f, ensure_ascii=False, indent=2)

    print("Scraping testing sites...")
    testing_articles = await scrape_sites(testing_df, "testing")
    with open(RAW_TESTING_PATH, "w", encoding="utf-8") as f:
        json.dump(testing_articles, f, ensure_ascii=False, indent=2)

    print("✅ All articles scraped and saved in /data")

if __name__ == "__main__":
    asyncio.run(main())
