from logic import ContentCheck
from metric_api import MetricAPI
from oddsportal_scraper import OddsportalScraper
from slack_api import SlackAPI

content_checker = ContentCheck()
metric_api = MetricAPI()
oddsportal = OddsportalScraper()
slack_api = SlackAPI()

oddsportal.load_selenium()
oddsportal.scrape_all('Today')
events = oddsportal.scrape_all('Tomorrow')
oddsportal.quit_selenium()
metric_events = metric_api.get_events()
incorrect_prices, missing_events = content_checker.compare_events(events, metric_events)
heavy_favourites, heavy_draws = content_checker.find_heavy_favourites(metric_events)
slack_api.send_incorrect_prices_message(incorrect_prices)
slack_api.send_heavy_favourites(heavy_favourites)
slack_api.send_heavy_draws(heavy_draws)
content_checker.df_to_csv(missing_events)
slack_api.send_csv()
