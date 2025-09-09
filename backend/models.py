from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

client = MongoClient("mongodb+srv://muskankamran3369:muskurahat2328U@cluster0.fxk1min.mongodb.net/insightbot_db?retryWrites=true&w=majority&appName=Cluster0")

try:
    client.server_info()
    print("Database connected successfully")
except ServerSelectionTimeoutError as err:
    print("Could not connect to database. Please check your connection string or network.")
    print(err)


db = client.insightbot_db
articles_collection = db.articles
keywords_collection = db.keywords
users_collection = db.users