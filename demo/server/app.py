from flask import Flask, request, jsonify
from flask_cors import CORS 
from content_based_recommender import *
from collaborative_filtering_recommender import *

app = Flask(__name__)
CORS(app) 

@app.route("/api/content-based-recommend", methods=["POST"])
def content_based_recommend_movies():
    try:
        data = request.get_json()
        movie_title = data.get("movie_title")

        # Get recommended movies as a list of titles
        recommended_movies, suggestion = contents_based_recommender(
            movie_title, num_of_recomm=10
        )

        return jsonify(
            {
                "recommendations": recommended_movies,
                "suggestion": suggestion,
            }
        )

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})

@app.route("/api/collaborative-filtering-recommend", methods=["POST"])
def collaborative_filteringl_recommend_movies():
    try:
        data = request.get_json()
        userId = data.get("userId")

        # Get recommended movies as a list of titles
        recommended_movies = item_based_recommender(userId)
        history = get_user_history_ratings(userId)
        return jsonify({"recommendations": recommended_movies, "history": history})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(port=5000)