from pymongo import MongoClient
import json

# MongoDB connection
client = MongoClient(
    "mongodb+srv://muskankamran3369:muskurahat2328U@cluster0.fxk1min.mongodb.net/insightbot_db?retryWrites=true&w=majority&appName=Cluster0"
)
db = client.insightbot_db
articles_collection = db.articles  # single collection (training + testing)

# Load training data
with open("data/preprocessed/training_articles.json", "r", encoding="utf-8") as f:
    training_articles = json.load(f)

# Add dataset label and remove old _id (avoid duplicate key error)
for art in training_articles:
    art["dataset_type"] = "training"
    art.pop("_id", None)  # remove _id if it exists

# Load testing data
with open("data/preprocessed/testing_articles.json", "r", encoding="utf-8") as f:
    testing_articles = json.load(f)

# Add dataset label and remove old _id
for art in testing_articles:
    art["dataset_type"] = "testing"
    art.pop("_id", None)

# Combine both
articles = training_articles + testing_articles

# Insert into MongoDB
if articles:
    result = articles_collection.insert_many(articles)
    print(f"✅ Inserted {len(result.inserted_ids)} articles into MongoDB!")
else:
    print("⚠️ No articles to insert.")
