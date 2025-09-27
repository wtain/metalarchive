import datetime
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual long-lived access token
ACCESS_TOKEN = os.getenv("INSTAGRAM_TOKEN")

# url = f"https://graph.instagram.com/me"
# params = {
#     "fields": "id,username,account_type",
#     "access_token": ACCESS_TOKEN
# }
#
# resp = requests.get(url, params=params)
#
# if resp.status_code == 200:
#     print("✅ Instagram API working")
#     print(resp.json())
# else:
#     print("❌ Error:", resp.status_code, resp.text)


# id = resp.json.id

# Replace with your IG user id from previous call
IG_USER_ID = os.getenv('INSTAGRAM_USER_ID')

# {'error': {'message':
# 'metric[0] must be one of the following values:
# reach, follower_count, website_clicks, profile_views, online_followers, accounts_engaged, total_interactions, likes, comments, shares, saves, replies, engaged_audience_demographics, reached_audience_demographics, follower_demographics, follows_and_unfollows, profile_links_taps, views, threads_likes, threads_replies, reposts, quotes, threads_followers, threads_follower_demographics, content_views, threads_views, threads_clicks',
# 'type': 'IGApiException', 'code': 100, 'fbtrace_id': 'AuWHyE2YGMQi76RLDCtH30f'}}

# follower_count,threads_followers,online_followers,accounts_engaged,total_interactions,likes,comments,shares,saves,replies

ts1 = int(datetime.datetime(2025, 1, 1, 0, 0).timestamp())
ts2 = int(datetime.datetime(2025, 9, 26, 0, 0).timestamp())

url = f"https://graph.instagram.com/v20.0/{IG_USER_ID}/insights"
params = {
    "metric": "follower_count",
    "period": "day",
    "since": ts1,
    "until": ts2,
    "access_token": ACCESS_TOKEN
}

resp = requests.get(url, params=params)
json_str = resp.json()['data']
print(json_str)

for v in json_str:
    for c in v['values']:
        value = c['value']
        end_time = c['end_time']
        print(f"{end_time}: {value}")

# v = json.loads(json_str)[0]
# print(json_str)

