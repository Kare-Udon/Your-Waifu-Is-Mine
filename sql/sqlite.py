from distutils.util import execute
import sqlite3

class database: 
    def __init__(self):
        pass
        
    def get_all_twitter_user_id(self):
        self.conn = sqlite3.connect('accounts.db')
        self.c = self.conn.cursor()
        self.c.execute("SELECT id FROM twitter_users")
        return_data = self.c.fetchall()
        self.conn.commit()
        self.conn.close()
        return return_data  # [(id,), (id,), ...]
    
    def add_twitter_user(self,twitter_id, name):
        self.conn = sqlite3.connect('accounts.db')
        self.c = self.conn.cursor()
        self.c.execute("SELECT id FROM twitter_users WHERE id=?", (twitter_id,))
        if len(list(self.c)) == 0:
            self.c.execute("INSERT INTO twitter_users (id, name) VALUES (?, ?)", (twitter_id, name))
            self.conn.commit()
            self.conn.close()
            self.add_new_twitter_user_database(name)
        else:
            return False
        
    def add_pixiv_user(self, pixiv_id, name):
        self.conn = sqlite3.connect('accounts.db')
        self.c = self.conn.cursor()
        self.c.execute("SELECT id FROM pixiv_users WHERE id=?", (pixiv_id,))
        if len(list(self.c)) == 0:
            self.c.execute("INSERT INTO pixiv_users (id, name) VALUES (?, ?)", (pixiv_id, name))
        else:
            return False
        self.conn.commit()
        self.conn.close()
        
    def del_user(self, type, id):
        self.conn = sqlite3.connect('accounts.db')
        self.c = self.conn.cursor()
        if type == 0:
            self.c.execute("SELECT id FROM twitter_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("DELETE FROM twitter_users WHERE id=?", (id,))
            else:
                return False
        elif type == 1:
            self.c.execute("SELECT id FROM pixiv_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("DELETE FROM pixiv_users WHERE id=?", (id,))
            else:
                return False
        self.conn.commit()
        self.conn.close()
    
    def add_new_twitter_user_database(self, database_name):
        self.conn = sqlite3.connect('accounts.db')
        self.c = self.conn.cursor()
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        command = "CREATE TABLE IF NOT EXISTS " + database_name + " (tweet_id INTEGER PRIMARY KEY)"
        c.execute(command)
        conn.commit()
        conn.close()