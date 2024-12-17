import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity, cosine_distances
from fuzzywuzzy import fuzz

movies_df = pd.read_csv('../../data/cleaned/cleaned_movies_details.csv', usecols=['title','genres', 'overview', 'year', 'img_url', 'director', 'stars', 'movie_id'])
embeddings = np.load('../../checkpoints/embeddings.npz')['embeds']

cosine_dist_matrix = cosine_distances(embeddings)
movieid_to_index = {movie_id: idx for idx, movie_id in enumerate(movies_df['movie_id'])}

# Function to find the closest title
def matching_score(a, b):
    return fuzz.ratio(a, b)

def get_index_from_title(title):
    return movies_df[movies_df.title == title].index.values[0]

def get_title_from_index(index):
    return movies_df[movies_df.index == index]['title'].values[0]

def find_closest_title(title):
    leven_scores = list(enumerate(movies_df['title'].apply(matching_score, b=title)))
    sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True)
    closest_title = get_title_from_index(sorted_leven_scores[0][0])
    distance_score = sorted_leven_scores[0][1]
    return closest_title, distance_score

def contents_based_recommender(movie, num_of_recomm=10, movieid_to_index=movieid_to_index, cosine_dist_matrix=cosine_dist_matrix):
    closest_title, score = find_closest_title(movie)
    name = closest_title if score != 100 else None
    
    movie_id = movies_df[movies_df['title'] == closest_title]['movie_id'].values[0]
    
    if movie_id not in movieid_to_index:
        raise ValueError('Movie ID does not exist.')
    
    index = movieid_to_index[movie_id]
    similarity_scores = 1 - cosine_dist_matrix[index]
    similarity_scores[index] = -np.inf
    
    top_indices = np.argsort(similarity_scores)[-num_of_recomm:][::-1] 
    
    recommended_movies = []
    for idx in top_indices:
        movie = movies_df.iloc[idx]
        movie_details = {
            'title': movie['title']
        }
        recommended_movies.append(movie_details)
    titles = [movie_details['title'] for movie_details in recommended_movies]
            
    return titles, name