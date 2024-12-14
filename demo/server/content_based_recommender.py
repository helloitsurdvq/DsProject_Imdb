import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from fuzzywuzzy import fuzz

movies_df = pd.read_csv('../../data/cleaned/cleaned_movies_details.csv', usecols=['title','genres', 'overview', 'year', 'img_url', 'director', 'stars', 'movie_id'])
sim_matrix = np.load('../../checkpoints/sim_matrix.npy')

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

def contents_based_recommender(movie, num_of_recomm=10):
    closest_title, similarity_score = find_closest_title(movie)    
    suggestion = None
    
    if similarity_score != 100:
        suggestion = closest_title
        
    movie_index = get_index_from_title(closest_title)
    movie_list = list(enumerate(sim_matrix[int(movie_index)]))
    
    similar_movies = list(filter(lambda x: x[0] != int(movie_index), 
                               sorted(movie_list, key=lambda x: x[1], reverse=True)))
    
    recommended_movies = [get_title_from_index(movie[0]) 
                        for movie in similar_movies[:num_of_recomm]]
    
    return recommended_movies, suggestion