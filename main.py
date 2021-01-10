import csv

import requests
import numpy as np
import pandas as pd
from datetime import datetime

eps = np.finfo(float).eps
from numpy import log2 as log

URL = "https://store.steampowered.com/appreviews/"
APPID = "1151640"

PARAMS = {'json': 1, "cursor": "*"}


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

def generate_data(appid):
    index = 0
    reviews = []
    query_summary = None
    while index < 1000:
        r = requests.get(url=URL + appid, params=PARAMS)
        data = r.json()
        if query_summary is None:
            query_summary = data['query_summary']
        reviews += data['reviews']
        index += data['query_summary']['num_reviews']
        PARAMS['cursor'] = data['cursor']
        print("INDEX " + str(index))
    fields = ['recommendationid', 'author_steamid', 'author_num_games_owned', 'author_num_reviews',
              'author_playtime_forever', 'author_playtime_last_two_weeks', 'author_playtime_at_review',
              'author_last_played', 'language', 'review', 'timestamp_created', 'timestamp_updated', 'voted_up',
              'votes_up', 'votes_funny', 'weighted_vote_score', 'comment_count', 'steam_purchase', 'received_for_free',
              'written_during_early_access', 'developer_response', 'timestamp_dev_responded']
    summary_fields = ['num_reviews', 'review_score', 'review_score_desc', 'total_positive', 'total_negative', 'total_reviews']
    query_summary['num_reviews'] = index
    with open('summary' + appid + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerow(query_summary)
    with open('review' + appid + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for entry in reviews:
            try:
                writer.writerow(dict_flatten(entry))
            except UnicodeEncodeError:
                pass
    print(reviews)

def open_data(appid):
    reviews = []
    summary = None
    with open('review' + appid + '.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            reviews.append(parse_row(row))
    with open('summary' + appid + '.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            summary = row
    return reviews, summary

if __name__ == "__main__":
    # generate_data(APPID)
    reviews, summary = open_data(APPID)
    print(summary)
