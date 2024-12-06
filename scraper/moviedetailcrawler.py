from bs4 import BeautifulSoup
import requests

url = 'https://www.imdb.com/title/tt0460791/?ref_=sr_t_228'

# Set up a header to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Accept-Language': 'en-US,en;q=0.9'
}

valid_genres = {
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", 
    "Drama", "Family", "Fantasy", "Film Noir", "Game Show", "History", "Horror", 
    "Music", "Musical", "Mystery", "News", "Reality TV", "Romance", "Sci-Fi", 
    "Short", "Sport", "Talk Show", "Thriller", "War", "Western"
}

# Send a request to the URL with headers
response = requests.get(url, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the h1 tag
aaa = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt').find_all('li')[0].a.text

duration_list = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt').find_all('li', class_='ipc-inline-list__item')
        # Check if the list has at least 2 elements, then try index 2 or fallback to index 1
if len(duration_list) > 2:
    duration = duration_list[2].text
elif len(duration_list) > 1 and len(duration_list) < 3:
    duration = duration_list[1].text
else:
    duration = "N/A"

li_tags = soup.find_all('li', class_='ipc-metadata-list__item ipc-metadata-list-item--link')
for li in li_tags:
    stars_link = li.find('a')
    if stars_link and stars_link.text == "Stars":
        stars_container = li.find('div', class_='ipc-metadata-list-item__content-container')
        if stars_container:
            stars_list = stars_container.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            stars = [star.text for star in stars_list]
                    
text_win_oscar = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base')
if text_win_oscar:
            oscar_text = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base').find('li').find('a').text or "None"
            oscar = 'N/A' if oscar_text == 'Awards' else oscar_text
            win_and_nomination = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-none sc-aa5ab255-2 fiMdao ipc-metadata-list--base').find('li').find('div').find('ul').find('li').find('span').text or "N/A"
else:
            oscar = 'N/A'
            win_and_nomination = 'N/A'

metascore = "N/A"
num_user_review = 0
num_critic_review = 0
review_sections = soup.find_all('span', class_=lambda c: c and 'three-Elements' in c)
for section in review_sections:
    label = section.find('span', class_='label').text
    if "User reviews" in label:
        num_user_review_tag = section.find('span', class_='score')
        num_user_review = num_user_review_tag.text if num_user_review_tag else 0
        print(num_user_review)
    elif "Critic reviews" in label:
        num_critic_review_tag = section.find('span', class_='score')
        num_critic_review = num_critic_review_tag.text if num_critic_review_tag else 0
        print(num_critic_review)
    elif "Metascore" in label:
        metascore_tag = section.find('span', class_='score')
        metascore = metascore_tag.text if metascore_tag else "N/A"
        print(metascore)
                
genre_tags = soup.find_all('a', class_='ipc-chip ipc-chip--on-baseAlt')
genres_all = [tag.find('span', class_='ipc-chip__text').text for tag in genre_tags]
genres = [genre for genre in genres_all if genre in valid_genres]

# print("Movie Title:", oscar, win_and_nomination)
print('stars: ', stars)
print('text: ', aaa)
# print('genres: ', genres)
# print(review_sections)
print('duration: ', duration)