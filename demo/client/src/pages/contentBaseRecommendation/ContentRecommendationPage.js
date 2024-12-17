import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./ContentRecommendationPage.css";

const ContentRecommendationPage = () => {
  const [movieTitle, setMovieTitle] = useState("");
  const [suggestion, setSuggestion] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestionDetails, setSuggestionDetails] = useState(null);

  const handleRecommendation = async () => {
    try {
      setLoading(true);
      let query = movieTitle.toLowerCase();
      const response = await axios.post(
        "http://localhost:5000/api/content-based-recommend",
        { movie_title: query }
      );
      const movieTitles = response.data.recommendations;
      setSuggestion(response.data.suggestion);

      if (response.data.suggestion) {
        const suggestionResponse = await axios.get(
          `https://api.themoviedb.org/3/search/movie`,
          {
            params: {
              api_key: "4e44d9029b1270a757cddc766a1bcb63",
              query: response.data.suggestion,
            },
          }
        );
        if (suggestionResponse.data.results.length > 0) {
          setSuggestionDetails(suggestionResponse.data.results[0]);
        }
      }

      const movieDetailsPromises = movieTitles.map(async (title) => {
        const tmdbResponse = await axios.get(
          `https://api.themoviedb.org/3/search/movie`,
          {
            params: {
              api_key: "4e44d9029b1270a757cddc766a1bcb63",
              query: title,
            },
          }
        );
        if (tmdbResponse.data.results.length === 0) {
          return null;
        }

        const movieDetails = tmdbResponse.data.results[0];
        return {
          id: movieDetails.id,
          original_title: movieDetails.original_title,
          releaseDate: movieDetails.release_date,
          overview: movieDetails.overview,
          posterPath: movieDetails.poster_path,
        };
      });

      const movieDetails = await Promise.all(movieDetailsPromises);
      setRecommendations(movieDetails);
    } catch (error) {
      setError("Error fetching recommendations");
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = async () => {
    setMovieTitle(suggestion);
    handleRecommendation();
  };

  return (
    <div className="recommendation-page">
      <div className="search-bar">
        <input
          type="text"
          value={movieTitle}
          onChange={(e) => setMovieTitle(e.target.value)}
          placeholder="Enter your favorite movie title"
        />
        <button onClick={handleRecommendation} disabled={loading}>
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </div>

      <div className="content-container">
        {/* Suggestion Section */}
        <div className="suggestion-section">
          {error && <p className="error-message">{error}</p>}
          {suggestion && suggestionDetails && (
            <div>
              <h2 className="suggestion-text">Do you mean:</h2>
              <div
                className="movie-container"
                onClick={handleSuggestionClick}
                style={{ cursor: "pointer" }}
              >
                <Link
                  to={`/movie/${suggestionDetails.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ textDecoration: "none", color: "inherit" }}
                >
                  <div className="movie-poster">
                    <img
                      src={`https://image.tmdb.org/t/p/original${suggestionDetails.poster_path}`}
                      alt={suggestionDetails.original_title}
                    />
                    <div className="movie-details">
                      <h3>{suggestionDetails.original_title}</h3>
                      <p>Release Date: {suggestionDetails.release_date}</p>
                      <p>{suggestionDetails.overview.slice(0, 118) + "..."}</p>
                    </div>
                  </div>
                </Link>
                <div className="movie-actions">
                  <a
                    rel="noreferrer"
                    href={`https://www.imdb.com/search/title/?title=${encodeURIComponent(
                      suggestionDetails.original_title
                    )}`}
                    target="_blank"
                    style={{ textDecoration: "none" }}
                  >
                    <span className="movie__imdbButton movie__Button">
                      IMDb <i className="newTab fas fa-external-link-alt"></i>
                    </span>
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recommendations Section */}
        <div className="recommendations-section">
          {suggestion && <h2>You may like these movies:</h2>}
          <div className="movie-list">
            {recommendations
              .filter((movie) => movie !== null)
              .map((movie, index) => (
                <div key={index} className="movie-container">
                  <Link
                    to={`/movie/${movie.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ textDecoration: "none", color: "inherit" }}
                  >
                    <div className="movie-poster">
                      <img
                        src={`https://image.tmdb.org/t/p/original${
                          movie ? movie.posterPath : ""
                        }`}
                        alt={movie ? movie.original_title : ""}
                      />
                      <div className="movie-details">
                        <h3>{movie ? movie.original_title : ""}</h3>
                        <p>Release Date: {movie ? movie.releaseDate : ""}</p>
                        <p>{movie ? movie.overview.slice(0, 118) + "..." : ""}</p>
                      </div>
                    </div>
                  </Link>
                  <div className="movie-actions">
                    <a
                      rel="noreferrer"
                      href={`https://www.imdb.com/search/title/?title=${encodeURIComponent(
                        movie ? movie.original_title : ""
                      )}`}
                      target="_blank"
                      style={{ textDecoration: "none" }}
                    >
                      <span className="movie__imdbButton movie__Button">
                        IMDb <i className="newTab fas fa-external-link-alt"></i>
                      </span>
                    </a>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentRecommendationPage;
