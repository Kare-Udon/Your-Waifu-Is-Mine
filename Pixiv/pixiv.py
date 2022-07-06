import logging
import os
import json
from time import sleep

from telegram import InputMediaPhoto
import sql.sqlite
import asyncio
import requests
from aiohttp_requests import requests as aiorequests
from bs4 import BeautifulSoup

from pixivpy3 import AppPixivAPI

db = sql.sqlite.database()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename="./data/error.log",
                    level=logging.ERROR, format=LOG_FORMAT)

loop = asyncio.new_event_loop()

class Pixiv:
    api = AppPixivAPI()

    def __init__(self):
        try:
            f = open("./data/settings.json", "r")
        except FileNotFoundError:
            print("Please create settings.json")

        settings_json = f.read()
        f.close()
        settings = json.loads(settings_json)
        ACCESS_TOKEN = settings['pixiv']['ACCESS_TOKEN']
        REFRESH_TOKEN = settings['pixiv']['REFRESH_TOKEN']

        if ACCESS_TOKEN == "":
            ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
        if REFRESH_TOKEN == "":
            REFRESH_TOKEN = os.environ['REFRESH_TOKEN']

        if ACCESS_TOKEN == "" or REFRESH_TOKEN == "":
            print("Please set ACCESS_TOKEN and REFRESH_TOKEN")
            exit(1)

        Pixiv.api.set_auth(ACCESS_TOKEN, REFRESH_TOKEN)

        

    def refresh_token(self, refresh_token):
        USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
        AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
        CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
        CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
        response = requests.post(
            AUTH_TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "refresh_token",
                "include_policy": "true",
                "refresh_token": refresh_token,
            },
            headers={"User-Agent": USER_AGENT},
        )
        data = response.json()
        try:
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
        except KeyError:
            return None
        return (access_token, refresh_token)

    def get_username(self, user_id):
        url = "https://www.pixiv.net/users/" + str(user_id)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        username = soup.title.string.split(" - ")[0]
        return username

    def get_new_post_of_user(self, id):
        json_result = Pixiv.api.user_illusts(id)
        data = json_result.illusts
        return_data = []    # [(post_id, [image_url, image_url, ...])]
        # return max 10 posts
        for i in range(max(10, data.__len__() - 20)):
            page_count = data[i].page_count
            image_urls = []
            if page_count == 1:
                image_urls.append(data[i].image_urls.large)
            else:
                meta_pages = data[i].meta_pages
                for page in meta_pages:
                    image_urls.append(page.image_urls.large)
            return_data.append((data[i].id, image_urls))
        return return_data

    async def get_image(self, image_url, images):
        header = {"Referer": "https://app-api.pixiv.net/"}
        response = await aiorequests.get(image_url, headers=header)
        if response.status == 200:
            images.append(await response.content.read())

    def get_pixiv_update(self):
        # Refresh access token
        # retry_time = 0
        # while True:
        #     try:
        #         Pixiv.api.auth()
        #         break
        #     except:
        #         logging.error("Refresh access token failed, retyring...")
        #         sleep(3 * retry_time)
        #         retry_time += 1
        try:
            Pixiv.api.auth()
        except:
            logging.error("Refreshing access token...")
            (access_token, refresh_token) = Pixiv.refresh_token(
                self, Pixiv.api.refresh_token)
            Pixiv.api.set_auth(access_token, refresh_token)

        asyncio.set_event_loop(loop)

        user_info = db.get_all_pixiv_user_info()
        return_data = []

        for info in user_info:
            name = info[0]
            user_id = info[1]
            post_data = Pixiv.get_new_post_of_user(self, user_id)

            for post in post_data:
                one_post_return_data = []
                post_id = post[0]
                image_urls = post[1]
                post_url = "https://www.pixiv.net/artworks/" + str(post_id)

                # media_group can only contain up to 10 photos
                image_url_clips = []
                if image_urls.__len__() > 9:
                    while image_urls.__len__() > 9:
                        image_url_clips.append(image_urls[:9])
                        image_urls = image_urls[9:]
                        image_url_clips.append(image_urls)
                else:
                    image_url_clips.append(image_urls)

                if db.add_new_post(post_id, user_id):

                    for image_url_clip in image_url_clips:
                        images = []
                        tasks = []

                        for image_url in image_url_clip:
                            tasks.append(asyncio.ensure_future(
                                Pixiv.get_image(self, image_url, images)))
                        loop.run_until_complete(asyncio.wait(tasks))

                        input_medias = []
                        for image in images:

                            if image == images[0]:
                                input_medias.append(
                                    InputMediaPhoto(image, caption=post_url))
                            else:
                                input_medias.append(InputMediaPhoto(image))

                        one_post_return_data.append(input_medias)
                else:
                    break
                return_data.append(one_post_return_data)
        if not user_id:
            db.shorten_pixiv_db(user_id)
        return return_data
