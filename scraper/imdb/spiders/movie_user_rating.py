import scrapy
import pandas as pd

class MovieUserRatingSpider(scrapy.Spider):
    name = 'movie_user_rating'
    df = pd.read_csv("./data/movies_details.csv", low_memory=False)
    df['title_id'] = df['url'].str.extract(r'/title/([^/]+)')
    title_id_list = df['title_id'].unique()
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/title/{}/reviews/?sort=num_votes%2Cdesc'.format(title_id) for title_id in title_id_list]

    def parse(self, response):
        user_urls = response.xpath("//a[@data-testid='author-link']/@href").getall()
        ratings = response.xpath("//span[@class='ipc-rating-star--rating']/text()").getall()

        for user_url, rating in zip(user_urls, ratings):
            user_id = user_url.split('/')[-2]
            movie_id = response.url.split('/')[4] 

            yield {
                'user_id': user_id,
                'movie_id': movie_id,
                'rating': rating
            }