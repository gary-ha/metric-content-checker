from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from decouple import config
import datetime


class OddsportalScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"')
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options, executable_path=config('CHROMEDRIVER_PATH'))
        self.url = "https://www.oddsportal.com/login/"
        self.events = []
        self.today = datetime.datetime.now()
        self.tomorrow = self.today + datetime.timedelta(days=1)

    def load_selenium(self):
        print("Loading Selenium...")
        self.driver.get(self.url)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="login-username"]'))).send_keys(config('BETFAIR_USERNAME'))
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="login-password"]'))).send_keys(config('ODDSPORTAL_PASSWORD'))
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][name='login-submit']"))).click()
        time.sleep(3)

    def gather_my_matches(self, day):
        print('Scraping My Matches...')
        self.driver.get('https://www.oddsportal.com/matches/my-matches/')
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{day}']"))).click()
        time.sleep(3)
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "pagination")))
            pages = self.driver.find_element_by_id('pagination')
            a_links = pages.find_elements_by_tag_name('a')
            number_of_pages = int(a_links[len(a_links) - 1].get_attribute('x-page'))
        except TimeoutException:
            number_of_pages = 1
        for _ in range(number_of_pages):
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
            rows = self.driver.find_elements_by_tag_name('tr')
            for row in rows:
                try:
                    row.find_element_by_class_name('table-score')
                    continue
                except NoSuchElementException:
                    try:
                        self.scrape_match(row, day)
                    except (NoSuchElementException, IndexError):
                        continue
            self.turn_page()
            time.sleep(3)
        return self.events

    def scrape_match(self, row, day):
        ko_day = self.find_day(day)
        start_time = row.find_element_by_class_name('table-time').text
        if ":" in start_time:
            event_info = row.find_element_by_class_name("table-participant")
            event_links = event_info.find_elements_by_tag_name('a')
            if len(event_links) != 1:
                event_name = event_links[1].text.replace('-', 'vs.')
                competition = event_links[1].get_attribute('href').split('/')
                competition = f"{competition[4].capitalize()} - {competition[5].capitalize()}"
            else:
                event_name = event_links[0].text.replace('-', 'vs.')
                competition = event_links[0].get_attribute('href').split('/')
                competition = f"{competition[4].capitalize()} - {competition[5].capitalize()}"
            odds = row.find_elements_by_class_name('odds-nowrp')
            number_of_bookmakers = row.find_element_by_class_name('info-value').text
            self.events.append({
                'starttime': f"{ko_day} {start_time}",
                'event': event_name,
                'competition': competition,
                'homeodds': odds[0].text,
                'drawodds': odds[1].text,
                'awayodds': odds[2].text,
                'bookmakers': int(number_of_bookmakers),
            })

    def turn_page(self):
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "pagination")))
            pages = self.driver.find_element_by_id('pagination')
            a_links = pages.find_elements_by_tag_name('a')
            a_links[len(a_links) - 2].click()
        except TimeoutException:
            pass

    def scrape_all(self, day):
        print("Scraping all matches...")
        ko_day = self.find_day(day)
        self.driver.get('https://www.oddsportal.com/matches/')
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{day}']"))).click()
        time.sleep(3)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
        rows = self.driver.find_elements_by_tag_name('tr')
        for row in rows:
            try:
                row.find_element_by_class_name('table-score')
                continue
            except NoSuchElementException:
                try:
                    start_time = row.find_element_by_class_name('table-time').text
                    if ":" in start_time:
                        event_info = row.find_element_by_class_name("table-participant")
                        event_links = event_info.find_elements_by_tag_name('a')
                        if len(event_links) != 1:
                            event_name = event_links[1].text.replace('-', 'vs.')
                            competition = event_links[1].get_attribute('href').split('/')
                            competition = f"{competition[4].capitalize()} - {competition[5].capitalize()}"
                        else:
                            event_name = event_links[0].text.replace('-', 'vs.')
                            competition = event_links[0].get_attribute('href').split('/')
                            competition = f"{competition[4].capitalize()} - {competition[5].capitalize()}"
                        odds = row.find_elements_by_class_name('odds-nowrp')
                        number_of_bookmakers = row.find_element_by_class_name('info-value').text
                        self.events.append({
                            'starttime': f"{ko_day} {start_time}",
                            'event': event_name,
                            'competition': competition,
                            'homeodds': odds[0].text,
                            'drawodds': odds[1].text,
                            'awayodds': odds[2].text,
                            'bookmakers': int(number_of_bookmakers),
                        })
                except (NoSuchElementException, IndexError):
                    continue
        return self.events

    def find_day(self, day):
        if day == 'Today':
            ko_day = self.today.strftime('%Y-%m-%d')
        else:
            ko_day = self.tomorrow.strftime('%Y-%m-%d')
        return ko_day

    def quit_selenium(self):
        self.driver.close()
        self.driver.quit()
