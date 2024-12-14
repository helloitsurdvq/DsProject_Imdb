import React from "react";
import { useNavigate } from "react-router-dom";
import "./RecommendationPage.css";

const RecommendationPage = () => {
  const navigate = useNavigate();

  return (
    <div className="recommendation-welcome">
      <div className="welcome-content">
        <h1>Discover Your Next Favorite Movie</h1>
        <p>Choose how you'd like to get recommendations:</p>
        
        <div className="recommendation-options">
          <div className="option-card" onClick={() => navigate("/movies/content-based/recommendation")}>
            <i className="fas fa-film"></i>
            <h3>Movie-Based Recommendations</h3>
            <p>Get recommendations based on a movie you love</p>
            <button className="option-button">Start Exploring</button>
          </div>

          <div className="option-card" onClick={() => navigate("/movies/collaborative-filtering/recommendation")}>
            <i className="fas fa-users"></i>
            <h3>Personalized Recommendations</h3>
            <p>Get recommendations based on your viewing history</p>
            <button className="option-button">View Recommendations</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationPage;