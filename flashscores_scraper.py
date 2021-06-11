from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
from decouple import config
import traceback


class FlashscoresScraper:

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"')
        # self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options, executable_path=config('CHROMEDRIVER_PATH'))
        self.url = "https://www.flashscore.com/"
        self.ALL_EVENTS = "div[title='Click for match detail!']"

    def flashscores_scraper(self):
        try:
            print("Scraping events from Flashscores...")
            self.driver.get(self.url)
            element = self.driver.find_element_by_css_selector('div[class*="otPlaceholder"]')
            self.driver.execute_script("arguments[0].click();", element)
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signIn"]'))).click()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='email']"))).send_keys(config('FLASHSCORES_USERNAME'))
            self.driver.find_element_by_xpath('//*[@id="passwd"]').send_keys(config('FLASHSCORES_PASSWORD'))
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]'))).click()
            time.sleep(10)
            list_events = []
            today_events = self.driver.find_elements_by_css_selector(self.ALL_EVENTS)
            self.scrape_event_information(today_events, list_events)
            # elements = self.driver.find_elements_by_css_selector('[class*="boxOverContent"]')
            # for element in elements:
            #     self.driver.execute_script("arguments[0].style.visibility='hidden'", element)
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "calendar__direction--tomorrow"))).click()
            # time.sleep(10)
            # tomorrow_events = self.driver.find_elements_by_css_selector(self.ALL_EVENTS)
            # self.scrape_event_information(tomorrow_events, list_events)
            self.driver.close()
            return list_events

        except Exception:
            self.driver.quit()
            print(traceback.format_exc())

    def scrape_event_information(self, events, list_events):
        for event in events:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'event__time')))
                if ":" in event.find_element_by_class_name('event__time').text and "FRO" not in event.find_element_by_class_name('event__time').text:
                    window_before = self.driver.window_handles[0]
                    event_details = f'{event.find_element_by_class_name("event__participant--home").text} vs. {event.find_element_by_class_name("event__participant--away").text}'
                    WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ALL_EVENTS)))
                    event.click()
                    window_after = self.driver.window_handles[1]
                    self.driver.switch_to.window(window_after)
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "country___24Qe-aj")))
                    competition = self.driver.find_element_by_class_name('country___24Qe-aj').text.split(" - ")[0]
                    start_time = self.driver.find_element_by_class_name('startTime___2oy0czV').text
                    home_odds = ""
                    draw_odds = ""
                    away_odds = ""
                    try:
                        WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "oddsValue___1euLZeq")))
                        if len(self.driver.find_elements_by_class_name('oddsValue___1euLZeq')) == 3:
                            home_odds = self.driver.find_elements_by_class_name('oddsValue___1euLZeq')[0].text
                            draw_odds = self.driver.find_elements_by_class_name('oddsValue___1euLZeq')[1].text
                            away_odds = self.driver.find_elements_by_class_name('oddsValue___1euLZeq')[2].text
                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                        pass
                    list_events.append({
                        'starttime': start_time,
                        'event': event_details,
                        'competition': f"{competition}",
                        'homeodds': home_odds,
                        'drawodds': draw_odds,
                        'awayodds': away_odds,
                    })
                    self.driver.close()
                    self.driver.switch_to.window(window_before)
            except (NoSuchElementException, TimeoutException):
                continue

