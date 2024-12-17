import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./CollaborativeRecommendationPage.css";

const CollaborativeRecommendationPage = () => {
  const [userId, setUserId] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const handleRecommendation = async () => {
    try {
      setLoading(true);

      const response = await axios.post(
        "http://localhost:5000/api/collaborative-filtering-recommend",
        { userId }
      );
      const movieTitles = response.data.recommendations;
      const historyData = response.data.history || [];

      const allMovieTitles = [...movieTitles, ...historyData.map(item => item[0])];
      const movieDetailsPromises = allMovieTitles.map(async (title) => {
        const tmdbResponse = await axios.get(
          `https://api.themoviedb.org/3/search/movie`,
          {
            params: {
              api_key: "4e44d9029b1270a757cddc766a1bcb63",
              query: typeof title === 'string' ? title : title[0],
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
          overview: movieDetails.overview || '',
          posterPath: movieDetails.poster_path,
          userRating: typeof title === 'string' ? null : title[1],
        };
      });

      const allMovieDetails = await Promise.all(movieDetailsPromises);
      
      const historyMovies = allMovieDetails.slice(movieTitles.length).map((movie, index) => ({
        ...movie,
        userRating: historyData[index][1]
      }));
      const recommendedMovies = allMovieDetails.slice(0, movieTitles.length);
      
      setRecommendations(recommendedMovies.filter(movie => movie !== null));
      setHistory(historyMovies.filter(movie => movie !== null));
      setError("");
    } catch (error) {
      setError("Error fetching recommendations. Please try again later.");
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recommendation-page">
      <div className="search-bar">
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter your userId"
        />
        <button onClick={handleRecommendation} disabled={loading}>
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </div>

      <div>
        {history.length > 0 && <h2>Your Rating History:</h2>}
        <div className="movie-list">
          {history
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
                      src={`https://image.tmdb.org/t/p/original${movie.posterPath}`}
                      alt={movie.original_title}
                    />
                    <div className="movie-details">
                      <h3>{movie.original_title}</h3>
                      <p className="rating-badge">
                        <i className="fas fa-star" style={{ color: "#ffd700" }}></i>
                        <span>History User Rating: {movie.userRating}/10</span>
                      </p>
                      <p>Release Date: {movie.releaseDate}</p>
                      <p>{movie.overview ? `${movie.overview.slice(0, 118)}...` : ''}</p>
                    </div>
                  </div>
                </Link>
                <div className="movie-actions">
                  <a
                    rel="noreferrer"
                    href={`https://www.imdb.com/search/title/?title=${encodeURIComponent(movie.original_title)}`}
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

      <div>
        {recommendations.length > 0 && <h2>You may like these movies:</h2>}
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
                      src={`https://image.tmdb.org/t/p/original${movie.posterPath}`}
                      alt={movie.original_title}
                    />
                    <div className="movie-details">
                      <h3>{movie.original_title}</h3>
                      <p>Release Date: {movie.releaseDate}</p>
                      <p>{movie.overview ? `${movie.overview.slice(0, 118)}...` : ''}</p>
                    </div>
                  </div>
                </Link>
                <div className="movie-actions">
                  <a
                    rel="noreferrer"
                    href={`https://www.imdb.com/search/title/?title=${encodeURIComponent(movie.original_title)}`}
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
  );
};

export default CollaborativeRecommendationPage;