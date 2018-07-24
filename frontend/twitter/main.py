import twitter
import json
import time


with open("twitter_auth.json") as f:
    twitter_auth = json.loads(f.read())
    consumer_key = twitter_auth["consumer_key"]
    consumer_secret = twitter_auth["consumer_secret"]
    access_token_key = twitter_auth["access_token_key"]
    access_token_secret = twitter_auth["access_token_secret"]

api = twitter.Api(consumer_key = consumer_key,
                  consumer_secret = consumer_secret,
                  access_token_key  = access_token_key,
                  access_token_secret = access_token_secret)

api.VerifyCredentials()
tweets = api.GetUserTimeline(screen_name='aaroadwatch', count=10,)

now = str(time.strftime("%a"))
dublin_tweets = []
i=0
for t in tweets:
    if t.text.startswith("#DUBLIN") and t.created_at.startswith(now):
        dublin_tweets.append(t.text)
    i += 1
