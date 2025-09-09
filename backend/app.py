from flask import Flask
from routes.articles import articles_bp

# Create Flask app
app = Flask(__name__)

# Register Blueprint for articles API
app.register_blueprint(articles_bp, url_prefix="/api/articles")

# Optional: handle CORS if frontend will fetch API
from flask_cors import CORS
CORS(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
