import pandas as pd
import requests
from datetime import datetime

URL = "https://store.steampowered.com/appreviews/"
APPID = "1151640"

DATA_DIR = 'data'


def dict_flatten(entry):
    entry['author_steamid'] = entry['author']['steamid']
    entry['author_num_games_owned'] = entry['author']['num_games_owned']
    entry['author_num_reviews'] = entry['author']['num_reviews']
    entry['author_playtime_forever'] = entry['author']['playtime_forever']
    entry['author_playtime_last_two_weeks'] = entry['author']['playtime_last_two_weeks']
    entry['author_playtime_at_review'] = entry['author']['playtime_at_review']
    entry['author_last_played'] = entry['author']['last_played']
    entry['review'] = entry['review'].replace(",", " ")
    del entry['author']
    return entry


def parse_row(entry):
    entry['recommendationid'] = int(entry['recommendationid'])
    entry['author_steamid'] = int(entry['author_steamid'])
    entry['author_num_games_owned'] = int(entry['author_num_games_owned'])
    entry['author_num_reviews'] = int(entry['author_num_reviews'])
    entry['author_playtime_forever'] = int(entry['author_playtime_forever'])
    entry['author_playtime_last_two_weeks'] = int(entry['author_playtime_last_two_weeks'])
    entry['author_playtime_at_review'] = int(entry['author_playtime_at_review'])
    entry['author_last_played'] = int(entry['author_last_played'])
    entry['timestamp_created'] = datetime.utcfromtimestamp(int(entry['timestamp_created']))
    entry['timestamp_updated'] = datetime.utcfromtimestamp(int(entry['timestamp_updated']))
    entry['voted_up'] = bool(entry['voted_up'])
    entry['votes_up'] = int(entry['votes_up'])
    entry['votes_funny'] = int(entry['votes_funny'])
    entry['weighted_vote_score'] = float(entry['weighted_vote_score'])
    entry['comment_count'] = int(entry['comment_count'])
    entry['steam_purchase'] = bool(entry['steam_purchase'])
    entry['received_for_free'] = bool(entry['received_for_free'])
    entry['written_during_early_access'] = bool(entry['written_during_early_access'])
    return entry


def generate_data(appid, size, data_path, review_type: str = 'all'):
    index = 0
    reviews = []
    query_summary = None
    cursor = '*'
    while index < size:
        r = requests.get(url=URL + appid, params={
            'json': 1,
            'cursor': cursor,
            'review_type': review_type,
        })
        data = r.json()
        if query_summary is None:
            query_summary = data['query_summary']
        reviews += data['reviews']
        index += data['query_summary']['num_reviews']

        print("index " + str(index))
        cursor = data['cursor']

    query_summary['num_reviews'] = index

    pd.DataFrame(query_summary, index=[0]).to_csv(
        '%s/summary_%s.csv' % (data_path, appid)
    )
    reviews = pd.DataFrame.from_records(
        [dict_flatten(review) for review in reviews]
    )
    reviews.to_csv('%s/review_%s_%s.csv' % (data_path, appid, review_type))


if __name__ == "__main__":
    generate_data(APPID, 100, DATA_DIR, 'positive')
    generate_data(APPID, 100, DATA_DIR, 'negative')
