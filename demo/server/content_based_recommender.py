import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from fuzzywuzzy import fuzz
import matplotlib
matplotlib.use('Agg')  # Set Matplotlib to use the Agg backend

# Load data
movies = pd.read_csv('../../cleaned_data/processed_movie_data.csv', usecols=['processed_title', 'genres', 'processed_overview'], sep=',', index_col=False, dtype='unicode')

# Import the cosine similarity matrix
sim_matrix = np.load('../../recommender/sim_matrix.npy')
# print(sim_matrix)


# Function to find the closest title
def matching_score(a, b):
    return fuzz.ratio(a, b)

# Function to return the most similar title to the words a user types
def find_closest_title(title):
    leven_scores = list(enumerate(movies['title'].apply(matching_score, b=title)))
    sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True)
    closest_title = get_title_from_index(sorted_leven_scores[0][0])
    distance_score = sorted_leven_scores[0][1]
    return closest_title, distance_score

# Function to get movie image URL from index
def get_movieimg_from_index(index):
    return movies[movies.index == index]['img_url'].values[0]

# Function to get index from title
def get_index_from_title(title):
    return movies[movies.title == title].index.values[0]

# Function to get title from index
def get_title_from_index(index):
    return movies[movies.index == index]['title'].values[0]

def contents_based_recommender(movie, num_of_recomm=10):
    closest_title, distance_score = find_closest_title(movie)
    recommended_movies = []

    if distance_score == 100:
        movie_index = get_index_from_title(closest_title)
        movie_list = list(enumerate(sim_matrix[int(movie_index)]))
        similar_movies = list(filter(lambda x: x[0] != int(movie_index), sorted(movie_list, key=lambda x: x[1], reverse=True)))

        for _, s in enumerate(similar_movies[:num_of_recomm]):
            recommended_movies.append(get_title_from_index(s[0]))
            print(recommended_movies)

    else:
        suggestion = 'Did you mean ' + str(closest_title) + '?'

        movie_index = get_index_from_title(closest_title)
        movie_list = list(enumerate(sim_matrix[int(movie_index)]))
        similar_movies = list(filter(lambda x: x[0] != int(movie_index), sorted(movie_list, key=lambda x: x[1], reverse=True)))

        for _, s in enumerate(similar_movies[:num_of_recomm]):
            recommended_movies.append(get_title_from_index(s[0]))

    return recommended_movies, suggestion
