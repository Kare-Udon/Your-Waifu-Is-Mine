import sqlite3

class database: 
    def __init__(self):
        pass
        
    def get_all_twitter_user_info(self):
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT name,id FROM twitter_users")
        return_data = c.fetchall()
        conn.commit()
        conn.close()
        return return_data
    
    def add_twitter_user(self, twitter_id, name):
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT id FROM twitter_users WHERE id=?", (twitter_id,))
        if len(list(c)) == 0:
            c.execute("INSERT INTO twitter_users (id, name) VALUES (?, ?)", (twitter_id, name))
            conn.commit()
            conn.close()
            self.add_new_twitter_user_database(name)
            return True
        else:
            return False
        
    def add_pixiv_user(self, pixiv_id, name):
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT id FROM pixiv_users WHERE id=?", (pixiv_id,))
        if len(list(c)) == 0:
            c.execute("INSERT INTO pixiv_users (id, name) VALUES (?, ?)", (pixiv_id, name))
        else:
            return False
        conn.commit()
        conn.close()
        
    def del_twitter_user(self, id):
        conn = sqlite3.connect('accounts.db')
        c = conn.cursor()
        c.execute("SELECT name FROM twitter_users WHERE id=?", (id,))
        db_name = c.fetchall()[0][0]
        if db_name != None:
            c.execute("DELETE FROM twitter_users WHERE id=?", (id,))
            conn.commit()
            conn.close()
            self.del_twitter_user_database(db_name)
            return True
        else:
            return False
        
    def del_pixiv_user(id):
        pass
    
    def add_new_twitter_user_database(self, database_name):
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        command = "CREATE TABLE IF NOT EXISTS " + database_name + " (tweet_id TEXT PRIMARY KEY)"
        c.execute(command)
        conn.commit()
        conn.close()
        
    def del_twitter_user_database(self, database_name):
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        command = "DROP TABLE IF EXISTS " + database_name
        c.execute(command)
        conn.commit()
        conn.close()
        
    def add_new_tweet(self, database_name, tweet_id):
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        command = "SELECT tweet_id FROM " + database_name + " WHERE tweet_id=" + str(tweet_id)
        c.execute(command)
        if len(list(c)) == 0:
            command = "INSERT INTO " + database_name + " VALUES (" + str(tweet_id) + ")"
            c.execute(command)
            conn.commit()
            conn.close()
            return True
        else:
            return False
        
    def shorten_db(self, database_name):
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        command = "DELETE FROM " + database_name + " WHERE tweet_id IN ( SELECT tweet_id FROM ( SELECT tweet_id FROM " + database_name + " ORDER BY tweet_id DESC LIMIT 30, 100) a);"
        c.execute(command)
        conn.commit()
        conn.close()