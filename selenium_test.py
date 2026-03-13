# Selenium test for InstaSentry
# This script opens Chrome and loads Instagram

from selenium import webdriver
import time


def test_browser():
    driver = webdriver.Chrome()
    driver.get("https://www.instagram.com")

    print("Instagram loaded successfully.")

    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    test_browser()