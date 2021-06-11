import requests
from decouple import config
import datetime


class MetricAPI:
    def __init__(self):
        self.url = config('BO_URL')

    def get_events(self):
        print("Retrieving events from Metric...")
        metric_events = []
        dates = ['today', 'tomorrow']
        for date in dates:
            parameters = {
                'fn': 'getavbsportsupcoming',
                'sport': 'Soccer',
                'marketType': 'MatchWinner',
                'lang': 'en',
                'org': 'snabbis',
                'ix': 0,
                'when': date,
                'timezone': 0,
                'numberOfEvents': 1000
            }

            response = requests.get(url=self.url, params=parameters)
            response.raise_for_status()
            events_data = response.json()

            for event in events_data['data']['events']:
                if event['status'] == "Live":
                    ko_time_object = datetime.datetime.strptime(event["startTime"], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=1)
                    match_winner = event['markets'][0]['selections']
                    metric_events.append({
                        'eventid': event['eventId'],
                        'starttime': ko_time_object.strftime("%Y-%m-%d %H:%M"),
                        'event': event['name'],
                        'competition': event['categoryName'],
                        'homeodds': match_winner[0]['odds'],
                        'drawodds': match_winner[2]['odds'],
                        'awayodds': match_winner[1]['odds'],
                    })
        return metric_events
