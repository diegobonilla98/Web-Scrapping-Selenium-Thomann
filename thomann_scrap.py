from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import wget
from uuid import uuid4
from bs4 import BeautifulSoup
import requests
import os


DRIVER_PATH = "/home/bonilla/chromedriver"
wd = webdriver.Chrome(executable_path=DRIVER_PATH)
wd.implicitly_wait(2)

MAX_PAGES = 50
PAGE = 1
NUM_ARTICLES = 25
wd.get(f'https://www.thomann.de/intl/st_models.html?pg={PAGE}&ls={NUM_ARTICLES}')
WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-accept-all-cookies'))).click()

for pg in range(MAX_PAGES):
    for idx in range(NUM_ARTICLES):
        try:
            article = wd.find_elements_by_class_name("extensible-article")[idx]
            article.click()

            image = wd.find_elements_by_class_name("prod-media-bdb")[0]
            image.click()
            wd.find_element_by_class_name("prod-media-spot-container").click()
            main_image = wd.find_element_by_xpath("//div[@class='ZoomImageWrapper']/picture[@class='ZoomImagePicture']/img").get_attribute("src")

            product_name = wd.find_element_by_tag_name("h1").text
            product_description = wd.find_elements_by_tag_name("ul")[16].text

            wd.find_element_by_class_name("zgCloseHandler").click()

            resp = requests.get(wd.current_url)
            soup = BeautifulSoup(resp.text, 'lxml').prettify()
            idx = soup.find('}},"artnr":"')
            product_id = soup[idx + 12: idx + 100].split(',')[0][:-1]

            name = str(uuid4())
            os.makedirs(f'./results/audios/{name}')

            stuff = wd.find_elements_by_tag_name('li')
            for s in stuff:
                audio_id = s.get_attribute("data-audio-id")
                if audio_id is not None and audio_id.isnumeric():
                    audio_type = s.get_attribute("data-track-title")
                    wget.download(f'https://audio2.thomann.de/wav_audiot/{product_id}/{audio_id}_mp3-256.mp3?p=1x4p65p.mp3',
                                  out=f'./results/audios/{name}/{audio_type}.mp3')

            wget.download(main_image, out=f'./results/images/{name}.jpg')
            with open(f'./results/metadata/{name}.txt', 'w') as file:
                file.write(wd.current_url)
                file.write('\n')
                file.write(product_name)
                file.write('\n')
                file.write(product_description)

            wd.back()
        except Exception:
            print("fuc")
            continue

    wd.find_element_by_class_name('rs-btn-secondary').click()

wd.close()
