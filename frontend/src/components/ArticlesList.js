import React, { useEffect, useState } from "react";
import axios from "axios";

const ArticlesList = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/api/articles/")
      .then((res) => {
        console.log("Fetched articles:", res.data); // Debugging
        setArticles(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching articles:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading articles...</p>;

  return (
    <div className="articles-container">
      <h2>Articles</h2>
      <ul>
        {articles.map((article, index) => (
          <li key={index} className="article-card">
            <h3>{article.title}</h3>
            <p>{article.body ? article.body.slice(0, 200) : "No content"}...</p>
            <a href={article.url} target="_blank" rel="noreferrer">
              Read More
            </a>
            <p>
              <strong>Dataset:</strong> {article.dataset_type} |{" "}
              <strong>Language:</strong> {article.language}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ArticlesList;
