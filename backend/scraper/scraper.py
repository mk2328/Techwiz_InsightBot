from scrape_training import scrape_training_sites
from scrape_testing import scrape_testing_sites
import pandas as pd
import json

# Load the CSV
df = pd.read_csv("data/websites.csv")

# Split by type
training_df = df[df["type"] == "training"]
testing_df = df[df["type"] == "testing"]

print("Starting training data scraping...")
training_articles = scrape_training_sites(training_df)
print(f"Scraped {len(training_articles)} training articles.")

print("Starting testing data scraping...")
testing_articles = scrape_testing_sites(testing_df)
print(f"Scraped {len(testing_articles)} testing articles.")

# Save raw scraped HTML directly to JSON
with open("data/training_articles.json", "w", encoding="utf-8") as f:
    json.dump(training_articles, f, ensure_ascii=False, indent=2)

with open("data/testing_articles.json", "w", encoding="utf-8") as f:
    json.dump(testing_articles, f, ensure_ascii=False, indent=2)

print("All scraped articles saved to JSON files in /data folder.")
