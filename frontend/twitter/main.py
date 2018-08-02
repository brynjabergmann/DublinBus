import twitter
import json
import time
import re
import pprint
import numpy as np


def banner_tweets():

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
    tweets = api.GetUserTimeline(screen_name='aaroadwatch', count=15,)

    now = str(time.strftime("%a"))
    dublin_tweets = []
    i=0
    for t in tweets:
        m = re.search('(?:)(cleared)(?:)', t.text)
        if m:
            pass
        elif t.text.startswith("#DUBLIN") and t.created_at.startswith(now):
            dublin_tweets.append(t.text)
        else:
            pass
        i += 1
    return dublin_tweets




def banner_tweets_regex():

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
    tweets = api.GetUserTimeline(screen_name='aaroadwatch', count=150,)

    now = str(time.strftime("%a"))
    dublin_tweets_raw = []
    dublin_tweets_lower = []
    fixed_traffic = []
    i=0
    current_day = str(time.strftime("%a"))

    for t in tweets:
        fixed_traffic_details = []
        m = re.search('(?:)(((C|c)leared)|((n|N)(o|O) (F|f)urther)|((R|r)eopened)|((M|m)oved)|working)(?:)', t.text)

        if m and t.text.startswith("#DUBLIN") and t.created_at.startswith(current_day):
            reg = re.search(r'(?:\bon the\b\s|\bon\b\s|from\s|in\s)(.*)\. More|\.', t.text)
            if reg:
                # Issues with regex for certain string slices
                # using str.replace() fixed this for the most part but will have to monitor
                reg_group = reg.group(1).replace("on ","")
                reg_group = reg_group.replace(".","")
                fixed_traffic_details.append(reg_group)
                fixed_traffic_details.append(t.text)
                fixed_traffic.append(fixed_traffic_details)
        elif t.text.startswith("#DUBLIN") and t.created_at.startswith(current_day):
            dublin_tweets_lower.append(t.text.lower())
            dublin_tweets_raw.append(t.text)
        else:
            pass
        i += 1
    roads = []
    m_roads = []
    n_roads = []
    m_test = []
    for i in range(len(dublin_tweets_raw)):
        m_details = []
        n_details = []
        roads_details = []
        n_regex = re.search(r'\bon the\b|\bon\b ((N\d+|N\d+\/M\d+)(?:.*)(J\d+)*)', dublin_tweets_raw[i])
        m_regex = re.search(
            r'\bon the\b\s|\bon\b\s((N\d+|M50)\s+(northbound|southbound|at|.*)(?:\.|\s+|\s+at\s+|.*)(J\d+)*)\.\s+More|\.',
            dublin_tweets_raw[i])
        roads_regex = re.search(r'(?:\bon the\b\s|\bon\b\s)(.*)\. More|\.', dublin_tweets_raw[i])
        test = "#DUBLIN Incident on M50 at J6. More here: https://t.co/PSzIBsvOzE"


        if n_regex and n_regex.group(1):
            n_roads.append(n_regex.group(0))
            # n_regex.group()
            # 1 = whole matched statement
            # 2 = road name
            # 4 = junction

            n_details.append(m_regex.group(2))
            n_details.append(m_regex.group(4))
            n_details.append(m_regex.group(1))
            n_details.append(dublin_tweets_raw[i])
            n_roads.append(n_details)

        elif m_regex.group(1): 
            # m_regex.group()
            # 1 = whole matched statement e.g. M50 southbound at J6
            # 2 = road name e.g. M50
            # 3 = direction e.g southbound
            # 4 = junction

            m_details.append(m_regex.group(2))
            m_details.append(m_regex.group(3))
            m_details.append(m_regex.group(4))
            m_details.append(m_regex.group(1))
            m_details.append(dublin_tweets_raw[i])
            m_roads.append(m_details)

        elif roads_regex.group(1):
            roads_details.append(roads_regex.group(1))
            roads_details.append(dublin_tweets_raw[i])
            roads.append(roads_details)
        else:
            pass
    print(fixed_traffic[0][0])
    print(len(roads),len(fixed_traffic))

    deletion_list = [] # List to keep track of indexes to be removed from roads
    for i in range(len(roads)):
        for j in range(len(fixed_traffic)):
            if roads[i][0].lower() == fixed_traffic[j][0].lower():
                print("True", roads[i][0].lower(), fixed_traffic[j][0].lower())
                deletion_list.append(i)
            else:
                print("False", roads[i][0].lower(), fixed_traffic[j][0].lower())
    #roads.reverse() # Had to reverse roads to start from the end of the list
                            # This is to ensure the most recent tweet is displayed if there is an error in RegEx
    roads = [x for i, x in enumerate(roads) if i not in deletion_list]
    #print(len(roads))
    #print(roads)
    #print(len(roads))
    #pprint.pprint(dublin_tweets_raw)
    #pprint.pprint(fixed_traffic)
    #pprint.pprint(roads)
    #pprint.pprint(m_roads)
    #pprint.pprint(n_roads)
    #pprint.pprint(m_roads)
    return roads
# fixed tweets and roads > contained in then delete both

print(banner_tweets_regex())