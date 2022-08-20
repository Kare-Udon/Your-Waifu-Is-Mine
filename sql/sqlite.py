import sqlite3
import os


class database:
    def __init__(self):
        pass

    def init_database(self):
        if not os.path.exists('./data/accounts.db'):
            conn = sqlite3.connect('./data/accounts.db')
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS twitter_users (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL)")
            c.execute(
                "CREATE TABLE IF NOT EXISTS pixiv_users (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL)")
            conn.commit
            conn.close()
        if not os.path.exists('./data/records.db'):
            conn = sqlite3.connect('./data/records.db')
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS twitter_records (tweet_id TEXT PRIMARY KEY, user_id TEXT)")
            c.execute(
                "CREATE TABLE IF NOT EXISTS pixiv_records (post_id TEXT PRIMARY KEY, user_id TEXT)")
            conn.commit
            conn.close()

    # Twitter

    def get_all_twitter_user_info(self):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT name,id FROM twitter_users")
        return_data = c.fetchall()
        conn.commit()
        conn.close()
        return return_data

    def add_twitter_user(self, twitter_id, name):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT id FROM twitter_users WHERE id=?", (twitter_id,))
        if len(list(c)) == 0:
            c.execute(
                "INSERT INTO twitter_users (id, name) VALUES (?, ?)", (twitter_id, name))
            conn.commit()
            conn.close()
            return True
        else:
            return False

    def del_twitter_user(self, id):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT name FROM twitter_users WHERE id=?", (id,))
        db_name = c.fetchall()[0][0]
        if db_name != None:
            c.execute("DELETE FROM twitter_users WHERE id=?", (id,))
            conn.commit()
            conn.close()
            return True
        else:
            return False

    def add_new_tweet(self, tweet_id, user_id):
        conn = sqlite3.connect('./data/records.db')
        c = conn.cursor()
        command = "SELECT tweet_id FROM twitter_records WHERE tweet_id=" + \
            str(tweet_id)
        c.execute(command)
        if len(list(c)) == 0:
            command = "INSERT INTO twitter_records VALUES (" + str(
                tweet_id) + ", " + str(user_id) + ")"
            c.execute(command)
            conn.commit()
            conn.close()
            return True
        else:
            return False

    def shorten_twitter_db(self, user_id):
        conn = sqlite3.connect('./data/records.db')
        c = conn.cursor()
        command = "DELETE FROM twitter_records WHERE tweet_id IN ( SELECT tweet_id FROM ( SELECT tweet_id FROM twitter_records WHERE user_id='" + \
            user_id + "' ORDER BY tweet_id DESC LIMIT 30, 100) a);"
        c.execute(command)
        conn.commit()
        conn.close()

    # Pixiv

    def get_all_pixiv_user_info(self):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT name,id FROM pixiv_users")
        return_data = c.fetchall()
        conn.commit()
        conn.close()
        return return_data

    def add_pixiv_user(self, pixiv_id, name):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT id FROM pixiv_users WHERE id=?", (pixiv_id,))
        if len(list(c)) == 0:
            c.execute(
                "INSERT INTO pixiv_users (id, name) VALUES (?, ?)", (pixiv_id, name))
            conn.commit()
            conn.close()
            return True

        else:
            return False

    def del_pixiv_user(self, id):
        conn = sqlite3.connect('./data/accounts.db')
        c = conn.cursor()
        c.execute("SELECT name FROM pixiv_users WHERE id=?", (id,))
        db_name = c.fetchall()[0][0]
        if db_name != None:
            c.execute("DELETE FROM pixiv_users WHERE id=?", (id,))
            conn.commit()
            conn.close()
            return True
        else:
            return False

    def add_new_post(self, post_id, user_id):
        conn = sqlite3.connect('./data/records.db')
        c = conn.cursor()
        c.execute("SELECT post_id FROM pixiv_records WHERE post_id=" + str(post_id))
        if len(list(c)) == 0:
            c.execute(
                "INSERT INTO pixiv_records VALUES (" + str(post_id) + ", " + str(user_id) + ")")
            conn.commit()
            conn.close()
            return True
        else:
            return False

    def shorten_pixiv_db(self, user_id):
        conn = sqlite3.connect('./data/records.db')
        c = conn.cursor()
        command = "DELETE FROM pixiv_records WHERE post_id IN ( SELECT post_id FROM ( SELECT post_id FROM pixiv_records WHERE user_id='" + \
            user_id + "' ORDER BY post_id DESC LIMIT 30, 100) a);"
        c.execute(command)
        conn.commit()
        conn.close()
