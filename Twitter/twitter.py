import os
import tweepy
import requests
import json


class Twitter:
    def __init__(self):
        try:
            f = open("./settings.json", "r")
        except FileNotFoundError:
            print("Please create settings.json")

        settings_json = f.read()
        f.close()
        settings = json.loads(settings_json)
        TWITTER_TOKEN = settings["twitter"]["TWITTER_TOKEN"]

        if TWITTER_TOKEN == "":
            TWITTER_TOKEN = os.environ['TWITTER_TOKEN']

        if TWITTER_TOKEN == "":
            print("Please set TWITTER_TOKEN")
            exit(1)
            
        self.client = tweepy.Client(TWITTER_TOKEN, return_type='json')

    def get_new_tweets_of_user(self, twitter_id):
        tweets = self.client.get_users_tweets(
            id=twitter_id,
            exclude=['retweets', 'replies'],
            expansions=['attachments.media_keys'],
            media_fields=['url', 'preview_image_url'],
            max_results=10
        )
        data = tweets.data
        if tweets.includes:
            media = tweets.includes['media']
        else:
            return ([], None)
        tweets_with_media = []
        true_urls = []
        for tweet in data:
            if tweet['attachments'] != None:
                tweets_with_media.append(tweet)
                true_urls.append(
                    "https://twitter.com/i/web/status/" + str(tweet['id']))
        return [tweets_with_media, media, true_urls]

    def url_to_id(self, username):
        header = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data_raw = "input=%40" + username + ""
        res = requests.post('https://tweeterid.com/ajax.php',
                            data=data_raw, headers=header)
        return res.text
