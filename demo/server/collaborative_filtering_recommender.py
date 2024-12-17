import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy import sparse
from scipy.sparse import coo_matrix, csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import math

rating_df = pd.read_csv('../../data/cleaned/cleaned_user_rating.csv')
rating_df_copy = rating_df.copy()
movies_df = pd.read_csv('../../data/cleaned/cleaned_movies_details.csv', usecols=['movie_id', 'title', 'img_url'])

# Only keep users with >= 5 ratings
user_rating_counts = rating_df_copy['user_id'].value_counts()
users_with_5_or_more_ratings = user_rating_counts[user_rating_counts >= 5].index
rating_df_copy = rating_df_copy[rating_df_copy['user_id'].isin(users_with_5_or_more_ratings)]
rating_df_copy = rating_df_copy.reset_index(drop=True)

# ID to number
rating_df_copy['user_id_number'] = rating_df_copy['user_id'].astype('category').cat.codes.values
rating_df_copy['movie_id_number'] = rating_df_copy['movie_id'].astype('category').cat.codes.values

all_data = rating_df_copy[['user_id_number', 'movie_id_number', 'rating']].values
number_to_user_id = dict(enumerate(rating_df_copy['user_id'].astype('category').cat.categories))
user_id_to_number = {v: k for k, v in number_to_user_id.items()}
number_to_movie_id = dict(enumerate(rating_df_copy['movie_id'].astype('category').cat.categories))
movie_id_to_number = {v: k for k, v in number_to_movie_id.items()}

# We may store an array for user_id <=> user_id_number and other types
def get_movieURL(movie_id):
    return movies_df[movies_df.movie_id == movie_id].img_url.values[0]
    
def get_user_history_ratings(user_id):
    user_ratings = rating_df_copy[rating_df_copy['user_id'] == user_id][['movie_id', 'rating']].head(10)
    history = []
    for _, row in user_ratings.iterrows():
        movie_title = movies_df[movies_df.movie_id == row['movie_id']].title.values[0]
        history.append([movie_title, row['rating']])
    return history

class CF(object):
    def __init__(self, train_data, n_neighbor, dist_func=cosine_similarity, type=1):
        self.type = type  # user-user (1) or item-item (0) CF
        self.train_data = train_data
        self.n_neighbor = n_neighbor
        self.dist_func = dist_func
        self.n_users = int(np.max(self.train_data[:, 0])) + 1
        self.n_movies = int(np.max(self.train_data[:, 1])) + 1

    def fit(self):
        if self.type == 1:
            self._fit_user_user()
        else:
            self._fit_item_item()
            
    def _fit_user_user(self):
        users = self.train_data[:, 0]
        self.Ybar_data = self.train_data.copy()
        
        self.mu = np.zeros((self.n_users + 100,))
        for u in range(self.n_users):
            ids = np.where(users == u)[0].astype(np.int32)
            ratings = self.train_data[ids, 2]
            self.mu[u] = np.mean(ratings) if len(ratings) > 0 else 0
            self.Ybar_data[ids, 2] = ratings - self.mu[u]
        
        self.Ybar = coo_matrix(
            (self.Ybar_data[:, 2], (self.Ybar_data[:, 0], self.Ybar_data[:, 1])),
            shape=(self.n_users + 100, self.n_movies + 100)
        ).tocsr()

    def load_model(self, file_path):
        loaded = np.load(file_path)
        self.Ybar = csr_matrix(
            (loaded['ybar_data'], loaded['ybar_indices'], loaded['ybar_indptr']),
            shape=loaded['ybar_shape']
        )
        self.mu = loaded['mu']

    def recommend(self, u):
        ids = np.where(self.train_data[:, 0] == u)[0]
        items_rated_by_u = self.train_data[ids, 1].tolist()
        recommended_items = {}
        
        for i in range(self.n_movies):
            if i not in items_rated_by_u:
                recommended_items[i] = self.pred(u, i)
                
        return sorted(recommended_items, key=recommended_items.get, reverse=True)
    
    def pred(self, u, i):
        ids = np.where(self.train_data[:, 1] == i)[0].astype(np.int32)
        users_rated_i = self.train_data[ids, 0].astype(np.int32)
        
        if len(users_rated_i) == 0:
            return self.mu[u]
            
        sim = self.dist_func(self.Ybar[u], self.Ybar[users_rated_i]).flatten()
        if len(sim) < self.n_neighbor:
            return self.mu[u]
        
        a = np.argsort(sim)[-self.n_neighbor:]
        nearest_sim = sim[a]
        r = self.Ybar[users_rated_i[a], i]
        
        return (r.T @ nearest_sim) / (np.abs(nearest_sim).sum() + 1e-12) + self.mu[u]

def cf_recommender(user_id, num_recommendations=10):
    cf_model = CF(all_data, n_neighbor=5, type=1)
    cf_model.fit()
    
    if user_id not in user_id_to_number:
        return []  
    user_id_number = user_id_to_number[user_id]
    
    recommended_movie_numbers = cf_model.recommend(user_id_number)[:num_recommendations]
    recommended_titles = []
    for movie_number in recommended_movie_numbers:
        movie_id = number_to_movie_id[movie_number]
        title = movies_df[movies_df.movie_id == movie_id]['title'].values[0]
        recommended_titles.append(title)
        
    return recommended_titles