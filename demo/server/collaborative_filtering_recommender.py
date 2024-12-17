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

class RISMF(object):
    global user_id_to_number, number_to_user_id, movie_id_to_number, number_to_movie_id
    def __init__(self, train_data, test_data, n_factors=10, learning_rate=0.01, lambda_reg=0.1, n_epochs=10):
        self.train_data = train_data
        self.test_data = test_data
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.lambda_reg = lambda_reg
        self.n_epochs = n_epochs
        self.n_users = int(np.max(self.train_data[:, 0])) + 1
        self.n_movies = int(np.max(self.train_data[:, 1])) + 1
        
        self.P = np.random.normal(scale=1.0 / self.n_factors, size=(self.n_users + 100, self.n_factors))
        self.Q = np.random.normal(scale=1.0 / self.n_factors, size=(self.n_movies + 100, self.n_factors))
    
    def incremental_update(self, new_ratings):
        # Convert new_ratings from IDs to numerical indices
        processed_ratings = []
        for user_id, movie_id, rating in new_ratings:
            # Check and update user_id_to_number
            if user_id not in user_id_to_number:
                user_id_to_number[user_id] = self.n_users
                number_to_user_id[self.n_users] = user_id
                self.n_users += 1

            # Check and update movie_id_to_number
            if movie_id not in movie_id_to_number:
                movie_id_to_number[movie_id] = self.n_movies
                number_to_movie_id[self.n_movies] = movie_id
                self.n_movies += 1

            # Convert IDs to numbers and append to processed_ratings
            u = user_id_to_number[user_id]
            i = movie_id_to_number[movie_id]
            processed_ratings.append([u, i, rating])

        # Convert processed_ratings to a NumPy array
        processed_ratings = np.array(processed_ratings)
        # Update the train_data matrix with the new ratings
        self.train_data = np.vstack((self.train_data, processed_ratings))
        # Incremental learning using new ratings
        for u, i, r in processed_ratings:
            u, i, r = int(u), int(i), int(r)
            pred = self.pred(u, i)
            error = r - pred
            # Update P and Q
            self.P[u, :] += self.learning_rate * (error * self.Q[i, :] - self.lambda_reg * self.P[u, :])
            self.Q[i, :] += self.learning_rate * (error * self.P[u, :] - self.lambda_reg * self.Q[i, :])

    def pred(self, u, i):
        return self.P[u, :].dot(self.Q[i, :].T)
            
    def recommend(self, u):        
        """
        Determine all unrated items should be recommended for user u
        """
        ids = np.where(self.train_data[:, 0] == u)[0]
        items_rated_by_u = self.train_data[ids, 1].tolist()
        recommended_items = {}
        for i in range(self.n_movies):
            if i not in items_rated_by_u:
                recommended_items[i] = self.pred(u, i)

        return sorted(recommended_items, key=recommended_items.get, reverse=True)
    
    def loss(self, data):
        L = 0
        for u, i, r in data:
            u, i = int(u), int(i)
            pred = self.pred(u, i)
            L += (r - pred)**2
        L /= data.shape[0]
        return math.sqrt(L)

def load_model(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def item_based_recommender(user_id, num_recommendations=10):
    try:
        rating_df_copy['user_id_number'] = rating_df_copy['user_id'].astype('category').cat.codes.values
        rating_df_copy['movie_id_number'] = rating_df_copy['movie_id'].astype('category').cat.codes.values
        
        number_to_user_id = dict(enumerate(rating_df_copy['user_id'].astype('category').cat.categories))
        user_id_to_number = {v: k for k, v in number_to_user_id.items()}
        number_to_movie_id = dict(enumerate(rating_df_copy['movie_id'].astype('category').cat.categories))
        
        user_number = user_id_to_number[user_id]
        
        cf_model = load_model("../../checkpoints/rismf_nf300_lr0.006.pkl")
        recommended_items = cf_model.recommend(user_number)
        top_recommendations = recommended_items[:num_recommendations]
        
        recommended_movies = []
        for movie_number in top_recommendations:
            movie_id = number_to_movie_id[movie_number]
            movie_title = movies_df[movies_df.movie_id == movie_id].title.values[0]
            recommended_movies.append(movie_title)
            
        return recommended_movies
        
    except Exception as e:
        print(f"Error in recommendation: {str(e)}")
        return []