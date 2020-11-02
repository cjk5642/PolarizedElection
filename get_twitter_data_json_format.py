# -*- coding: utf-8 -*-

from tweepy import OAuthHandler
import json
import tweepy


output_filename = 'election_filter_10-26_10-29.jsonl'

t = 0
def scrape_tweets(search_words, date_since, date_until, num_tweets = 5000000):
    ''' Scrapes tweets until the date_since date is reached or num_tweets is reached '''
    
    creds = {'CONSUMER_KEY': "XtMJv3wN6AJqhuwYtIYJavPOP", 
              'CONSUMER_SECRET': "4hnEulpJqAlwIwXMceXUVPzvvtIoT69fUohgMGLDKZVZHizYi3",
              'ACCESS_TOKEN': "1052244514931449856-GTAHiINDlbVhKePOeomjXkh8DNPnAm", 
              'ACCESS_SECRET': "sJQzyOgyMJktuCog5ylCKPiVrsHqkbU3g34BSRYpG1P7i"}
    
    auth = OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
 
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    # Collect tweets using the Cursor object
    tweets = tweepy.Cursor(api.search, q=search_words, lang="en", since=date_since, until=date_until, tweet_mode='extended').items()
    
    count = 0
    for tweet in tweets:
        count += 1
        dict_to_append = {}
        dict_to_append['username'] = tweet.user.screen_name
        dict_to_append['acct_desc'] = tweet.user.description
        dict_to_append['location'] = tweet.user.location
        dict_to_append['following'] = tweet.user.friends_count
        dict_to_append['followers'] = tweet.user.followers_count
        dict_to_append['user_total_tweets'] = tweet.user.statuses_count
        dict_to_append['user_created_ts'] = str(tweet.user.created_at)
        dict_to_append['tweet_created_ts'] = str(tweet.created_at)
        dict_to_append['retweet_count'] = tweet.retweet_count
        dict_to_append['hashtags'] = tweet.entities['hashtags']
        dict_to_append['text'] = tweet.full_text
        dict_to_append['favorite_count'] = tweet.favorite_count
        
        if count % 10 == 0: print(f"Tweet #{count}\tDate: {dict_to_append['tweet_created_ts']}")
        
        with open(output_filename, "a") as outfile:  
            json.dump(dict_to_append, outfile) 
            outfile.write('\n')
        
        if count > num_tweets: break
    
election2020_filter = "#trump OR #biden OR #election OR #election2020 -filter:retweets"
date_since = "2020-10-26"
date_until = "2020-10-29"
scrape_tweets(election2020_filter, date_since, date_until)