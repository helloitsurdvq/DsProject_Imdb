import csv
import scrapy
from scrapy.spiders import CrawlSpider

popular_genres = {
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", 
    "Drama", "Family", "Fantasy", "Film Noir", "Game Show", "History", "Horror", 
    "Music", "Musical", "Mystery", "News", "Reality TV", "Romance", "Sci-Fi", 
    "Short", "Sport", "Talk Show", "Thriller", "War", "Western"
}

class MoviesDetailsSpider(CrawlSpider):
    name = 'movies_details'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/search/title/?title_type=feature&user_rating=1,10&count=250']
    def start_requests(self):
        with open('data/movies_url_data.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                url = row['url']
                yield scrapy.Request(url=url, callback=self.parse_movie_details)
            
    def parse_movie_details(self, response):
        title = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get()
        img_url = response.xpath("//meta[@property='og:image']/@content").get()
        year = response.xpath("//ul[@class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']/li/a/text()").get()
        director = response.xpath("//li[contains(.//text(), 'Director')]//ul/li/a/text()").get() or "N/A"
        stars = list(dict.fromkeys([item.xpath(".//text()").get() for item in response.xpath("//li[contains(.//text(), 'Stars')]//ul/li/a")]))
        duration = response.xpath("//li[@class='ipc-inline-list__item']/text()").get()
        genres = [
            genre for genre in [item.xpath('.//span/text()').get() for item in response.xpath("//div[@class='ipc-chip-list__scroller']/a")]
            if genre in popular_genres
        ]
        overview = response.xpath("//span[@data-testid='plot-xl']/text()").get()
        rating = response.xpath("(//div[@data-testid='hero-rating-bar__aggregate-rating__score'])[1]/span/text()").get() or 0.0
        num_rating = response.xpath("//div[@class='sc-d541859f-3 dwhNqC'][1]/text()").get() or 0
        num_user_review = response.xpath("(//span[contains(@class, 'three-Elements')])[1]/span/text()").get() or 0
        num_critic_review = response.xpath("(//span[contains(@class, 'three-Elements')])[2]/span/text()").get() or 0
        budget = response.xpath("//li[@data-testid='title-boxoffice-budget']/div/ul/li/span/text()").get(default=None) or "N/A"
        gross = response.xpath("//li[@data-testid='title-boxoffice-cumulativeworldwidegross']/div/ul/li/span/text()").get(default=None) or "N/A"
        country = response.xpath("//li[@data-testid='title-details-origin']//a/text()").get()
        metascore = response.xpath("//span[contains(@class, 'metacritic-score-box')]/text()").get() or "N/A"
        oscar_text = response.xpath("//ul[@class='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base']/li/a/text()").get() or "N/A"
        oscar = 'N/A' if oscar_text == 'Awards' else oscar_text
        win_and_nomination = response.xpath("//ul[@class='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base']/li/div/ul/li/span/text()").get(default=None) or "N/A"
        url = response.url

        yield {
            'title': title,
            'img_url': img_url,
            'year': year,
            'director': director,
            'stars': stars,
            'duration': duration,
            'genres': genres,
            'overview': overview,
            'rating': rating,
            'num_rating': num_rating,
            'num_user_review': num_user_review,
            'num_critic_review': num_critic_review,
            'budget': budget,
            'gross': gross,
            'country': country,
            'metascore': metascore,
            'oscar': oscar,
            'win_and_nomination': win_and_nomination,
            'url': url,
        }        