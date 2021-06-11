from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
from decouple import config


class ContentCheck:
    def __init__(self):
        self.incorrect_odds = []
        self.heavy_favourites = []
        self.heavy_draws = []

    def compare_events(self, list_events, metric_events):
        print("Checking any missing events comparing Metric and Flashscores...")
        oddsportal_events = list_events
        for event in metric_events:
            choices = [oddsportal_event['event'] for oddsportal_event in oddsportal_events if
                       oddsportal_event['starttime'] == event['starttime']]
            try:
                best_choice = process.extractOne(event['event'], choices, scorer=fuzz.token_set_ratio)
                if best_choice[1] > 64:
                    self.calculate_odds(event, best_choice, oddsportal_events)
                    for i in range(len(oddsportal_events)):
                        if oddsportal_events[i]['event'] == best_choice[0]:
                            del oddsportal_events[i]
                            break
            except TypeError:
                continue
        missing_events = []
        for event in oddsportal_events:
            if int(event['bookmakers']) > 9:
                missing_events.append(event)
        return self.incorrect_odds, missing_events

    def calculate_odds(self, event, best_choice, oddsportal_events):
        for oddsportal_event in oddsportal_events:
            if oddsportal_event['event'] == best_choice[0]:
                home_prob = max(float(oddsportal_event['homeodds']), (float(event['homeodds'])))
                draw_prob = max(float(oddsportal_event['drawodds']), (float(event['drawodds'])))
                away_prob = max(float(oddsportal_event['awayodds']), (float(event['awayodds'])))
                if 1/home_prob + 1/draw_prob + 1/away_prob < 1:
                    add_competitior_odds = event
                    add_competitior_odds['homeodds-competitor'] = oddsportal_event['homeodds']
                    add_competitior_odds['drawodds-competitor'] = oddsportal_event['drawodds']
                    add_competitior_odds['awayodds-competitor'] = oddsportal_event['awayodds']
                    self.incorrect_odds.append(add_competitior_odds)

    def find_heavy_favourites(self, metric_events):
        for metric_event in metric_events:
            if float(metric_event['homeodds']) <= 1.10 or float(metric_event['awayodds']) <= 1.10:
                self.heavy_favourites.append(metric_event)
            if float(metric_event['drawodds']) <= 2.50:
                self.heavy_draws.append(metric_event)
        return self.heavy_favourites, self.heavy_draws

    def df_to_csv(self, missing_events):
        print("Saving missing events to CSV...")
        df = pd.DataFrame(missing_events)
        df.to_csv(config('CSV_FILE'), index=False)