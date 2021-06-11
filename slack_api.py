from decouple import config
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime


class SlackAPI:
    def __init__(self):
        self.client = WebClient(token=config('SLACK_BOT_TOKEN'))
        self.slack_channel = config('SLACK_CHANNEL')

    def send_incorrect_prices_message(self, incorrect_prices):
        print('Sending events to Slack...')
        events = []
        for event in incorrect_prices:
            events.append(f"*Please Check Match Winner Prices*\nKO {event['starttime']} - {event['event']} - {event['competition']} - {event['eventid']}\nMetric - H: {event['homeodds']}, X: {event['drawodds']}, A: {event['awayodds']}\nOddsportal - H: {event['homeodds-competitor']}, X: {event['drawodds-competitor']}, A: {event['awayodds-competitor']}")
        for event in events:
            try:
                self.client.chat_postMessage(channel=self.slack_channel, text=event)
            except SlackApiError as e:
                print(f"Got an error: {e.response['error']}")

    def send_heavy_favourites(self, heavy_favourites):
        events = []
        for event in heavy_favourites:
            events.append(f"*Please Check Heavily One-Sided Game*\nKO {event['starttime']} - {event['event']} - {event['competition']} - {event['eventid']}\nMetric - H: {event['homeodds']}, X: {event['drawodds']}, A: {event['awayodds']}")
        for event in events:
            try:
                self.client.chat_postMessage(channel=self.slack_channel, text=event)
            except SlackApiError as e:
                print(f"Got an error: {e.response['error']}")

    def send_heavy_draws(self, heavy_draws):
        events = []
        for event in heavy_draws:
            events.append(
                f"*Please Check Heavily Draw Sided Game*\nKO {event['starttime']} - {event['event']} - {event['competition']} - {event['eventid']}\nMetric - H: {event['homeodds']}, X: {event['drawodds']}, A: {event['awayodds']}")
        for event in events:
            try:
                self.client.chat_postMessage(channel=self.slack_channel, text=event)
            except SlackApiError as e:
                print(f"Got an error: {e.response['error']}")

    def send_csv(self):
        try:
            today = datetime.datetime.now()
            self.client.files_upload(
                channels=self.slack_channel,
                file=config('CSV_FILE'),
                title=f"{today.strftime('%d/%m/%y')} - Missing Events",
                initial_comment=f"*{today.strftime('%d/%m/%y')} - Missing Events*",
            )
            print('Sent CSV to Slack')
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")
