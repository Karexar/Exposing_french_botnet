import tweepy
import os
import pandas as pd
import time
from concat_csv import *

# Authenticate to Twitter
auth = tweepy.OAuthHandler("",
    "")
auth.set_access_token("",
    "")
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


def fetch_timeline(author_id, since_id, max_id):
    '''
    Fetch all tweets from a given author user
    Be aware that the servers may be overloaded (error 503) and thus some
    timeline may be missing for this reason.
    Arguments :
     - user_id : the user id
     - since_id : a tweet id which creation date is close to the starting date
       from where we want to fetch tweets. This works because tweet_id increase
       with time.
     - max_id : a tweet id which creation date is close to the last date from
       where we want to fetch tweets.
    '''
    tweets = []
    #By default, include replies and retweets, in those cases the user is the
    # one who replies or retweet.
    try:
        for tweet in tweepy.Cursor(api.user_timeline,user_id=author_id,
                                                     since_id=since_id,
                                                     max_id=max_id).items():
            tweets.append(tweet)
    except tweepy.TweepError:
        print("TweepError with author_id " + str(author_id))
        pass
    return tweets

def df_from_fetched(tweets):
    '''
    Takes a list of tweets, create a dataframe from it, and return it
     - tweets : a list of tweets as return by the fetch_timeline() function
    '''
    rows = []
    for tweet in tweets:
        row = [tweet.id,
               tweet.created_at,
               tweet.user.id,
               tweet.text,
               tweet.entities,
               tweet.source_url,
               tweet.in_reply_to_user_id,
               tweet.in_reply_to_status_id,
               tweet.retweet_count,
               tweet.is_quote_status,
               tweet.user.screen_name,
               tweet.user.followers_count,
               tweet.user.friends_count,
               tweet.user.created_at,
               tweet.user.favourites_count]
        rows.append(row)
    new_df = pd.DataFrame(rows, columns=["tweet_id",
                                         "created_at",
                                         "author_id",
                                         "text",
                                         "entities",
                                         "source_url",
                                         "in_reply_to_user_id",
                                         "in_reply_to_status_id",
                                         "retweet_count",
                                         "is_quote_status",
                                         "user_screen_name",
                                         "user_follower_count",
                                         "user_friend_count",
                                         "user_created_at",
                                         "user_favourites_count"])

    return new_df


def fetch_timelines(author_ids, since_id, max_id, out_dir):
    '''
    Fetch all tweets for user whose timeline is not available
    Arguments :
     - author_ids : a list of author ids whose timeline is already available
     - since_id : a tweet id which creation date is close to the starting date
       from where we want to fetch tweets. This works because tweet_id increase
       with time.
     - max_id : a tweet id which creation date is close to the last date from
       where we want to fetch tweets.
     - out_dir : a directory path where to store the csv of the fetched timelines
    '''
    base_time = time.time()
    idx_out = 0
    new_authors_df = pd.DataFrame()
    for author_id in author_ids:
        tweets = fetch_timeline(author_id, since_id, max_id)
        new_df = df_from_fetched(tweets)
        new_authors_df = pd.concat([new_authors_df, new_df])
        if time.time() > base_time + 300:
            if new_authors_df.shape[0] > 0:
                new_authors_df.to_csv(os.path.join(out_dir, "new_authors_" + str(idx_out) + ".csv"),
                                      index=False,
                                      encoding='utf-8')

                print("saved until author id " + str(author_id))
                new_authors_df = pd.DataFrame()
                idx_out += 1
    if new_authors_df.shape[0] > 0:
        new_authors_df.to_csv(os.path.join(out_dir, "new_authors_" + str(idx_out) + ".csv"),
                              index=False,
                              encoding='utf-8')

    # Concatenate the partial results
    concat_csv(out_dir, "new_authors_", os.path.join(out_dir, "new_authors.csv"))
