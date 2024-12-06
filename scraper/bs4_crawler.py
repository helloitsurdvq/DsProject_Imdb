from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time
import requests
import random

chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")  # Set window size

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get("https://www.imdb.com/search/title/?title_type=feature&user_rating=1,10&languages=en&count=250")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

movies_data = []
movie_links = []

# Try to find the '50 more' button and click it if available
while True:
    try:
        btn_more = driver.find_element(By.CSS_SELECTOR, ".ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--on-accent2.ipc-btn--rounded.ipc-text-button.ipc-see-more__button")
        driver.execute_script('arguments[0].click()', btn_more)
        time.sleep(2)
    except:
        break  

movie_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-188eab07-2 dWinDP dli-title')]/a[contains(@class, 'ipc-title-link-wrapper')]")
movie_links.extend([movie.get_attribute("href") for movie in movie_elements])
print(movie_links)

# Close the Selenium browser
driver.quit()

popular_genres = {
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", 
    "Drama", "Family", "Fantasy", "Film Noir", "Game Show", "History", "Horror", 
    "Music", "Musical", "Mystery", "News", "Reality TV", "Romance", "Sci-Fi", 
    "Short", "Sport", "Talk Show", "Thriller", "War", "Western"
}

def get_movie_details(link, retries=5, backoff_factor=1):
    """Scrapes the details from the movie page and adds them to the movies_data list."""
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.find('h1', {'data-testid': 'hero__pageTitle'}).find('span').get_text(strip=True)
            
            img_url = soup.find('meta', property='og:image')['content']
            
            year = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt').find_all('li')[0].a.text
        
            director = soup.find('a', class_='ipc-metadata-list-item__list-content-item--link').text
            
            li_tags = soup.find_all('li', class_='ipc-metadata-list__item ipc-metadata-list-item--link')
            for li in li_tags:
                stars_link = li.find('a')
                if stars_link and stars_link.text == "Stars":
                    stars_container = li.find('div', class_='ipc-metadata-list-item__content-container')
                    if stars_container:
                        stars_list = stars_container.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
                        stars = [star.text for star in stars_list]
            
            duration_tag = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt').find_all('li', class_='ipc-inline-list__item')
            # Check if the list has at least 2 elements, then try index 2 or fallback to index 1
            if len(duration_tag) > 2:
                duration = duration_tag[2].text
            elif len(duration_tag) > 1 and len(duration_tag) < 3:
                duration = duration_tag[1].text
            else:
                duration = "N/A"
            
            genre_tags = soup.find_all('a', class_='ipc-chip ipc-chip--on-baseAlt')
            genres_all = [tag.find('span', class_='ipc-chip__text').text for tag in genre_tags]
            genres = [genre for genre in genres_all if genre in popular_genres]
            
            overview = soup.find('span', {'data-testid': 'plot-xl'}).text
            
            rating = soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'}).span.text or 0.0
            
            num_rating = soup.find('div', class_='sc-d541859f-3 dwhNqC').text or 0
            
            metascore = "N/A"
            num_user_review = 0
            num_critic_review = 0
            review_sections = soup.find_all('span', class_=lambda c: c and 'three-Elements' in c)
            # Loop through the sections to find the Critic reviews only
            for section in review_sections:
                label = section.find('span', class_='label').text
                if "User reviews" in label:
                    num_user_review_tag = section.find('span', class_='score')
                    num_user_review = num_user_review_tag.text if num_user_review_tag else 0
                elif "Critic reviews" in label:
                    num_critic_review_tag = section.find('span', class_='score')
                    num_critic_review = num_critic_review_tag.text if num_critic_review_tag else 0
                elif "Metascore" in label:
                    metascore_tag = section.find('span', class_='score')
                    metascore = metascore_tag.text if metascore_tag else "N/A"
            
            budget_tag = soup.find('li', {'data-testid': 'title-boxoffice-budget'})
            if budget_tag:
                budget = soup.find('li', {'data-testid': 'title-boxoffice-budget'}).find('div').find('ul').find('li').find('span').text or "N/A"
            else:
                budget = 'N/A'
            
            gross_tag = soup.find('li', {'data-testid': 'title-boxoffice-cumulativeworldwidegross'})
            if gross_tag:
                gross = soup.find('li', {'data-testid': 'title-boxoffice-cumulativeworldwidegross'}).find('div').find('ul').find('li').find('span').text or "N/A"
            else:
                gross = 'N/A'
                
            country = soup.find('li', {'data-testid': 'title-details-origin'}).find('a').text
            
            text_win_oscar = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base')
            if text_win_oscar:
                oscar_text = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base').find('li').find('a').text or "None"
                oscar = 'N/A' if oscar_text == 'Awards' else oscar_text
                win_and_nomination = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base').find('li').find('div').find('ul').find('li').find('span').text or "N/A"
            else:
                oscar = 'N/A'
                win_and_nomination = 'N/A'
                
            url = link

            movies_data.append({
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
            })
            
            return

        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt < retries:
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                print(f"Error scraping movie details from {link}, retrying in {sleep_time:.2f} seconds... (Attempt {attempt}/{retries})")
                time.sleep(sleep_time)
            else:
                print(f"Error scraping movie details from {link}: {e}")
                break

# Scrape the movie details for each link in movie_links using BeautifulSoup
for link in movie_links:
    get_movie_details(link)
    print(link)
    time.sleep(5)

# Save the movie details to a CSV file
with open('movies_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=[
        'title', 'img_url', 'year', 'director', 'stars', 'duration', 'genres', 
        'overview', 'rating', 'num_rating', 'num_user_review', 'num_critic_review', 
        'budget', 'gross', 'country', 'metascore', 'oscar', 'win_and_nomination', 'url'
    ])
    writer.writeheader()
    for movie in movies_data:
        movie['stars'] = ', '.join(movie['stars'])
        movie['genres'] = ', '.join(movie['genres'])
        writer.writerow(movie)

print("Movies data saved to 'movies_data.csv'.")