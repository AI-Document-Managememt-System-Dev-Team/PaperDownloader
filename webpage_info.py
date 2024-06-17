import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

def extract_info(driver: webdriver) -> tuple[str, str, str, str]:
    abstract = ""
    keyword_links = []
    try:
        abstract = driver.find_element(By.CLASS_NAME, "abstract-text").text
    except exceptions.NoSuchElementException:
        print(f"无法获取 {driver.title} 的摘要。\n")
    try:
        keywords_element = driver.find_element(By.CLASS_NAME, "keywords")
        keyword_links = keywords_element.find_elements(By.TAG_NAME, "a")
    except exceptions.NoSuchElementException:
        print(f"无法获取 {driver.title} 的关键词。\n")
    title = driver.title[:-6]
    current_url = driver.current_url
    keywords = ""
    for link in keyword_links:
        keywords += link.text
    return title, abstract, keywords, current_url