from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


options = FirefoxOptions()
# options.add_argument("--headless")
options.set_preference('permissions.default.stylesheet', 2)
options.set_preference('permissions.default.image', 2)
options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

driver = webdriver.Firefox(options=options, executable_path='./gecko/geckodriver')

# url = 'https://auburn.craigslist.org/bop/d/auburn-cyclingdeal-tailgate-bike-pads/7433657736.html'

def get_email(url):
    driver.get(url)
    reply = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/section/section/header/div[2]/div/button'))
        )
    driver.find_element(By.XPATH, '/html/body/section/section/header/div[2]/div/button').click()
    try:
        reply_ = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/section/section/header/div[2]/div/div[1]/aside/ul/button'))
            )
        driver.find_element(By.XPATH, '/html/body/section/section/header/div[2]/div/div[1]/aside/ul/button').click()
        reply__ = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/section/section/header/div[2]/div/div[1]/aside/ul/li[3]/input'))
            )
        html = driver.page_source
        soup = BeautifulSoup(html)
        mail = soup.find(class_='anonemail').get('value')
    except:
        reply_ = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/section/section/header/div[2]/div/div[1]/aside/ul/li/button'))
            )
        driver.find_element(By.XPATH, '/html/body/section/section/header/div[2]/div/div[1]/aside/ul/button').click()
        reply__ = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="reply-tel-number"]'))
            )
        html = driver.page_source
        soup = BeautifulSoup(html)
        mail = soup.find(id='reply-tel-number').text
    return mail