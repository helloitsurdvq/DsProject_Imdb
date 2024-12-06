from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time

chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")  # Set window size
chrome_options.add_argument("--memory-model-cache-size-mb=512")

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.delete_all_cookies()
driver.get("https://www.imdb.com/search/title/?title_type=feature&user_rating=1,10&count=250")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

movies_data = []
movie_links = []

# Try to find the expanding button and click it if available
while True:
    try:
        btn_more = driver.find_element(By.CSS_SELECTOR, ".ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--button-radius.ipc-btn--on-accent2.ipc-text-button.ipc-see-more__button")
        driver.execute_script('arguments[0].click()', btn_more)
        time.sleep(3)
    except:
        break  

movie_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-a69a4297-2 bqNXEn dli-title with-margin')]/a[contains(@class, 'ipc-title-link-wrapper')]")
movie_links.extend([movie.get_attribute("href") for movie in movie_elements])

driver.quit()

with open('movies_url_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['url'])
    writer.writeheader()
    for link in movie_links:
        writer.writerow({'url': link})

print("Movies-url data is saved to 'movies_url_data.csv'.")