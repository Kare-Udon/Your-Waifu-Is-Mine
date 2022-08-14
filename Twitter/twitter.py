import os
import tweepy
import requests
import json
import sql.sqlite
from telegram import InputMediaPhoto

db = sql.sqlite.database()


class Twitter:
    def __init__(self):
        try:
            f = open("./data/settings.json", "r")
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

    def get_new_tweets_of_user(self, user_id):
        tweets = self.client.get_users_tweets(
            id=user_id,
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
        text = ''
        retries = 0
        while text != '':
            res = requests.post('https://tweeterid.com/ajax.php',
                                data=data_raw, headers=header)
            if retries >= 5:
                raise Exception('Convert twitter username to id failed. Too many tries!')
            if res.text != 'error':
                text = res.text
            else:
                retries += 1
                os.sleep(5)
        return text

    def get_twitter_update(self):
        twitter_infos = db.get_all_twitter_user_info()
        return_data = []    #
        for info in twitter_infos:
            name = info[0]
            user_id = info[1]
            tweets_data = Twitter.get_new_tweets_of_user(self, user_id)
            tweets_with_media = tweets_data[0]
            true_urls = []
            if tweets_with_media != []:
                medias = tweets_data[1]
                true_urls = tweets_data[2]

            image_counter = 0
            for tweet_with_media in tweets_with_media:
                if db.add_new_tweet(tweet_with_media['id'], user_id):
                    num_of_images = len(
                        tweet_with_media['attachments']['media_keys'])
                    twitter_url = "https://twitter.com/" + \
                        str(name) + "/status/" + str(tweet_with_media['id'])
                    return_text = (
                        f'#{name} #twitter\n'
                        f'<a href="{twitter_url}">URL</a>\n'
                        f'Text: {tweet_with_media["text"]}'
                    )

                    input_medias = []
                    for index in range(num_of_images):
                        if index == 0:
                            input_medias.append(InputMediaPhoto(
                                medias[index + image_counter]['url'], caption=return_text, parse_mode='HTML'))
                        else:
                            input_medias.append(
                                InputMediaPhoto(medias[index]['url']))
                        image_counter += 1
                    return_data.append(input_medias)
                else:
                    break

        db.shorten_twitter_db(user_id)
        return return_data
