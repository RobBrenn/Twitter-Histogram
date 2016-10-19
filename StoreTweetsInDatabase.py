# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 10:08:04 2015

@author: Confero
"""

import configparser
import time
from twython import Twython, TwythonError
from pymongo import MongoClient

print("Retrieving settings")
config = configparser.ConfigParser()
config.read('settings.cfg')

#Get the keys from the settings file
APP_KEY    = config.get('keys','APP_KEY')
APP_SECRET = config.get('keys','APP_SECRET')

#Authenticate with twitter
print("Authenticating with twitter")
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()    
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

#Start the database
print("Starting database")
client = MongoClient()

username = config.get('database', 'username')
DBNAME = config.get('database', 'name')
#COLLECTION = config.get('database', 'user_collection')
db = client[DBNAME]
user_tweets = db[(username + "_timeline4")]

num_tweets_in_db = user_tweets.count()  

def  get_rate_limit():
    print("Getting rate limit")
    
    try:
        status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
    except:
        print("error getting status")
        
    user_status = status['resources']['statuses']['/statuses/user_timeline']
    print("Rate limit left: " + str(user_status['remaining']))
    return user_status['remaining']

def store_tweets(tweets, collection):
    try:
        #I might want to process the tweets as I store them.
        collection.insert(tweets)
    except:
        print("Error storing tweets")

def get_tweets(**get_tweet_params):
    try:
            if get_rate_limit() > 0:
                print(get_tweet_params)
                new_tweets = twitter.get_user_timeline(**get_tweet_params)
                print(new_tweets[0]['id'])
                print(new_tweets[-1]['id'])
                store_tweets(new_tweets, user_tweets)
                
                return new_tweets
            else:
                print("Rate limit met: Sleeping 2 min")
                time.sleep(60*2)
    except:
        print("Error getting tweets")

def get_new_tweets(**get_tweet_params):
    print("Getting newer tweets")
    try:
        new_tweets = { 1 }
        while len(new_tweets) > 0:
            new_tweets = get_tweets(**get_tweet_params)
            
            newest_tweet = new_tweets[0]['id']
            get_tweet_params['since_id'] = newest_tweet
        print("Getting newer tweets")
    except:
        print("Error getting new tweets")

def get_old_tweets(**get_tweet_params):
    print("Getting older tweets")
    try:
        old_tweets = { 1 }
        while len(old_tweets) > 0:
            old_tweets = get_tweets(**get_tweet_params)
            
            oldest_tweet = old_tweets[-1]['id']
            get_tweet_params['max_id'] = oldest_tweet-1
        print("Got older tweets")
    except:
        print("Error getting old tweets")

#get_tweet_params = {'screen_name':username, 'count':200}

#Gets how many tweets are in the database
num_tweets_in_db = user_tweets.count()  
print("Tweets in database: ", num_tweets_in_db)

if num_tweets_in_db > 0:
    #Getting new tweets, or tweets not yet put into the database.
    print("Getting new tweets")
    oldest_tweet = user_tweets.find(limit=1, sort=[('id',1)])[0]['id']
    newest_tweet = user_tweets.find(limit=1, sort=[('id',-1)])[0]['id']
    
    get_old_tweets(screen_name = username, count = 200, max_id = oldest_tweet-1 )
    
    get_new_tweets(screen_name = username, count = 200, since_id = newest_tweet)
    
    print("Got new tweets")
else:
    #Getting tweets for the first time
    print("Getting tweets for the first time")
    new_tweets = get_tweets(screen_name = username, count = 200)
    
    newest_tweet = new_tweets[0]['id']
    print("Newest id:" , newest_tweet)
    oldest_tweet = new_tweets[-1]['id']
    print("Oldest id:" , oldest_tweet)
    

    get_old_tweets(screen_name = username, count = 200, max_id = oldest_tweet-1 )

    get_new_tweets(screen_name = username, count = 200, since_id = newest_tweet)
    
    print("Got tweets for the first time")
