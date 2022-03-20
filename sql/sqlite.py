from cgi import test
import sqlite3

class database: 
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()
    
    # type: 0-twitter 1-pixiv
    def add_user(self, type, id, name):
        if type == 0:
            self.c.execute("INSERT INTO twitter_users (id, name) VALUES (?, ?)", (id, name))
        elif type == 1:
            self.c.execute("INSERT INTO pixiv_users (id, name) VALUES (?, ?)", (id, name))
        self.conn.commit()
        self.conn.close()
        
    def del_user(self, type, id):
        if type == 0:
            self.c.execute("DELETE FROM twitter_users WHERE id=?", (id,))
        elif type == 1:
            self.c.execute("DELETE FROM pixiv_users WHERE id=?", (id,))
        self.conn.commit()
        self.conn.close()